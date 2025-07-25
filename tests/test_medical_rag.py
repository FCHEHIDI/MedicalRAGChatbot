"""
Comprehensive Test Suite for Medical RAG Chatbot
================================================

Tests all components: API endpoints, RAG functionality, 
medical accuracy, and system integration.
"""

import pytest
import requests
import asyncio
import time
from typing import Dict, Any

class TestMedicalRAGChatbot:
    base_url = "http://localhost:8000"
    
    def setup_method(self):
        """Setup before each test"""
        # Wait for server to be ready
        self.wait_for_server()
    
    def wait_for_server(self, timeout=30):
        """Wait for server to be available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    return True
            except:
                time.sleep(1)
        raise Exception("Server not available")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "components" in data
        
        # Check components
        components = data["components"]
        assert "api" in components
        assert "database" in components
        assert "llm" in components
        
        print(f"✅ Health Check: {data['status']}")
    
    def test_chat_endpoint_basic(self):
        """Test basic chat functionality"""
        test_message = "What is hypertension?"
        
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": test_message},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "response" in data
        assert "conversation_id" in data
        assert "sources" in data
        assert "safety_disclaimer" in data
        assert "timestamp" in data
        
        # Check content quality
        assert len(data["response"]) > 50  # Substantial response
        assert "hypertension" in data["response"].lower()
        
        print(f"✅ Chat Response Length: {len(data['response'])}")
    
    def test_medical_accuracy(self):
        """Test medical response accuracy"""
        medical_tests = [
            {
                "question": "What are the normal blood pressure ranges?",
                "expected_keywords": ["120/80", "mmHg", "systolic", "diastolic"]
            },
            {
                "question": "What are the symptoms of diabetes?",
                "expected_keywords": ["polyuria", "polydipsia", "thirst", "urination"]
            },
            {
                "question": "When should I call 911 for chest pain?",
                "expected_keywords": ["emergency", "crushing", "radiating", "shortness"]
            }
        ]
        
        for test in medical_tests:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"message": test["question"]},
                timeout=60
            )
            
            assert response.status_code == 200
            data = response.json()
            
            response_text = data["response"].lower()
            found_keywords = [kw for kw in test["expected_keywords"] 
                            if kw.lower() in response_text]
            
            # At least 2 expected keywords should be present
            assert len(found_keywords) >= 2, f"Missing keywords in: {test['question']}"
            
            print(f"✅ Medical Test: {test['question'][:50]}... ({len(found_keywords)} keywords)")
    
    def test_safety_disclaimers(self):
        """Test that safety disclaimers are present"""
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": "Should I stop taking my medication?"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check disclaimer presence
        disclaimer = data.get("safety_disclaimer", "")
        assert "medical advice" in disclaimer.lower()
        assert "healthcare professional" in disclaimer.lower()
        
        print("✅ Safety Disclaimer Present")
    
    def test_conversation_continuity(self):
        """Test conversation memory"""
        # First message
        response1 = requests.post(
            f"{self.base_url}/chat",
            json={"message": "What is diabetes?"},
            timeout=60
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        conversation_id = data1["conversation_id"]
        
        # Follow-up message
        response2 = requests.post(
            f"{self.base_url}/chat",
            json={
                "message": "What are the treatment options?",
                "conversation_id": conversation_id
            },
            timeout=60
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should maintain same conversation
        assert data2["conversation_id"] == conversation_id
        
        print("✅ Conversation Continuity")
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Empty message
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": ""},
            timeout=30
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
        
        # Very long message
        long_message = "A" * 10000
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": long_message},
            timeout=60
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 413]
        
        print("✅ Error Handling")
    
    def test_response_time(self):
        """Test response time performance"""
        start_time = time.time()
        
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": "What is a fever?"},
            timeout=60
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 30  # Should respond within 30 seconds
        
        print(f"✅ Response Time: {response_time:.2f}s")
    
    def test_rag_integration(self):
        """Test RAG system integration"""
        # Question that should use RAG data
        response = requests.post(
            f"{self.base_url}/chat",
            json={"message": "What are the diagnostic criteria for diabetes?"},
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check if sources are being used
        sources = data.get("sources", [])
        
        # Response should be substantial and medical
        response_text = data["response"]
        assert len(response_text) > 100
        assert any(term in response_text.lower() for term in 
                  ["glucose", "hba1c", "diabetes", "diagnostic"])
        
        print(f"✅ RAG Integration: {len(sources)} sources")

def run_tests():
    """Run all tests and generate report"""
    print("🧪 MEDICAL RAG CHATBOT - TEST SUITE")
    print("=" * 60)
    
    test_instance = TestMedicalRAGChatbot()
    
    tests = [
        ("Health Endpoint", test_instance.test_health_endpoint),
        ("Basic Chat", test_instance.test_chat_endpoint_basic),
        ("Medical Accuracy", test_instance.test_medical_accuracy),
        ("Safety Disclaimers", test_instance.test_safety_disclaimers),
        ("Conversation Continuity", test_instance.test_conversation_continuity),
        ("Error Handling", test_instance.test_error_handling),
        ("Response Time", test_instance.test_response_time),
        ("RAG Integration", test_instance.test_rag_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Testing: {test_name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
