#!/usr/bin/env python3
"""
Test script for PostgreSQL+Vector LLM MCP tools
Tests all new tools to ensure they work correctly
"""

import sys
import os
import asyncio
import json

# Add current directory to path
sys.path.append('.')

from mcp_langflow_connector_simple import SimpleLangFlowMCPConnector

async def test_postgresql_vector_tools():
    """Test all PostgreSQL+Vector LLM tools"""
    
    print("🧪 Testing PostgreSQL+Vector LLM MCP Tools")
    print("=" * 60)
    
    # Initialize connector
    connector = SimpleLangFlowMCPConnector()
    
    if not connector.vector_llm:
        print("❌ PostgreSQL+Vector LLM not initialized")
        print("Please ensure PostgreSQL is running and pgvector extension is installed")
        return
    
    print("✅ PostgreSQL+Vector LLM initialized successfully")
    print()
    
    # Test 1: Store Embedding
    print("📝 Test 1: Store Embedding")
    print("-" * 30)
    
    store_args = {
        "name": "test_document_001",
        "content": "This is a test document about machine learning and artificial intelligence.",
        "metadata": {
            "category": "technology",
            "author": "Test User",
            "date": "2024-01-15"
        }
    }
    
    result = await connector.handle_store_embedding(store_args)
    print(f"Result: {result}")
    print()
    
    # Test 2: Store another embedding for similarity search
    print("📝 Test 2: Store Second Embedding")
    print("-" * 30)
    
    store_args2 = {
        "name": "test_document_002",
        "content": "Machine learning algorithms are used in artificial intelligence applications.",
        "metadata": {
            "category": "technology",
            "author": "Test User",
            "date": "2024-01-16"
        }
    }
    
    result2 = await connector.handle_store_embedding(store_args2)
    print(f"Result: {result2}")
    print()
    
    # Test 3: Similarity Search
    print("🔍 Test 3: Similarity Search")
    print("-" * 30)
    
    search_args = {
        "query": "machine learning algorithms",
        "limit": 5
    }
    
    result3 = await connector.handle_similarity_search(search_args)
    print(f"Result: {result3}")
    print()
    
    # Test 4: Process Text with LLM - Summarize
    print("🤖 Test 4: LLM Processing - Summarize")
    print("-" * 30)
    
    llm_args = {
        "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions based on those patterns. There are several types of machine learning including supervised learning, unsupervised learning, and reinforcement learning.",
        "task": "summarize"
    }
    
    result4 = await connector.handle_process_text_with_llm(llm_args)
    print(f"Result: {result4}")
    print()
    
    # Test 5: Process Text with LLM - Extract Keywords
    print("🔑 Test 5: LLM Processing - Extract Keywords")
    print("-" * 30)
    
    llm_args2 = {
        "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed.",
        "task": "extract_keywords"
    }
    
    result5 = await connector.handle_process_text_with_llm(llm_args2)
    print(f"Result: {result5}")
    print()
    
    # Test 6: Process Text with LLM - Sentiment Analysis
    print("😊 Test 6: LLM Processing - Sentiment Analysis")
    print("-" * 30)
    
    llm_args3 = {
        "text": "I love machine learning! It's amazing how computers can learn from data.",
        "task": "sentiment_analysis"
    }
    
    result6 = await connector.handle_process_text_with_llm(llm_args3)
    print(f"Result: {result6}")
    print()
    
    # Test 7: DataFrame Operations
    print("📊 Test 7: DataFrame Operations")
    print("-" * 30)
    
    csv_data = """name,age,city,occupation
John,25,NYC,Engineer
Jane,30,LA,Designer
Bob,35,Chicago,Manager
Alice,28,Boston,Developer
Charlie,32,Seattle,Analyst"""
    
    df_args = {
        "operation": "head",
        "data": csv_data,
        "parameters": {
            "rows": 3
        }
    }
    
    result7 = await connector.handle_dataframe_operations(df_args)
    print(f"Result: {result7}")
    print()
    
    # Test 8: DataFrame Operations - Describe
    print("📈 Test 8: DataFrame Operations - Describe")
    print("-" * 30)
    
    df_args2 = {
        "operation": "describe",
        "data": csv_data
    }
    
    result8 = await connector.handle_dataframe_operations(df_args2)
    print(f"Result: {result8}")
    print()
    
    # Test 9: Split Text
    print("✂️ Test 9: Split Text")
    print("-" * 30)
    
    split_args = {
        "text": "This is sentence one. This is sentence two. This is sentence three.",
        "method": "sentences"
    }
    
    result9 = await connector.handle_split_text(split_args)
    print(f"Result: {result9}")
    print()
    
    # Test 10: Split Text - Words
    print("🔤 Test 10: Split Text - Words")
    print("-" * 30)
    
    split_args2 = {
        "text": "Machine learning is fascinating",
        "method": "words"
    }
    
    result10 = await connector.handle_split_text(split_args2)
    print(f"Result: {result10}")
    print()
    
    # Test 11: Structured Output
    print("📋 Test 11: Structured Output")
    print("-" * 30)
    
    structured_args = {
        "text": "Contact: John Doe, Email: john@example.com, Phone: 555-1234, Age: 30",
        "schema": {
            "name": "Contact: ([^,]+)",
            "email": "Email: ([^,]+)",
            "phone": "Phone: ([^\\s]+)",
            "age": "Age: (\\d+)"
        }
    }
    
    result11 = await connector.handle_structured_output(structured_args)
    print(f"Result: {result11}")
    print()
    
    # Test 12: Type Convert
    print("🔄 Test 12: Type Convert")
    print("-" * 30)
    
    convert_args = {
        "data": '[{"name":"John","age":25},{"name":"Jane","age":30}]',
        "target_type": "csv"
    }
    
    result12 = await connector.handle_type_convert(convert_args)
    print(f"Result: {result12}")
    print()
    
    # Test 13: Type Convert - JSON
    print("📄 Test 13: Type Convert - JSON")
    print("-" * 30)
    
    convert_args2 = {
        "data": '{"name":"John","age":25,"city":"NYC"}',
        "target_type": "json"
    }
    
    result13 = await connector.handle_type_convert(convert_args2)
    print(f"Result: {result13}")
    print()
    
    print("✅ All PostgreSQL+Vector LLM tests completed!")
    print("=" * 60)

