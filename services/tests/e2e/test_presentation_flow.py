import pytest
import asyncio
import aiohttp
import json
import random
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

class TestPresentationFlowLoad:
    """Load testing for presentation flow scenarios"""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8001"
    
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
    async def test_concurrent_presentation_creation(self, base_url, auth_token):
        """Test creating multiple presentations concurrently"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def create_presentation(pres_id):
            presentation_data = {
                "presentation": {
                    "title": f"Load Test Presentation {pres_id}",
                    "description": f"Presentation created during concurrent load test {pres_id}",
                    "theme": random.choice(["modern", "classic", "dark", "light"]),
                    "tags": ["load-test", "concurrent", f"pres-{pres_id}"]
                },
                "slides": [
                    {
                        "title": f"Slide 1 for Pres {pres_id}",
                        "content": f"This is the first slide content for presentation {pres_id}",
                        "slide_type": "title",
                        "order": 1
                    },
                    {
                        "title": f"Content Slide {pres_id}",
                        "content": f"Detailed content for presentation {pres_id} created during load testing",
                        "slide_type": "content", 
                        "order": 2
                    },
                    {
                        "title": f"Conclusion {pres_id}",
                        "content": f"Conclusion slide for presentation {pres_id}",
                        "slide_type": "content",
                        "order": 3
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/presentations",
                    json=presentation_data,
                    headers=headers
                ) as response:
                    return response.status, await response.text()
        
        # Create 30 presentations concurrently
        tasks = [create_presentation(i) for i in range(30)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        failure_count = len(results) - success_count
        
        print(f"Concurrent presentation creation: {success_count} successes, {failure_count} failures")
        
        assert success_count >= 25, f"Too many failures: {failure_count} out of {len(results)}"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_presentation_read_heavy_workload(self, base_url, auth_token):
        """Test read-heavy workload for presentations"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First create some presentations to read
        presentation_ids = []
        for i in range(20):
            presentation_data = {
                "presentation": {
                    "title": f"Read Load Test Presentation {i}",
                    "description": "Presentation for read-heavy load testing",
                    "theme": "modern",
                    "tags": ["read-test", f"pres-{i}"]
                },
                "slides": [
                    {
                        "title": "Read Test Slide",
                        "content": "Content for read load testing",
                        "slide_type": "content",
                        "order": 1
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/presentations",
                    json=presentation_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        presentation_ids.append(data["id"])
        
        # Now perform concurrent read operations
        async def read_presentation(operation_id):
            # 80% read single presentation, 20% list all presentations
            if random.random() < 0.8 and presentation_ids:
                pres_id = random.choice(presentation_ids)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{base_url}/api/v1/presentations/{pres_id}",
                        headers=headers
                    ) as response:
                        return response.status, "read_single"
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{base_url}/api/v1/presentations",
                        headers=headers
                    ) as response:
                        return response.status, "list_all"
        
        # Perform 100 read operations
        tasks = [read_presentation(i) for i in range(100)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        
        print(f"Read-heavy workload: {success_count}/{len(results)} successful reads")
        
        assert success_rate >= 0.95, f"Read success rate too low: {success_rate}"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_presentation_update_workload(self, base_url, auth_token):
        """Test presentation update operations under load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create presentations to update
        presentation_ids = []
        for i in range(15):
            presentation_data = {
                "presentation": {
                    "title": f"Update Test Presentation {i}",
                    "description": "Presentation for update load testing",
                    "theme": "classic",
                    "tags": ["update-test"]
                },
                "slides": [
                    {
                        "title": "Original Slide",
                        "content": "Original content before updates",
                        "slide_type": "content",
                        "order": 1
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/v1/presentations",
                    json=presentation_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        presentation_ids.append(data["id"])
        
        # Perform concurrent updates
        async def update_presentation(pres_id, update_id):
            update_data = {
                "title": f"Updated Presentation {update_id}",
                "description": f"Updated description for load test {update_id}",
                "theme": random.choice(["modern", "dark", "light"]),
                "status": random.choice(["draft", "published"])
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{base_url}/api/v1/presentations/{pres_id}",
                    json=update_data,
                    headers=headers
                ) as response:
                    return response.status, pres_id
        
        # Update each presentation multiple times concurrently
        tasks = []
        for pres_id in presentation_ids:
            for i in range(3):  # 3 updates per presentation
                tasks.append(update_presentation(pres_id, i))
        
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        
        print(f"Update workload: {success_count}/{len(results)} successful updates")
        
        assert success_count >= len(results) * 0.9, "Too many update failures"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_presentation_deletion_workload(self, base_url, auth_token):
        """Test presentation deletion under load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def create_and_delete(pres_id):
            # Create presentation
            presentation_data = {
                "presentation": {
                    "title": f"Delete Test Presentation {pres_id}",
                    "description": "Presentation for deletion load testing",
                    "theme": "modern",
                    "tags": ["delete-test"]
                },
                "slides": [
                    {
                        "title": "Temporary Slide",
                        "content": "This presentation will be deleted",
                        "slide_type": "content",
                        "order": 1
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                # Create
                async with session.post(
                    f"{base_url}/api/v1/presentations",
                    json=presentation_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        pres_id = data["id"]
                        
                        # Immediately delete
                        async with session.delete(
                            f"{base_url}/api/v1/presentations/{pres_id}",
                            headers=headers
                        ) as delete_response:
                            return delete_response.status, pres_id
                    else:
                        return response.status, None
        
        # Create and delete 25 presentations
        tasks = [create_and_delete(i) for i in range(25)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        
        print(f"Deletion workload: {success_count}/{len(results)} successful create-delete cycles")
        
        assert success_count >= 20, "Too many create-delete failures"
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_presentation_slide_management_load(self, base_url, auth_token):
        """Test slide management operations under load"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a presentation to work with
        presentation_data = {
            "presentation": {
                "title": "Slide Management Load Test",
                "description": "Presentation for slide management load testing",
                "theme": "modern",
                "tags": ["slide-test", "load"]
            },
            "slides": [
                {
                    "title": "Initial Slide",
                    "content": "Starting slide content",
                    "slide_type": "title",
                    "order": 1
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/api/v1/presentations",
                json=presentation_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    presentation_id = data["id"]
                else:
                    pytest.fail("Failed to create presentation for slide testing")
        
        # Perform concurrent slide operations
        async def slide_operation(op_id):
            async with aiohttp.ClientSession() as session:
                if op_id % 3 == 0:
                    # Add slide
                    slide_data = {
                        "title": f"Added Slide {op_id}",
                        "content": f"Content for dynamically added slide {op_id}",
                        "slide_type": "content",
                        "order": op_id + 2,  # Start after initial slide
                        "metadata": {"added_via": "load_test"}
                    }
                    
                    # Note: This would require a specific add-slide endpoint
                    # For now, we'll update the entire presentation
                    update_data = {
                        "title": f"Updated with Slide {op_id}",
                        "slides": [
                            {
                                "title": "Initial Slide",
                                "content": "Starting slide content", 
                                "slide_type": "title",
                                "order": 1
                            },
                            {
                                "title": f"Added Slide {op_id}",
                                "content": f"Content for slide {op_id}",
                                "slide_type": "content",
                                "order": 2
                            }
                        ]
                    }
                    
                    async with session.put(
                        f"{base_url}/api/v1/presentations/{presentation_id}",
                        json=update_data,
                        headers=headers
                    ) as response:
                        return response.status, f"add_slide_{op_id}"
                
                else:
                    # Just read the presentation
                    async with session.get(
                        f"{base_url}/api/v1/presentations/{presentation_id}",
                        headers=headers
                    ) as response:
                        return response.status, f"read_slide_{op_id}"
        
        # Perform 40 slide operations
        tasks = [slide_operation(i) for i in range(40)]
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for status, _ in results if status == 200)
        
        print(f"Slide management: {success_count}/{len(results)} successful operations")
        
        assert success_count >= 35, "Too many slide operation failures"
        
        # Cleanup
        async with aiohttp.ClientSession() as session:
            await session.delete(
                f"{base_url}/api/v1/presentations/{presentation_id}",
                headers=headers
            )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "load", "--asyncio-mode=auto"])