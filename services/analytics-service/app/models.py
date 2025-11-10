from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class Transaction:
    """
    Modèle de données pour une transaction
    """
    id: str
    amount: float
    currency: str
    status: str  # success, failed, pending
    timestamp: str
    payment_method: str
    customer_id: Optional[str] = None
    reference: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return asdict(self)

@dataclass
class DailyStats:
    """
    Statistiques quotidiennes agrégées
    """
    date: str
    total_amount: float
    transaction_count: int
    successful_count: int
    failed_count: int
    average_amount: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return asdict(self)

@dataclass
class PaymentMethodStats:
    """
    Statistiques par méthode de paiement
    """
    payment_method: str
    total_amount: float
    transaction_count: int
    success_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return asdict(self)

@dataclass
class RevenueMetrics:
    """
    Métriques de revenu
    """
    total_revenue: float
    monthly_revenue: float
    average_transaction_value: float
    total_transactions: int
    successful_transactions: int
    success_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return asdict(self)

@dataclass
class HealthStatus:
    """
    Statut de santé d'un service
    """
    service: str
    status: str  # healthy, unhealthy, unreachable
    response_time: Optional[float] = None
    last_checked: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return asdict(self)

@dataclass
class AnalyticsReport:
    """
    Rapport analytique complet
    """
    period: str
    generated_at: str
    revenue_metrics: RevenueMetrics
    daily_stats: List[DailyStats]
    payment_method_stats: List[PaymentMethodStats]
    health_status: Dict[str, HealthStatus]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire"""
        return {
            'period': self.period,
            'generated_at': self.generated_at,
            'revenue_metrics': self.revenue_metrics.to_dict(),
            'daily_stats': [stats.to_dict() for stats in self.daily_stats],
            'payment_method_stats': [stats.to_dict() for stats in self.payment_method_stats],
            'health_status': {k: v.to_dict() for k, v in self.health_status.items()}
        }