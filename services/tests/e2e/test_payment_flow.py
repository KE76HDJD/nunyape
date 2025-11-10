import pytest
import asyncio
import aiohttp
import json
import random
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

class TestPaymentFlowLoad:
    """Load testing for payment flow scenarios"""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8080"
    
    @pytest.fixture
    async def auth_token(self):
        """Get auth token for API requests"""
        async with aiohttp.ClientSession() as session:
            login_data = {
                "email": "load_test@company.com", 
                "password": "LoadTestPass123!"
            }
            async with session.post(
                "http://localhost:8000/api/v1/token",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["access_token"]
                else:
                    pytest.fail("Failed to get auth token")
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_concurrent_payment_creation(self, base_url, auth_token):
        """Test creating multiple payments concurrently"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def create_payment(payment_id):
            payment_data = {
                "amount": round(random.uniform(10, 1000), 2),
                "currency": "USD",
                "payment_method": random.choice(["credit_card", "paypal", "bank_transfer"]),
                "customer_id": f"load_customer_{payment_id}",
                "order_id": f"order_concurrent_{payment_id}_{datetime.utcnow().timestamp()}",
                "description": f"Concurrent load test payment {payment_id}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/payments",
                    json=payment_data,
                    headers=headers
                ) as response:
                    return response.status, await response.text()
        
        # Create 50 payments concurrently
        tasks = [create_payment(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        failure_count = len(results) - success_count
        
        print(f"Concurrent payment creation: {success_count} successes, {failure_count} failures")
        
        assert success_count >= 45, f"Too many failures: {failure_count} out of {len(results)}"
        assert failure_count <= 5, f"Excessive failures: {failure_count}"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_payment_status_checks_under_load(self, base_url, auth_token):
        """Test checking payment status under load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create some payments
        payment_ids = []
        for i in range(20):
            payment_data = {
                "amount": 100.00,
                "currency": "USD", 
                "payment_method": "credit_card",
                "customer_id": f"status_check_customer_{i}",
                "order_id": f"order_status_{i}_{datetime.utcnow().timestamp()}",
                "description": "Payment for status check load test"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/payments",
                    json=payment_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        payment_ids.append(data["id"])
        
        # Now check status for all payments concurrently
        async def check_payment_status(payment_id):
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{base_url}/api/v1/payments/{payment_id}",
                    headers=headers
                ) as response:
                    return response.status, payment_id
        
        tasks = [check_payment_status(pid) for pid in payment_ids]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        
        print(f"Payment status checks: {success_count}/{len(payment_ids)} successful")
        
        assert success_count == len(payment_ids), "Some payment status checks failed"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_mixed_payment_workload(self, base_url, auth_token):
        """Test mixed workload of payment operations"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def mixed_operation(operation_id):
            async with aiohttp.ClientSession() as session:
                # 70% create payment, 30% check status
                if random.random() < 0.7:
                    # Create payment
                    payment_data = {
                        "amount": round(random.uniform(1, 500), 2),
                        "currency": random.choice(["USD", "EUR", "GBP"]),
                        "payment_method": random.choice(["credit_card", "paypal"]),
                        "customer_id": f"mixed_customer_{operation_id}",
                        "order_id": f"order_mixed_{operation_id}_{datetime.utcnow().timestamp()}",
                        "description": "Mixed workload payment"
                    }
                    
                    async with session.post(
                        f"{base_url}/api/v1/payments",
                        json=payment_data,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return "create_success", data["id"]
                        else:
                            return "create_failure", None
                else:
                    # Check random payment status (if we have any)
                    # For simplicity, we'll create one first then check it
                    payment_data = {
                        "amount": 50.00,
                        "currency": "USD",
                        "payment_method": "credit_card", 
                        "customer_id": f"check_customer_{operation_id}",
                        "order_id": f"order_check_{operation_id}",
                        "description": "Payment for status check"
                    }
                    
                    async with session.post(
                        f"{base_url}/api/v1/payments",
                        json=payment_data,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            payment_id = data["id"]
                            
                            # Now check its status
                            async with session.get(
                                f"{base_url}/api/v1/payments/{payment_id}",
                                headers=headers
                            ) as status_response:
                                if status_response.status == 200:
                                    return "check_success", payment_id
                                else:
                                    return "check_failure", payment_id
                        else:
                            return "create_failure_before_check", None
        
        # Run 100 mixed operations
        tasks = [mixed_operation(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        operation_types = {}
        for op_type, _ in results:
            operation_types[op_type] = operation_types.get(op_type, 0) + 1
        
        print(f"Mixed workload results: {operation_types}")
        
        total_success = operation_types.get('create_success', 0) + operation_types.get('check_success', 0)
        success_rate = total_success / len(results)
        
        assert success_rate >= 0.9, f"Success rate too low: {success_rate}"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_payment_webhook_processing_load(self, base_url, auth_token):
        """Test webhook processing under load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def send_webhook(webhook_id):
            webhook_data = {
                "event_type": "payment.succeeded",
                "payment_id": f"pay_webhook_load_{webhook_id}",
                "data": {
                    "amount": round(random.uniform(10, 1000), 2),
                    "currency": "USD",
                    "status": "succeeded",
                    "customer_id": f"webhook_customer_{webhook_id}"
                },
                "signature": f"sig_webhook_{webhook_id}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/webhooks/stripe",
                    json=webhook_data,
                    headers=headers
                ) as response:
                    return response.status, webhook_id
        
        # Send 50 webhooks concurrently
        tasks = [send_webhook(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status in [200, 202])
        
        print(f"Webhook processing: {success_count}/{len(results)} successful")
        
        assert success_count >= 45, f"Too many webhook failures: {len(results) - success_count}"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_payment_refund_workload(self, base_url, auth_token):
        """Test refund operations under load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create payments to refund
        payment_ids = []
        for i in range(30):
            payment_data = {
                "amount": 100.00,
                "currency": "USD",
                "payment_method": "credit_card",
                "customer_id": f"refund_customer_{i}",
                "order_id": f"order_refund_{i}",
                "description": "Payment for refund testing"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/payments",
                    json=payment_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        payment_ids.append(data["id"])
        
        # Process refunds concurrently
        async def process_refund(payment_id, refund_id):
            refund_data = {
                "payment_id": payment_id,
                "amount": 50.00,  # Partial refund
                "reason": f"Load test refund {refund_id}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/payments/{payment_id}/refund",
                    json=refund_data,
                    headers=headers
                ) as response:
                    return response.status, payment_id
        
        tasks = [process_refund(pid, i) for i, pid in enumerate(payment_ids)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        
        print(f"Refund processing: {success_count}/{len(payment_ids)} successful")
        
        assert success_count >= len(payment_ids) * 0.8, "Too many refund failures"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "load", "--asyncio-mode=auto"])