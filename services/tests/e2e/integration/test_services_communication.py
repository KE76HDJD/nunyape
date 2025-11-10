import pytest
import asyncio
import aiohttp
import json
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

class TestServicesCommunication:
    """Test communication between microservices"""
    
    @pytest.fixture
    def base_urls(self):
        """Return base URLs for services"""
        return {
            "auth": "http://localhost:8000",
            "payment": "http://localhost:8080", 
            "presentation": "http://localhost:8001",
            "qa": "http://localhost:8081",
            "webhook": "http://localhost:8090"
        }
    
    @pytest.fixture
    async def auth_token(self, base_urls):
        """Get authentication token for API requests"""
        async with aiohttp.ClientSession() as session:
            login_data = {
                "email": "admin@testcompany.com",
                "password": "AdminSecurePass123!"
            }
            async with session.post(
                f"{base_urls['auth']}/api/v1/token",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["access_token"]
                else:
                    pytest.fail("Failed to get auth token")
    
    @pytest.mark.asyncio
    async def test_service_health_checks(self, base_urls):
        """Test that all services are healthy"""
        async with aiohttp.ClientSession() as session:
            for service_name, url in base_urls.items():
                async with session.get(f"{url}/health") as response:
                    assert response.status == 200, f"Service {service_name} is not healthy"
                    health_data = await response.json()
                    assert health_data["status"] == "healthy"
                    print(f"✅ {service_name} service is healthy")
    
    @pytest.mark.asyncio
    async def test_cross_service_authentication(self, base_urls, auth_token):
        """Test that services can communicate with proper authentication"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with aiohttp.ClientSession() as session:
            # Test accessing protected endpoints across services
            endpoints = [
                f"{base_urls['auth']}/api/v1/users/me",
                f"{base_urls['presentation']}/api/v1/presentations",
                f"{base_urls['qa']}/api/v1/qa/stats"
            ]
            
            for endpoint in endpoints:
                async with session.get(endpoint, headers=headers) as response:
                    assert response.status in [200, 201, 204], f"Failed to access {endpoint}"
                    print(f"✅ Successfully accessed {endpoint}")
    
    @pytest.mark.asyncio
    async def test_payment_to_presentation_flow(self, base_urls, auth_token):
        """Test complete flow from payment to presentation creation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Create a payment
            payment_data = {
                "amount": 99.99,
                "currency": "USD",
                "payment_method": "credit_card",
                "customer_id": "test_customer_001",
                "order_id": f"order_{datetime.utcnow().timestamp()}",
                "description": "Premium presentation package"
            }
            
            async with session.post(
                f"{base_urls['payment']}/api/v1/payments",
                json=payment_data,
                headers=headers
            ) as response:
                assert response.status == 200
                payment_result = await response.json()
                payment_id = payment_result["id"]
                print(f"✅ Payment created: {payment_id}")
            
            # Step 2: Verify payment status
            async with session.get(
                f"{base_urls['payment']}/api/v1/payments/{payment_id}",
                headers=headers
            ) as response:
                assert response.status == 200
                payment_status = await response.json()
                assert payment_status["status"] == "completed"
                print(f"✅ Payment completed: {payment_id}")
            
            # Step 3: Create presentation (unlocked by successful payment)
            presentation_data = {
                "title": "Premium Presentation",
                "description": "Created after successful payment",
                "theme": "premium",
                "tags": ["paid", "premium"]
            }
            
            slides_data = [
                {
                    "title": "Welcome Slide",
                    "content": "Thank you for your purchase!",
                    "slide_type": "title",
                    "order": 1
                }
            ]
            
            async with session.post(
                f"{base_urls['presentation']}/api/v1/presentations",
                json={
                    "presentation": presentation_data,
                    "slides": slides_data
                },
                headers=headers
            ) as response:
                assert response.status == 200
                presentation_result = await response.json()
                presentation_id = presentation_result["id"]
                print(f"✅ Presentation created: {presentation_id}")
            
            # Step 4: Verify presentation has premium features
            async with session.get(
                f"{base_urls['presentation']}/api/v1/presentations/{presentation_id}",
                headers=headers
            ) as response:
                assert response.status == 200
                presentation = await response.json()
                assert presentation["theme"] == "premium"
                print(f"✅ Premium features verified")
    
    @pytest.mark.asyncio
    async def test_qa_service_integration(self, base_urls, auth_token):
        """Test QA service integration with other services"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with aiohttp.ClientSession() as session:
            # Add document to knowledge base
            document_data = {
                "title": "Microservices Integration Guide",
                "content": """
                    This guide explains how microservices communicate with each other.
                    Services use HTTP APIs and message queues for communication.
                    Authentication is handled via JWT tokens.
                    What is service discovery?
                    Service discovery helps services find each other in the network.
                    How to handle service failures?
                    Use circuit breakers and retry mechanisms.
                """,
                "category": "architecture",
                "tags": ["microservices", "integration", "api"]
            }
            
            async with session.post(
                f"{base_urls['qa']}/api/v1/qa/documents",
                json=document_data,
                headers=headers
            ) as response:
                assert response.status == 201
                doc_result = await response.json()
                document_id = doc_result["document_id"]
                print(f"✅ Document added to knowledge base: {document_id}")
            
            # Ask question about microservices
            question_data = {
                "question": "How do microservices communicate?",
                "question_type": "factual",
                "max_results": 3
            }
            
            async with session.post(
                f"{base_urls['qa']}/api/v1/qa/ask",
                json=question_data,
                headers=headers
            ) as response:
                assert response.status == 200
                answer_result = await response.json()
                assert len(answer_result["answer"]) > 0
                assert answer_result["confidence"] > 0.5
                print(f"✅ QA service provided answer: {answer_result['answer'][:100]}...")
    
    @pytest.mark.asyncio
    async def test_webhook_communication(self, base_urls, auth_token):
        """Test webhook communication between services"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with aiohttp.ClientSession() as session:
            # Simulate payment webhook
            webhook_data = {
                "event_type": "payment.succeeded",
                "payment_id": "pay_test_123",
                "data": {
                    "amount": 99.99,
                    "currency": "USD",
                    "customer_id": "test_customer_001"
                },
                "signature": "test_signature_123"
            }
            
            async with session.post(
                f"{base_urls['webhook']}/api/v1/webhooks/stripe",
                json=webhook_data,
                headers=headers
            ) as response:
                # Webhook might return 200 or 202 accepted
                assert response.status in [200, 202]
                print("✅ Webhook processed successfully")
            
            # Test notification service integration
            notification_data = {
                "user_id": "test_user_001",
                "type": "payment_success",
                "title": "Payment Successful",
                "message": "Your payment of $99.99 was processed successfully",
                "metadata": {
                    "payment_id": "pay_test_123",
                    "amount": 99.99
                }
            }
            
            # This would typically go to a notification service
            # For now, we'll log it
            print(f"📧 Notification would be sent: {notification_data}")
    
    @pytest.mark.asyncio
    async def test_error_scenarios(self, base_urls, auth_token):
        """Test error handling in service communication"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with aiohttp.ClientSession() as session:
            # Test with invalid payment data
            invalid_payment = {
                "amount": -100,  # Invalid amount
                "currency": "INVALID",  # Invalid currency
                "payment_method": "invalid_method"
            }
            
            async with session.post(
                f"{base_urls['payment']}/api/v1/payments",
                json=invalid_payment,
                headers=headers
            ) as response:
                # Should return 400 Bad Request
                assert response.status == 400
                error_data = await response.json()
                assert "error" in error_data or "detail" in error_data
                print("✅ Proper error handling for invalid payment")
            
            # Test with non-existent resource
            async with session.get(
                f"{base_urls['presentation']}/api/v1/presentations/non_existent_id",
                headers=headers
            ) as response:
                assert response.status == 404
                print("✅ Proper 404 handling for non-existent resource")
            
            # Test rate limiting (if implemented)
            for i in range(10):
                async with session.get(
                    f"{base_urls['qa']}/api/v1/qa/stats",
                    headers=headers
                ) as response:
                    if response.status == 429:  # Too Many Requests
                        print("✅ Rate limiting properly enforced")
                        break
                    elif i == 9:
                        print("⚠️  Rate limiting not triggered with 10 requests")
    
    @pytest.mark.asyncio
    async def test_data_consistency_across_services(self, base_urls, auth_token):
        """Test data consistency across multiple services"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        test_user_id = f"test_user_{datetime.utcnow().timestamp()}"
        
        async with aiohttp.ClientSession() as session:
            # Create user profile in auth service
            user_data = {
                "email": f"consistency_test_{datetime.utcnow().timestamp()}@test.com",
                "first_name": "Consistency",
                "last_name": "Test",
                "password": "TestPass123!"
            }
            
            async with session.post(
                f"{base_urls['auth']}/api/v1/users",
                json=user_data,
                headers=headers
            ) as response:
                assert response.status in [200, 201]
                user_result = await response.json()
                user_id = user_result["id"]
                print(f"✅ User created: {user_id}")
            
            # Create presentation for the user
            presentation_data = {
                "title": "Consistency Test Presentation",
                "description": "Testing data consistency across services",
                "theme": "default",
                "slides": [
                    {
                        "title": "Test Slide",
                        "content": "Content for consistency testing",
                        "slide_type": "content",
                        "order": 1
                    }
                ]
            }
            
            async with session.post(
                f"{base_urls['presentation']}/api/v1/presentations",
                json={
                    "presentation": presentation_data,
                    "slides": presentation_data["slides"]
                },
                headers=headers
            ) as response:
                assert response.status == 200
                presentation_result = await response.json()
                presentation_id = presentation_result["id"]
                print(f"✅ Presentation created: {presentation_id}")
            
            # Verify user can access their presentation
            async with session.get(
                f"{base_urls['presentation']}/api/v1/presentations/{presentation_id}",
                headers=headers
            ) as response:
                assert response.status == 200
                presentation = await response.json()
                assert presentation["owner_id"] == user_id
                print("✅ Data consistency verified: user owns presentation")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])