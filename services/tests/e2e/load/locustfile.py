from locust import HttpUser, task, between, TaskSet
import json
import random
import time

class UserBehavior(TaskSet):
    """Define user behavior for load testing"""
    
    def on_start(self):
        """Called when a user starts the test"""
        self.auth_token = self.get_auth_token()
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }
    
    def get_auth_token(self):
        """Get authentication token"""
        login_data = {
            "email": "load_test@company.com",
            "password": "LoadTestPass123!"
        }
        
        with self.client.post(
            "/api/v1/token",
            json=login_data,
            catch_response=True,
            name="Get Auth Token"
        ) as response:
            if response.status_code == 200:
                return response.json()['access_token']
            else:
                response.failure(f"Failed to get token: {response.status_code}")
                return None
    
    @task(3)
    def create_payment(self):
        """Create a payment (high frequency)"""
        if not self.auth_token:
            return
            
        payment_data = {
            "amount": round(random.uniform(1, 500), 2),
            "currency": "USD",
            "payment_method": random.choice(["credit_card", "paypal", "bank_transfer"]),
            "customer_id": f"load_test_customer_{self.user_id}",
            "order_id": f"order_{int(time.time())}_{self.user_id}",
            "description": "Load test payment transaction"
        }
        
        with self.client.post(
            "/api/v1/payments",
            json=payment_data,
            headers=self.headers,
            catch_response=True,
            name="Create Payment"
        ) as response:
            if response.status_code == 200:
                payment_id = response.json().get('id')
                self.check_payment_status(payment_id)
            else:
                response.failure(f"Payment creation failed: {response.status_code}")
    
    def check_payment_status(self, payment_id):
        """Check payment status"""
        with self.client.get(
            f"/api/v1/payments/{payment_id}",
            headers=self.headers,
            catch_response=True,
            name="Check Payment Status"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Payment status check failed: {response.status_code}")
    
    @task(2)
    def create_presentation(self):
        """Create a presentation (medium frequency)"""
        if not self.auth_token:
            return
            
        presentation_data = {
            "presentation": {
                "title": f"Load Test Presentation {int(time.time())}",
                "description": "Presentation created during load testing",
                "theme": random.choice(["modern", "classic", "dark"]),
                "tags": ["load-test", "automated"]
            },
            "slides": [
                {
                    "title": "Welcome Slide",
                    "content": "This is a load test presentation",
                    "slide_type": "title",
                    "order": 1
                },
                {
                    "title": "Content Slide", 
                    "content": "This content was generated during load testing",
                    "slide_type": "content",
                    "order": 2
                }
            ]
        }
        
        with self.client.post(
            "/api/v1/presentations",
            json=presentation_data,
            headers=self.headers,
            catch_response=True,
            name="Create Presentation"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Presentation creation failed: {response.status_code}")
    
    @task(4)
    def use_qa_service(self):
        """Use QA service (very high frequency)"""
        if not self.auth_token:
            return
            
        questions = [
            "What is microservices architecture?",
            "How does authentication work?",
            "What are API best practices?",
            "How to scale web applications?",
            "What is containerization?",
            "How does load balancing work?",
            "What are the benefits of cloud computing?",
            "How to handle database migrations?",
            "What is CI/CD pipeline?",
            "How to monitor application performance?"
        ]
        
        question_data = {
            "question": random.choice(questions),
            "max_results": random.randint(1, 5)
        }
        
        with self.client.post(
            "/api/v1/qa/ask",
            json=question_data,
            headers=self.headers,
            catch_response=True,
            name="Ask Question"
        ) as response:
            if response.status_code == 200:
                answer_data = response.json()
                if answer_data.get('answer'):
                    response.success()
                else:
                    response.failure("No answer received from QA service")
            else:
                response.failure(f"QA service failed: {response.status_code}")
    
    @task(1)
    def browse_presentations(self):
        """Browse existing presentations (low frequency)"""
        if not self.auth_token:
            return
            
        with self.client.get(
            "/api/v1/presentations",
            headers=self.headers,
            catch_response=True,
            name="Browse Presentations"
        ) as response:
            if response.status_code == 200:
                presentations = response.json()
                # Optionally view a specific presentation
                if presentations and len(presentations) > 0:
                    presentation_id = random.choice(presentations)['id']
                    self.view_presentation(presentation_id)
            else:
                response.failure(f"Failed to browse presentations: {response.status_code}")
    
    def view_presentation(self, presentation_id):
        """View a specific presentation"""
        with self.client.get(
            f"/api/v1/presentations/{presentation_id}",
            headers=self.headers,
            catch_response=True,
            name="View Presentation"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to view presentation: {response.status_code}")
    
    @task(1)
    def get_service_stats(self):
        """Get service statistics (low frequency)"""
        if not self.auth_token:
            return
            
        endpoints = [
            "/api/v1/qa/stats",
            "/api/v1/users/me",
            "/health"
        ]
        
        for endpoint in endpoints:
            with self.client.get(
                endpoint,
                headers=self.headers,
                catch_response=True,
                name=f"Get {endpoint} Stats"
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Stats endpoint failed: {endpoint} - {response.status_code}")

class WebsiteUser(HttpUser):
    """Main user class for load testing"""
    tasks = [UserBehavior]
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = id(self)

class HighLoadUser(HttpUser):
    """User class for high load scenarios"""
    tasks = [UserBehavior]
    wait_time = between(0.1, 1)  # Very short wait times for high load
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = f"high_load_{id(self)}"

class ApiClientUser(HttpUser):
    """User class simulating API clients"""
    
    @task(10)
    def make_api_calls(self):
        """Make various API calls"""
        endpoints = [
            ("/api/v1/qa/ask", "POST", {
                "question": "What is the system status?",
                "max_results": 1
            }),
            ("/api/v1/presentations", "GET", None),
            ("/health", "GET", None),
            ("/api/v1/payments/status/mock_payment", "GET", None)
        ]
        
        for endpoint, method, data in endpoints:
            if method == "POST":
                self.client.post(endpoint, json=data, name="API Client POST")
            else:
                self.client.get(endpoint, name="API Client GET")
    
    wait_time = between(0.5, 2)