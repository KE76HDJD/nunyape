from flask import Blueprint, request, jsonify
from aggregators import AnalyticsAggregator
from collectors import DataCollector
from models import AnalyticsReport
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration des URLs des adaptateurs
ADAPTER_URLS = {
    'paypal': os.getenv('PAYPAL_ADAPTER_URL', 'http://adapter-paypal:8080/api/v1/paypal'),
    'stripe': os.getenv('STRIPE_ADAPTER_URL', 'http://adapter-stripe:8080/api/v1/stripe'),
    'umb': os.getenv('UMB_ADAPTER_URL', 'http://adapter-umb:8080/api/v1/umb'),
    'orange': os.getenv('ORANGE_ADAPTER_URL', 'http://adapter-orange:8080/api/v1/orange')
}

# Initialisation des composants
data_collector = DataCollector(ADAPTER_URLS)
analytics_aggregator = AnalyticsAggregator()

# Création du blueprint
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé du service analytique"""
    return jsonify({
        'status': 'healthy', 
        'service': 'analytics-service',
        'timestamp': datetime.utcnow().isoformat()
    })

@analytics_bp.route('/report', methods=['GET'])
def generate_report():
    """
    Génère un rapport analytique complet
    
    Query Parameters:
        days: Période en jours pour le rapport (défaut: 7)
    """
    try:
        days = int(request.args.get('days', 7))
        
        # Collecte des données
        transactions = data_collector.collect_transaction_data(days)
        health_status = data_collector.collect_health_status()
        
        # Agrégation des données
        daily_stats = analytics_aggregator.aggregate_daily_transactions(transactions)
        payment_method_stats = analytics_aggregator.aggregate_by_payment_method(transactions)
        revenue_metrics = analytics_aggregator.calculate_revenue_metrics(transactions)
        
        # Conversion des statistiques quotidiennes en objets DailyStats
        daily_stats_objects = []
        for date, stats in daily_stats.items():
            daily_stats_objects.append(
                DailyStats(
                    date=date,
                    total_amount=stats['total_amount'],
                    transaction_count=stats['transaction_count'],
                    successful_count=stats['successful_count'],
                    failed_count=stats['failed_count'],
                    average_amount=stats['average_amount']
                )
            )
        
        # Conversion des statistiques par méthode de paiement
        payment_method_objects = []
        for method, stats in payment_method_stats.items():
            payment_method_objects.append(
                PaymentMethodStats(
                    payment_method=method,
                    total_amount=stats['total_amount'],
                    transaction_count=stats['transaction_count'],
                    success_rate=stats['success_rate']
                )
            )
        
        # Conversion du statut de santé
        health_status_objects = {}
        for service, status in health_status.items():
            health_status_objects[service] = HealthStatus(
                service=service,
                status=status['status'],
                response_time=status.get('response_time'),
                last_checked=status.get('last_checked'),
                error=status.get('error')
            )
        
        # Création du rapport
        report = AnalyticsReport(
            period=f"{days} days",
            generated_at=datetime.utcnow().isoformat(),
            revenue_metrics=RevenueMetrics(**revenue_metrics),
            daily_stats=daily_stats_objects,
            payment_method_stats=payment_method_objects,
            health_status=health_status_objects
        )
        
        return jsonify({
            'success': True,
            'report': report.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erreur génération rapport: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@analytics_bp.route('/metrics/revenue', methods=['GET'])
def get_revenue_metrics():
    """Retourne uniquement les métriques de revenu"""
    try:
        days = int(request.args.get('days', 30))
        
        transactions = data_collector.collect_transaction_data(days)
        revenue_metrics = analytics_aggregator.calculate_revenue_metrics(transactions)
        
        return jsonify({
            'success': True,
            'period_days': days,
            'metrics': revenue_metrics
        })
        
    except Exception as e:
        logger.error(f"Erreur métriques revenu: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/health/status', methods=['GET'])
def get_health_status():
    """Retourne le statut de santé de tous les adaptateurs"""
    try:
        health_status = data_collector.collect_health_status()
        
        return jsonify({
            'success': True,
            'health_status': health_status
        })
        
    except Exception as e:
        logger.error(f"Erreur statut santé: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/transactions/summary', methods=['GET'])
def get_transactions_summary():
    """Retourne un résumé des transactions"""
    try:
        days = int(request.args.get('days', 7))
        
        transactions = data_collector.collect_transaction_data(days)
        payment_method_stats = analytics_aggregator.aggregate_by_payment_method(transactions)
        
        return jsonify({
            'success': True,
            'period_days': days,
            'total_transactions': len(transactions),
            'payment_methods': payment_method_stats
        })
        
    except Exception as e:
        logger.error(f"Erreur résumé transactions: {e}")
        return jsonify({'error': str(e)}), 500