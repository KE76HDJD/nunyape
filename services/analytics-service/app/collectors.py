import logging
import requests
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Collecteur de données depuis différentes sources
    Récupère les données des adaptateurs de paiement
    """
    
    def __init__(self, adapter_urls: Dict[str, str]):
        """
        Initialise le collecteur avec les URLs des adaptateurs
        
        Args:
            adapter_urls: Dictionnaire des URLs des adaptateurs
        """
        self.adapter_urls = adapter_urls
        self.session = requests.Session()
    
    def collect_transaction_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Collecte les données de transaction de tous les adaptateurs
        
        Args:
            days: Nombre de jours de données à collecter
            
        Returns:
            Liste consolidée des transactions
        """
        all_transactions = []
        
        for adapter_name, base_url in self.adapter_urls.items():
            try:
                # Récupération des transactions de l'adaptateur
                transactions = self._get_adapter_transactions(adapter_name, base_url, days)
                all_transactions.extend(transactions)
                
                logger.info(f"Collecté {len(transactions)} transactions de {adapter_name}")
                
            except Exception as e:
                logger.error(f"Erreur collecte données {adapter_name}: {e}")
                continue
        
        # Tri par timestamp
        all_transactions.sort(key=lambda x: x['timestamp'])
        
        logger.info(f"Total transactions collectées: {len(all_transactions)}")
        return all_transactions
    
    def collect_health_status(self) -> Dict[str, Any]:
        """
        Collecte le statut de santé de tous les adaptateurs
        
        Returns:
            Statut de santé consolidé
        """
        health_status = {}
        
        for adapter_name, base_url in self.adapter_urls.items():
            try:
                response = self.session.get(f"{base_url}/health", timeout=10)
                health_status[adapter_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time': response.elapsed.total_seconds(),
                    'last_checked': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                health_status[adapter_name] = {
                    'status': 'unreachable',
                    'error': str(e),
                    'last_checked': datetime.utcnow().isoformat()
                }
                logger.warning(f"Adaptateur {adapter_name} inaccessible: {e}")
        
        return health_status
    
    def _get_adapter_transactions(self, adapter_name: str, base_url: str, days: int) -> List[Dict]:
        """
        Récupère les transactions d'un adaptateur spécifique
        
        Args:
            adapter_name: Nom de l'adaptateur
            base_url: URL de base de l'adaptateur
            days: Nombre de jours de données
            
        Returns:
            Liste des transactions de l'adaptateur
        """
        try:
            # Endpoint fictif - à adapter selon l'implémentation réelle
            response = self.session.get(
                f"{base_url}/transactions",
                params={'days': days},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                # Normalisation des données
                return self._normalize_transaction_data(data.get('transactions', []), adapter_name)
            else:
                logger.warning(f"Statut {response.status_code} pour {adapter_name}")
                return []
                
        except Exception as e:
            logger.error(f"Erreur récupération transactions {adapter_name}: {e}")
            return []
    
    def _normalize_transaction_data(self, transactions: List[Dict], adapter_name: str) -> List[Dict]:
        """
        Normalise les données de transaction dans un format standard
        
        Args:
            transactions: Transactions à normaliser
            adapter_name: Nom de l'adaptateur source
            
        Returns:
            Transactions normalisées
        """
        normalized = []
        
        for transaction in transactions:
            normalized_transaction = {
                'id': transaction.get('id', ''),
                'amount': float(transaction.get('amount', 0)),
                'currency': transaction.get('currency', 'USD'),
                'status': transaction.get('status', 'unknown'),
                'timestamp': transaction.get('timestamp', datetime.utcnow().isoformat()),
                'payment_method': adapter_name,
                'customer_id': transaction.get('customer_id', ''),
                'reference': transaction.get('reference', '')
            }
            normalized.append(normalized_transaction)
        
        return normalized