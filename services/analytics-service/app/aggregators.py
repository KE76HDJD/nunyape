import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AnalyticsAggregator:
    """
    Agrégateur de données analytiques
    Consolide et agrège les données de différentes sources
    """
    
    def __init__(self):
        """Initialise l'agrégateur avec des structures de données vides"""
        self.transaction_data = []
        self.user_activity = []
    
    def aggregate_daily_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Agrège les transactions par jour
        
        Args:
            transactions: Liste des transactions à agréger
            
        Returns:
            Statistiques quotidiennes agrégées
        """
        try:
            daily_stats = {}
            
            for transaction in transactions:
                # Extraction de la date (sans l'heure)
                transaction_date = transaction['timestamp'].split('T')[0]
                
                if transaction_date not in daily_stats:
                    daily_stats[transaction_date] = {
                        'total_amount': 0,
                        'transaction_count': 0,
                        'successful_count': 0,
                        'failed_count': 0,
                        'average_amount': 0
                    }
                
                # Mise à jour des statistiques
                stats = daily_stats[transaction_date]
                stats['total_amount'] += transaction['amount']
                stats['transaction_count'] += 1
                
                if transaction['status'] == 'success':
                    stats['successful_count'] += 1
                else:
                    stats['failed_count'] += 1
            
            # Calcul des moyennes
            for date_stats in daily_stats.values():
                if date_stats['transaction_count'] > 0:
                    date_stats['average_amount'] = (
                        date_stats['total_amount'] / date_stats['transaction_count']
                    )
            
            logger.info(f"Statistiques quotidiennes agrégées pour {len(daily_stats)} jours")
            return daily_stats
            
        except Exception as e:
            logger.error(f"Erreur agrégation transactions quotidiennes: {e}")
            raise
    
    def aggregate_by_payment_method(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Agrège les transactions par méthode de paiement
        
        Args:
            transactions: Liste des transactions
            
        Returns:
            Statistiques par méthode de paiement
        """
        try:
            method_stats = {}
            
            for transaction in transactions:
                payment_method = transaction.get('payment_method', 'unknown')
                
                if payment_method not in method_stats:
                    method_stats[payment_method] = {
                        'total_amount': 0,
                        'transaction_count': 0,
                        'success_rate': 0
                    }
                
                stats = method_stats[payment_method]
                stats['total_amount'] += transaction['amount']
                stats['transaction_count'] += 1
            
            # Calcul des taux de succès
            for method, stats in method_stats.items():
                successful_transactions = len([
                    t for t in transactions 
                    if t.get('payment_method') == method and t['status'] == 'success'
                ])
                
                if stats['transaction_count'] > 0:
                    stats['success_rate'] = (
                        successful_transactions / stats['transaction_count'] * 100
                    )
            
            logger.info(f"Statistiques agrégées pour {len(method_stats)} méthodes de paiement")
            return method_stats
            
        except Exception as e:
            logger.error(f"Erreur agrégation par méthode de paiement: {e}")
            raise
    
    def calculate_revenue_metrics(self, transactions: List[Dict]) -> Dict[str, Any]:
        """
        Calcule les métriques de revenu
        
        Args:
            transactions: Liste des transactions
            
        Returns:
            Métriques de revenu calculées
        """
        try:
            successful_transactions = [
                t for t in transactions if t['status'] == 'success'
            ]
            
            total_revenue = sum(t['amount'] for t in successful_transactions)
            avg_transaction_value = (
                total_revenue / len(successful_transactions) 
                if successful_transactions else 0
            )
            
            # Transactions des 30 derniers jours
            recent_transactions = [
                t for t in successful_transactions
                if self._is_recent(t['timestamp'], days=30)
            ]
            
            monthly_revenue = sum(t['amount'] for t in recent_transactions)
            
            metrics = {
                'total_revenue': total_revenue,
                'monthly_revenue': monthly_revenue,
                'average_transaction_value': avg_transaction_value,
                'total_transactions': len(transactions),
                'successful_transactions': len(successful_transactions),
                'success_rate': (
                    len(successful_transactions) / len(transactions) * 100 
                    if transactions else 0
                )
            }
            
            logger.info("Métriques de revenu calculées avec succès")
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur calcul métriques revenu: {e}")
            raise
    
    def _is_recent(self, timestamp: str, days: int = 30) -> bool:
        """
        Vérifie si un timestamp est récent
        
        Args:
            timestamp: Timestamp à vérifier
            days: Nombre de jours pour définir "récent"
            
        Returns:
            True si récent, False sinon
        """
        try:
            transaction_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return transaction_date >= cutoff_date
        except Exception:
            return False