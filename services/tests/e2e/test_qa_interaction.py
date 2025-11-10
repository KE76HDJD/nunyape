import pytest
import asyncio
import aiohttp
import json
import random
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

class TestQAInteractionLoad:
    """Load testing for QA service interactions"""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8081"
    
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
    async def test_concurrent_question_answering(self, base_url, auth_token):
        """Test answering multiple questions concurrently"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        questions = [
            "What is microservices architecture?",
            "How does authentication work in web applications?",
            "What are the benefits of using containers?",
            "How to scale a database?",
            "What is CI/CD pipeline?",
            "How does load balancing work?",
            "What are REST API best practices?",
            "How to handle errors in distributed systems?",
            "What is the difference between SQL and NoSQL?",
            "How to monitor application performance?",
            "What are message queues used for?",
            "How to implement caching strategies?",
            "What is domain-driven design?",
            "How to secure API endpoints?",
            "What are the principles of clean code?",
            "How to perform database migrations?",
            "What is test-driven development?",
            "How to handle file uploads in web applications?",
            "What are web sockets used for?",
            "How to implement search functionality?"
        ]
        
        async def ask_question(question_id):
            question_data = {
                "question": random.choice(questions),
                "question_type": "factual",
                "max_results": random.randint(1, 5)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/qa/ask",
                    json=question_data,
                    headers=headers
                ) as response:
                    return response.status, await response.text()
        
        # Ask 50 questions concurrently
        tasks = [ask_question(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        failure_count = len(results) - success_count
        
        print(f"Concurrent question answering: {success_count} successes, {failure_count} failures")
        
        # Check response quality for successful requests
        valid_answers = 0
        for status, response_text in results:
            if status == 200:
                try:
                    response_data = json.loads(response_text)
                    if response_data.get('answer') and len(response_data['answer']) > 10:
                        valid_answers += 1
                except:
                    pass
        
        print(f"Valid answers: {valid_answers}/{success_count}")
        
        assert success_count >= 45, f"Too many failures: {failure_count}"
        assert valid_answers >= success_count * 0.8, "Too many invalid answers"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_document_upload_and_processing_load(self, base_url, auth_token):
        """Test document upload and processing under load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Sample document contents for upload
        sample_documents = [
            {
                "title": "Microservices Guide",
                "content": """
                    Microservices architecture is an approach to developing software systems 
                    that focuses on building small, independent services that work together.
                    
                    What are microservices?
                    Microservices are small, independent services that communicate over well-defined APIs.
                    
                    Benefits of microservices:
                    - Independent deployment
                    - Technology diversity  
                    - Fault isolation
                    - Scalability
                    
                    Challenges of microservices:
                    - Distributed system complexity
                    - Data consistency
                    - Network latency
                    - Operational overhead
                """,
                "category": "architecture"
            },
            {
                "title": "API Design Principles",
                "content": """
                    RESTful API design follows several key principles that make APIs scalable and maintainable.
                    
                    What is REST?
                    REST stands for Representational State Transfer, an architectural style for distributed systems.
                    
                    Key principles:
                    1. Client-server architecture
                    2. Statelessness
                    3. Cacheability
                    4. Uniform interface
                    5. Layered system
                    
                    How to design good APIs?
                    - Use meaningful resource names
                    - Proper HTTP methods
                    - Consistent error handling
                    - Versioning strategy
                    - Documentation
                """,
                "category": "api-design"
            },
            {
                "title": "Database Management",
                "content": """
                    Effective database management is crucial for application performance and reliability.
                    
                    What is database indexing?
                    Indexing is a technique to improve query performance by creating data structures.
                    
                    Types of databases:
                    - Relational (SQL)
                    - Document (NoSQL)
                    - Key-value stores
                    - Graph databases
                    
                    Database best practices:
                    - Normalization
                    - Proper indexing
                    - Connection pooling
                    - Backup strategies
                    - Monitoring and optimization
                """,
                "category": "database"
            }
        ]
        
        async def upload_document(doc_id):
            doc_data = random.choice(sample_documents)
            doc_data["title"] = f"{doc_data['title']} - Load Test {doc_id}"
            doc_data["tags"] = ["load-test", f"doc-{doc_id}"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/qa/documents",
                    json=doc_data,
                    headers=headers
                ) as response:
                    return response.status, await response.text()
        
        # Upload 20 documents concurrently
        tasks = [upload_document(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 201)
        
        print(f"Document upload: {success_count}/{len(results)} successful uploads")
        
        assert success_count >= 18, "Too many document upload failures"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_knowledge_base_search_load(self, base_url, auth_token):
        """Test knowledge base search operations under load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        search_queries = [
            "microservices",
            "API design",
            "database",
            "authentication",
            "security",
            "performance",
            "scalability",
            "containers",
            "deployment",
            "monitoring",
            "testing",
            "architecture",
            "best practices",
            "error handling",
            "caching"
        ]
        
        async def search_knowledge_base(search_id):
            query = random.choice(search_queries)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{base_url}/api/v1/qa/search?query={query}&limit=10",
                    headers=headers
                ) as response:
                    return response.status, query, await response.text()
        
        # Perform 60 search operations
        tasks = [search_knowledge_base(i) for i in range(60)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _, _ in results if status == 200)
        
        # Analyze search results
        results_with_data = 0
        for status, query, response_text in results:
            if status == 200:
                try:
                    response_data = json.loads(response_text)
                    if response_data.get('results') and len(response_data['results']) > 0:
                        results_with_data += 1
                except:
                    pass
        
        print(f"Knowledge base search: {success_count}/{len(results)} successful, {results_with_data} with results")
        
        assert success_count >= 55, "Too many search failures"
        assert results_with_data >= success_count * 0.7, "Too many empty search results"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_mixed_qa_workload(self, base_url, auth_token):
        """Test mixed QA service workload"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def mixed_operation(op_id):
            operation_type = random.choice(["ask", "search", "stats", "documents"])
            
            async with aiohttp.ClientSession() as session:
                if operation_type == "ask":
                    question_data = {
                        "question": "What are software design patterns?",
                        "max_results": 3
                    }
                    async with session.post(
                        f"{base_url}/api/v1/qa/ask",
                        json=question_data,
                        headers=headers
                    ) as response:
                        return response.status, "ask"
                
                elif operation_type == "search":
                    query = random.choice(["design", "patterns", "software"])
                    async with session.get(
                        f"{base_url}/api/v1/qa/search?query={query}&limit=5",
                        headers=headers
                    ) as response:
                        return response.status, "search"
                
                elif operation_type == "stats":
                    async with session.get(
                        f"{base_url}/api/v1/qa/stats",
                        headers=headers
                    ) as response:
                        return response.status, "stats"
                
                else:  # documents
                    async with session.get(
                        f"{base_url}/api/v1/qa/documents",
                        headers=headers
                    ) as response:
                        return response.status, "documents"
        
        # Perform 80 mixed operations
        tasks = [mixed_operation(i) for i in range(80)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results by operation type
        operation_results = {}
        for status, op_type in results:
            if op_type not in operation_results:
                operation_results[op_type] = {"success": 0, "total": 0}
            operation_results[op_type]["total"] += 1
            if status == 200:
                operation_results[op_type]["success"] += 1
        
        print("Mixed QA workload results:")
        for op_type, stats in operation_results.items():
            success_rate = stats["success"] / stats["total"]
            print(f"  {op_type}: {stats['success']}/{stats['total']} ({success_rate:.1%})")
        
        # Verify overall success rate
        total_success = sum(stats["success"] for stats in operation_results.values())
        overall_success_rate = total_success / len(results)
        
        assert overall_success_rate >= 0.9, f"Overall success rate too low: {overall_success_rate}"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_qa_service_stress_test(self, base_url, auth_token):
        """Stress test for QA service with high concurrent load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def stress_operation(op_id):
            # Mix of simple and complex operations
            if op_id % 4 == 0:
                # Complex question
                question_data = {
                    "question": "Explain the differences between microservices and monolithic architecture including pros and cons of each approach",
                    "max_results": 5
                }
            else:
                # Simple question
                simple_questions = [
                    "What is API?",
                    "Define database",
                    "What is caching?",
                    "Explain authentication"
                ]
                question_data = {
                    "question": random.choice(simple_questions),
                    "max_results": 2
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/qa/ask",
                    json=question_data,
                    headers=headers
                ) as response:
                    return response.status, op_id
        
        # Run 100 concurrent operations for stress testing
        tasks = [stress_operation(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        success_rate = success_count / len(results)
        
        print(f"QA stress test: {success_count}/{len(results)} successful ({success_rate:.1%})")
        
        # For stress testing, we might accept a lower success rate
        assert success_rate >= 0.8, f"Stress test success rate too low: {success_rate}"
        
        # Check response times (this would need timing measurements)
        # For now, we just verify the service didn't completely crash

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "load", "--asyncio-mode=auto"])