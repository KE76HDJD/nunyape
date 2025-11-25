from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum
import httpx

app = FastAPI(title="Payment Router - Nunyape")

# Configuration des adapters
ADAPTERS = {
    "stripe": "http://adapter-stripe:8020",
    "paypal": "http://adapter-paypal:8021",
    "mtn_money": "http://adapter-mtn:8022",
    "orange_money": "http://adapter-orange:8023",
    "flooz": "http://adapter-flooz:8024",
    "mixx": "http://adapter-mixx:8025",
    "umb": "http://adapter-umb:8026"
}

# Modèles
class RouteRequest(BaseModel):
    payment_id: str
    payment_method: str
    amount: float
    currency: str
    user_email: str
    user_phone: Optional[str] = None
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class RouteResponse(BaseModel):
    payment_id: str
    status: str
    gateway: str
    redirect_url: Optional[str] = None
    qr_code_url: Optional[str] = None
    message: Optional[str] = None
    transaction_ref: Optional[str] = None
    expires_at: Optional[str] = None

# Routes
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "payment-router"}

@app.post("/route", response_model=RouteResponse)
async def route_payment(request: RouteRequest):
    """Route le paiement vers l'adapter approprié"""
    
    # Vérifier que l'adapter existe
    if request.payment_method not in ADAPTERS:
        raise HTTPException(
            status_code=400,
            detail=f"Payment method {request.payment_method} not supported"
        )
    
    adapter_url = ADAPTERS[request.payment_method]
    
    # Préparer le payload pour l'adapter
    adapter_payload = {
        "payment_id": request.payment_id,
        "amount": request.amount,
        "currency": request.currency,
        "user_email": request.user_email,
        "user_phone": request.user_phone,
        "return_url": request.return_url,
        "cancel_url": request.cancel_url,
        "metadata": request.metadata
    }
    
    # Appeler l'adapter
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{adapter_url}/process",
                json=adapter_payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Adapter {request.payment_method} failed"
                )
            
            result = response.json()
            
            return RouteResponse(
                payment_id=request.payment_id,
                status=result.get("status", "pending"),
                gateway=request.payment_method,
                redirect_url=result.get("redirect_url"),
                qr_code_url=result.get("qr_code_url"),
                message=result.get("message"),
                transaction_ref=result.get("transaction_ref"),
                expires_at=result.get("expires_at")
            )
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Payment adapter {request.payment_method} unavailable: {str(e)}"
        )

@app.get("/adapters")
def list_adapters():
    """Liste tous les adapters de paiement disponibles"""
    return {
        "adapters": list(ADAPTERS.keys()),
        "total": len(ADAPTERS)
    }

@app.get("/adapters/{payment_method}/health")
async def check_adapter_health(payment_method: str):
    """Vérifie la santé d'un adapter spécifique"""
    
    if payment_method not in ADAPTERS:
        raise HTTPException(status_code=404, detail="Adapter not found")
    
    adapter_url = ADAPTERS[payment_method]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{adapter_url}/health", timeout=5.0)
            return {
                "adapter": payment_method,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response": response.json() if response.status_code == 200 else None
            }
    except httpx.RequestError:
        return {
            "adapter": payment_method,
            "status": "unavailable"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)