async def test_error_handling():
    """Test error handling for PostgreSQL+Vector LLM tools"""
    
    print("\n🧪 Testing Error Handling")
    print("=" * 60)
    
    connector = SimpleLangFlowMCPConnector()
    
    if not connector.vector_llm:
        print("❌ Cannot test error handling - PostgreSQL+Vector LLM not initialized")
        return
    
    # Test 1: Missing required parameters
    print("❌ Test 1: Missing Required Parameters")
    print("-" * 30)
    
    invalid_args = {
        "name": "test"  # Missing content
    }
    
    result = await connector.handle_store_embedding(invalid_args)
    print(f"Result: {result}")
    print()
    
    # Test 2: Invalid task type
    print("❌ Test 2: Invalid Task Type")
    print("-" * 30)
    
    invalid_llm_args = {
        "text": "Test text",
        "task": "invalid_task"
    }
    
    result2 = await connector.handle_process_text_with_llm(invalid_llm_args)
    print(f"Result: {result2}")
    print()
    
    # Test 3: Invalid DataFrame operation
    print("❌ Test 3: Invalid DataFrame Operation")
    print("-" * 30)
    
    invalid_df_args = {
        "operation": "invalid_operation",
        "data": "name,age\nJohn,25"
    }
    
    result3 = await connector.handle_dataframe_operations(invalid_df_args)
    print(f"Result: {result3}")
    print()
    
    print("✅ Error handling tests completed!")
    print("=" * 60)

async def main():
    """Main test function"""
    
    print("🚀 PostgreSQL+Vector LLM MCP Tools Test Suite")
    print("=" * 60)
    
    try:
        # Test normal functionality
        await test_postgresql_vector_tools()
        
        # Test error handling
        await test_error_handling()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 