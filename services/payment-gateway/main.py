from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid
import httpx
import time
from datetime import datetime, timezonels
import logging
from contextlib import asynccontextmanager

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base de données en mémoire
payments_db = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Payment Gateway starting up...")
    yield
    # Shutdown
    logger.info("Payment Gateway shutting down...")
    payments_db.clear()

app = FastAPI(
    title="Payment Gateway - Nunyape",
    description="API Gateway central pour le traitement des paiements",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration des services
ROUTER_SERVICE_URL = "http://payment-router:8013"
BILLING_SERVICE_URL = "http://billing-service:8011"

# Timeouts configuration
REQUEST_TIMEOUT = 30.0
HEALTH_CHECK_TIMEOUT = 5.0

# Enums
class PaymentMethod(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    MTN_MONEY = "mtn_money"
    ORANGE_MONEY = "orange_money"
    FLOOZ = "flooz"
    MIXX = "mixx"
    UMB = "umb"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

# Modèles
class PaymentRequest(BaseModel):
    invoice_id: str = Field(..., description="ID de la facture à payer")
    payment_method: PaymentMethod = Field(..., description="Méthode de paiement")
    amount: float = Field(..., gt=0, description="Montant à payer (doit être positif)")
    currency: str = Field(default="XOF", description="Devise du paiement")
    user_id: str = Field(..., description="ID de l'utilisateur")
    user_email: str = Field(..., description="Email de l'utilisateur")
    user_phone: Optional[str] = Field(None, description="Téléphone de l'utilisateur")
    return_url: Optional[str] = Field(None, description="URL de retour après paiement")
    cancel_url: Optional[str] = Field(None, description="URL d'annulation")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Métadonnées supplémentaires")

class PaymentResponse(BaseModel):
    payment_id: str = Field(..., description="ID unique du paiement")
    status: PaymentStatus = Field(..., description="Statut du paiement")
    gateway: str = Field(..., description="Gateway de paiement utilisée")
    redirect_url: Optional[str] = Field(None, description="URL de redirection pour le paiement")
    qr_code_url: Optional[str] = Field(None, description="URL du QR code pour paiement mobile")
    message: Optional[str] = Field(None, description="Message d'information")
    transaction_ref: Optional[str] = Field(None, description="Référence de transaction")
    expires_at: Optional[str] = Field(None, description="Date d'expiration du paiement")

class PaymentStatusResponse(BaseModel):
    payment_id: str = Field(..., description="ID du paiement")
    status: PaymentStatus = Field(..., description="Statut actuel")
    amount: float = Field(..., description="Montant du paiement")
    currency: str = Field(..., description="Devise")
    payment_method: str = Field(..., description="Méthode de paiement")
    created_at: str = Field(..., description="Date de création")
    updated_at: str = Field(..., description="Date de dernière mise à jour")
    completed_at: Optional[str] = Field(None, description="Date de complétion")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées")
    invoice_id: str = Field(..., description="ID de la facture associée")

class PaymentListResponse(BaseModel):
    payments: List[PaymentStatusResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class StatisticsResponse(BaseModel):
    total_payments: int
    completed: int
    pending: int
    failed: int
    cancelled: int
    total_amount: float
    success_rate: float
    average_amount: float

# Services
class BillingService:
    @staticmethod
    async def validate_invoice(invoice_id: str, amount: float) -> Dict[str, Any]:
        """Valide une facture auprès du service de billing"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BILLING_SERVICE_URL}/invoices/{invoice_id}",
                    timeout=HEALTH_CHECK_TIMEOUT
                )
                
                if response.status_code == 404:
                    raise HTTPException(status_code=404, detail="Facture non trouvée")
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=503, 
                        detail="Service de facturation indisponible"
                    )
                
                invoice = response.json()
                
                # Validation de la facture
                if invoice.get("status") == "paid":
                    raise HTTPException(status_code=400, detail="Facture déjà payée")
                
                if abs(invoice.get("total_amount", 0) - amount) > 0.01:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Montant incorrect. Attendu: {invoice.get('total_amount')}, Reçu: {amount}"
                    )
                
                return invoice
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Timeout du service de facturation")
        except httpx.RequestError as e:
            logger.error(f"Erreur de connexion au service de facturation: {e}")
            raise HTTPException(status_code=503, detail="Service de facturation indisponible")

class PaymentRouterService:
    @staticmethod
    async def route_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route le paiement vers le service approprié"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{ROUTER_SERVICE_URL}/route",
                    json=payment_data,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code != 200:
                    logger.error(f"Router error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Échec du traitement du paiement"
                    )
                
                return response.json()
                
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Timeout du routeur de paiement")
        except httpx.RequestError as e:
            logger.error(f"Erreur de connexion au routeur: {e}")
            raise HTTPException(status_code=503, detail="Routeur de paiement indisponible")

# Utilitaires
def get_current_timestamp() -> str:
    """Retourne le timestamp actuel en format ISO"""
    return datetime.now(timezone.utc).isoformat()

def generate_payment_id() -> str:
    """Génère un ID de paiement unique"""
    return f"pay_{uuid.uuid4().hex[:16]}"

# Routes
@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Payment Gateway API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": get_current_timestamp()
    }

@app.get("/health")
async def health_check():
    """Health check du service"""
    services_status = {
        "payment_gateway": "healthy",
        "billing_service": "unknown",
        "payment_router": "unknown"
    }
    
    # Vérifier le service de facturation
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BILLING_SERVICE_URL}/health", timeout=HEALTH_CHECK_TIMEOUT)
            services_status["billing_service"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services_status["billing_service"] = "unavailable"
    
    # Vérifier le routeur de paiement
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ROUTER_SERVICE_URL}/health", timeout=HEALTH_CHECK_TIMEOUT)
            services_status["payment_router"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services_status["payment_router"] = "unavailable"
    
    return {
        "status": "ok",
        "service": "payment-gateway",
        "timestamp": get_current_timestamp(),
        "services": services_status,
        "database_entries": len(payments_db)
    }

@app.post("/pay", response_model=PaymentResponse)
async def process_payment(payment_request: PaymentRequest):
    """Point d'entrée principal pour initier un paiement"""
    
    # Générer un ID de paiement unique
    payment_id = generate_payment_id()
    logger.info(f"Processing payment {payment_id} for invoice {payment_request.invoice_id}")
    
    # Valider la facture
    invoice = await BillingService.validate_invoice(
        payment_request.invoice_id, 
        payment_request.amount
    )
    
    # Préparer la requête pour le router
    router_payload = {
        "payment_id": payment_id,
        "payment_method": payment_request.payment_method.value,
        "amount": payment_request.amount,
        "currency": payment_request.currency,
        "user_email": payment_request.user_email,
        "user_phone": payment_request.user_phone,
        "return_url": payment_request.return_url,
        "cancel_url": payment_request.cancel_url,
        "metadata": {
            **payment_request.metadata,
            "invoice_id": payment_request.invoice_id,
            "user_id": payment_request.user_id,
            "invoice_data": invoice
        }
    }
    
    # Envoyer au router pour traitement
    router_result = await PaymentRouterService.route_payment(router_payload)
    
    # Enregistrer le paiement
    current_time = get_current_timestamp()
    payments_db[payment_id] = {
        "payment_id": payment_id,
        "invoice_id": payment_request.invoice_id,
        "user_id": payment_request.user_id,
        "amount": payment_request.amount,
        "currency": payment_request.currency,
        "payment_method": payment_request.payment_method.value,
        "status": PaymentStatus.PENDING,
        "gateway_response": router_result,
        "created_at": current_time,
        "updated_at": current_time,
        "metadata": router_payload["metadata"]
    }
    
    logger.info(f"Payment {payment_id} created successfully")
    
    return PaymentResponse(
        payment_id=payment_id,
        status=PaymentStatus(router_result.get("status", "pending")),
        gateway=router_result.get("gateway", ""),
        redirect_url=router_result.get("redirect_url"),
        qr_code_url=router_result.get("qr_code_url"),
        message=router_result.get("message"),
        transaction_ref=router_result.get("transaction_ref"),
        expires_at=router_result.get("expires_at")
    )

@app.get("/payments/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(payment_id: str):
    """Vérifie le statut d'un paiement"""
    
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    payment = payments_db[payment_id]
    
    return PaymentStatusResponse(
        payment_id=payment["payment_id"],
        status=payment["status"],
        amount=payment["amount"],
        currency=payment["currency"],
        payment_method=payment["payment_method"],
        created_at=payment["created_at"],
        updated_at=payment["updated_at"],
        completed_at=payment.get("completed_at"),
        metadata=payment.get("metadata", {}),
        invoice_id=payment["invoice_id"]
    )

@app.post("/payments/{payment_id}/cancel")
async def cancel_payment(payment_id: str):
    """Annule un paiement en attente"""
    
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    payment = payments_db[payment_id]
    
    if payment["status"] not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
        raise HTTPException(
            status_code=400,
            detail="Impossible d'annuler un paiement déjà complété ou échoué"
        )
    
    payment["status"] = PaymentStatus.CANCELLED
    payment["updated_at"] = get_current_timestamp()
    
    logger.info(f"Payment {payment_id} cancelled")
    
    return {
        "message": "Paiement annulé avec succès",
        "payment_id": payment_id,
        "status": PaymentStatus.CANCELLED
    }

@app.post("/payments/{payment_id}/webhook")
async def payment_webhook(payment_id: str, payload: Dict[str, Any]):
    """Webhook pour recevoir les mises à jour de statut des gateways"""
    
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    payment = payments_db[payment_id]
    new_status = payload.get("status")
    
    if new_status in [s.value for s in PaymentStatus]:
        payment["status"] = PaymentStatus(new_status)
        payment["updated_at"] = get_current_timestamp()
        
        if new_status == PaymentStatus.COMPLETED:
            payment["completed_at"] = get_current_timestamp()
        
        logger.info(f"Payment {payment_id} status updated to {new_status}")
        
        return {"message": "Statut mis à jour avec succès", "payment_id": payment_id}
    else:
        raise HTTPException(status_code=400, detail="Statut invalide")

@app.get("/payments", response_model=PaymentListResponse)
async def list_payments(
    user_id: Optional[str] = None,
    status: Optional[PaymentStatus] = None,
    page: int = 1,
    page_size: int = 20
):
    """Liste tous les paiements avec filtres optionnels"""
    
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    
    payments = list(payments_db.values())
    
    # Appliquer les filtres
    if user_id:
        payments = [p for p in payments if p["user_id"] == user_id]
    
    if status:
        payments = [p for p in payments if p["status"] == status]
    
    # Pagination
    total = len(payments)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_payments = payments[start_idx:end_idx]
    
    return PaymentListResponse(
        payments=[
            PaymentStatusResponse(
                payment_id=p["payment_id"],
                status=p["status"],
                amount=p["amount"],
                currency=p["currency"],
                payment_method=p["payment_method"],
                created_at=p["created_at"],
                updated_at=p["updated_at"],
                completed_at=p.get("completed_at"),
                metadata=p.get("metadata", {}),
                invoice_id=p["invoice_id"]
            ) for p in paginated_payments
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@app.get("/statistics", response_model=StatisticsResponse)
async def get_payment_statistics():
    """Statistiques des paiements"""
    
    payments = list(payments_db.values())
    total_payments = len(payments)
    
    if total_payments == 0:
        return StatisticsResponse(
            total_payments=0,
            completed=0,
            pending=0,
            failed=0,
            cancelled=0,
            total_amount=0,
            success_rate=0,
            average_amount=0
        )
    
    completed = len([p for p in payments if p["status"] == PaymentStatus.COMPLETED])
    pending = len([p for p in payments if p["status"] == PaymentStatus.PENDING])
    failed = len([p for p in payments if p["status"] == PaymentStatus.FAILED])
    cancelled = len([p for p in payments if p["status"] == PaymentStatus.CANCELLED])
    
    total_amount = sum(p["amount"] for p in payments if p["status"] == PaymentStatus.COMPLETED)
    average_amount = total_amount / completed if completed > 0 else 0
    
    return StatisticsResponse(
        total_payments=total_payments,
        completed=completed,
        pending=pending,
        failed=failed,
        cancelled=cancelled,
        total_amount=total_amount,
        success_rate=round((completed / total_payments) * 100, 2),
        average_amount=round(average_amount, 2)
    )

@app.get("/methods")
async def get_available_payment_methods():
    """Liste les méthodes de paiement disponibles"""
    return {
        "available_methods": [method.value for method in PaymentMethod],
        "default_currency": "XOF",
        "supported_currencies": ["XOF", "EUR", "USD"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8012,
        log_level="info"
    )