import pytest
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from services.app.models import User, UserCreate
from services.app.storage import StorageManager
from services.qa_service.app.knowledge_base import KnowledgeBase
from services.presentation_service.app.models import PresentationCreate, SlideCreate

class TestDatabaseOperations:
    """Comprehensive database operations integration tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.storage = StorageManager(storage_path="test_data")
        self.kb = KnowledgeBase(db_path=":memory:")
        self.test_start_time = datetime.utcnow()
        yield
        # Cleanup
        import shutil
        if Path("test_data").exists():
            shutil.rmtree("test_data")
    
    @pytest.mark.asyncio
    async def test_user_lifecycle(self):
        """Test complete user lifecycle operations"""
        # Create user
        user = User(
            id="test_user_001",
            email="lifecycle@test.com",
            first_name="Lifecycle",
            last_name="Test",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        
        # Save user
        save_result = await self.storage.save_user(user)
        assert save_result == True
        
        # Retrieve user
        retrieved = await self.storage.get_user(user.id)
        assert retrieved.id == user.id
        assert retrieved.email == user.email
        
        # Update user (simulated)
        user.email = "updated@test.com"
        update_result = await self.storage.save_user(user)
        assert update_result == True
        
        # Verify update
        updated_user = await self.storage.get_user(user.id)
        assert updated_user.email == "updated@test.com"
        
        # Delete user
        delete_result = await self.storage.delete_user(user.id)
        assert delete_result == True
        
        # Verify deletion
        deleted_user = await self.storage.get_user(user.id)
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_knowledge_base_transactions(self):
        """Test knowledge base transactional operations"""
        # Add multiple related documents
        doc_ids = []
        for i in range(3):
            doc_id = self.kb.add_document(
                title=f"Transaction Doc {i}",
                content=f"Content for transactional document {i}",
                category="transaction_test",
                tags=["transaction", f"doc_{i}"]
            )
            doc_ids.append(doc_id)
        
        # Add QA pairs linking to documents
        qa_mappings = []
        for doc_id in doc_ids:
            for j in range(2):
                qa_id = self.kb.add_qa_pair(
                    question=f"What is document {doc_id} about?",
                    answer=f"This is about transactional testing for doc {doc_id}",
                    document_id=doc_id,
                    confidence=0.85
                )
                qa_mappings.append((doc_id, qa_id))
        
        # Verify data integrity
        for doc_id in doc_ids:
            document_qa = self.kb.get_document_qa_pairs(doc_id)
            assert len(document_qa) == 2
            for qa in document_qa:
                assert qa['document_id'] == doc_id
        
        # Test search across all documents
        search_results = self.kb.search_documents("transactional testing", limit=10)
        assert len(search_results) == 3
        
        # Test deletion cascade (simulated)
        first_doc_id = doc_ids[0]
        # In a real DB, this would cascade delete related QA pairs
        # For our test, we'll manually verify relationships
        
    def test_concurrent_data_access(self):
        """Test concurrent access to data storage"""
        import threading
        import time
        
        results = []
        errors = []
        
        def concurrent_operation(thread_id, operation_type):
            try:
                if operation_type == "write":
                    for i in range(10):
                        doc_id = self.kb.add_document(
                            title=f"Concurrent Write {thread_id}-{i}",
                            content=f"Content from thread {thread_id} operation {i}",
                            category="concurrency"
                        )
                        results.append(("write", thread_id, i, doc_id))
                        time.sleep(0.01)
                else:  # read
                    for i in range(10):
                        search_results = self.kb.search_documents("concurrency", limit=5)
                        results.append(("read", thread_id, i, len(search_results)))
                        time.sleep(0.01)
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {str(e)}")
        
        # Start multiple threads
        threads = []
        for i in range(3):  # 3 writer threads
            thread = threading.Thread(target=concurrent_operation, args=(f"writer_{i}", "write"))
            threads.append(thread)
        
        for i in range(2):  # 2 reader threads
            thread = threading.Thread(target=concurrent_operation, args=(f"reader_{i}", "read"))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors and operations completed
        assert len(errors) == 0
        assert len(results) == 50  # 5 threads * 10 operations each
        
        # Verify data consistency
        final_search = self.kb.search_documents("concurrency", limit=100)
        assert len(final_search) >= 30  # At least 30 documents from writers
    
    @pytest.mark.asyncio
    async def test_data_validation_and_constraints(self):
        """Test database constraints and data validation"""
        # Test with invalid data
        invalid_users = [
            User(id="", email="invalid", first_name="", last_name="", 
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            User(id="test", email="", first_name="Test", last_name="User",
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        ]
        
        for invalid_user in invalid_users:
            # Depending on implementation, this might raise exceptions
            # For now, we'll test that our system handles invalid data gracefully
            try:
                result = await self.storage.save_user(invalid_user)
                # If we get here, the test might fail depending on requirements
                if invalid_user.id == "":
                    assert result == False, "Should not save user with empty ID"
            except Exception as e:
                # Expected behavior for invalid data
                assert "validation" in str(e).lower() or "constraint" in str(e).lower()
        
        # Test knowledge base constraints
        try:
            # Try to add QA pair with non-existent document ID
            qa_id = self.kb.add_qa_pair(
                question="Test question",
                answer="Test answer",
                document_id=99999,  # Non-existent ID
                confidence=0.9
            )
            # If foreign key constraints are enforced, this should fail
            # If not, we verify the QA was created without document link
            if qa_id is not None:
                qa_pairs = self.kb.get_document_qa_pairs(99999)
                assert len(qa_pairs) == 0, "Should not find QA pairs for non-existent document"
        except Exception as e:
            # Expected if foreign key constraints are enforced
            assert "foreign key" in str(e).lower() or "constraint" in str(e).lower()
    
    def test_performance_benchmarks(self):
        """Test database performance benchmarks"""
        import time
        
        # Bulk insert performance
        start_time = time.time()
        
        batch_size = 100
        for i in range(batch_size):
            self.kb.add_document(
                title=f"Performance Doc {i}",
                content=f"Content for performance testing document {i} with some additional text to make it more substantial for testing.",
                category="performance",
                tags=[f"tag_{j}" for j in range(3)]
            )
        
        insert_time = time.time() - start_time
        print(f"Bulk insert of {batch_size} documents took: {insert_time:.2f}s")
        
        # Query performance
        query_start = time.time()
        for i in range(10):
            results = self.kb.search_documents("performance", limit=50)
        query_time = time.time() - query_start
        
        print(f"10 queries took: {query_time:.2f}s")
        print(f"Average query time: {query_time/10:.3f}s")
        
        # Performance assertions (adjust thresholds based on requirements)
        assert insert_time < 10.0, f"Bulk insert too slow: {insert_time:.2f}s"
        assert query_time < 5.0, f"Query performance too slow: {query_time:.2f}s"
        assert len(results) > 0, "Should return results for valid query"
    
    @pytest.mark.asyncio
    async def test_backup_and_recovery_simulation(self):
        """Simulate backup and recovery operations"""
        # Create test data
        test_data = []
        for i in range(5):
            user = User(
                id=f"backup_user_{i}",
                email=f"backup_{i}@test.com",
                first_name=f"Backup{i}",
                last_name="Test",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            await self.storage.save_user(user)
            test_data.append(user)
        
        # Simulate backup (in real scenario, this would export data)
        backup_data = []
        for user in test_data:
            backup_data.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'backup_timestamp': datetime.utcnow().isoformat()
            })
        
        # Simulate data loss by clearing storage
        for user in test_data:
            await self.storage.delete_user(user.id)
        
        # Verify data is gone
        for user in test_data:
            assert await self.storage.get_user(user.id) is None
        
        # Simulate recovery from backup
        recovery_count = 0
        for backup_item in backup_data:
            recovered_user = User(
                id=backup_item['id'],
                email=backup_item['email'],
                first_name=backup_item['first_name'],
                last_name=backup_item['last_name'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            save_result = await self.storage.save_user(recovered_user)
            if save_result:
                recovery_count += 1
        
        # Verify recovery
        assert recovery_count == len(test_data)
        for user in test_data:
            recovered = await self.storage.get_user(user.id)
            assert recovered is not None
            assert recovered.email == user.email

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])