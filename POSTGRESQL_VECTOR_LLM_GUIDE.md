# PostgreSQL+Vector LLM MCP Tools Guide

## Overview

The PostgreSQL+Vector LLM integration provides local processing capabilities that can replace many external API dependencies. This system combines PostgreSQL with pgvector for vector storage and similarity search, along with local LLM-like processing capabilities.

## Key Benefits

✅ **Local Processing**: No external API calls required  
✅ **Vector Storage**: Efficient similarity search with pgvector  
✅ **Cost Effective**: Eliminates API costs for basic operations  
✅ **Privacy**: All data stays local  
✅ **Scalable**: PostgreSQL handles large datasets efficiently  
✅ **Integrated**: Works seamlessly with existing MCP tools  

## Available Tools

### 1. **store_embedding**
Store text content with vector embeddings for similarity search.

**Parameters:**
- `name` (string, required): Identifier for the content
- `content` (string, required): Text content to embed and store
- `metadata` (object, optional): Additional metadata as JSON

**Example Usage:**
```json
{
  "name": "document_001",
  "content": "This is a sample document about machine learning.",
  "metadata": {
    "category": "technology",
    "author": "John Doe",
    "date": "2024-01-15"
  }
}
```

### 2. **similarity_search**
Search for similar content using vector similarity.

**Parameters:**
- `query` (string, required): Search query text
- `limit` (integer, optional): Maximum results (default: 5, max: 20)

**Example Usage:**
```json
{
  "query": "machine learning algorithms",
  "limit": 10
}
```

### 3. **process_text_with_llm**
Process text using local LLM-like operations.

**Parameters:**
- `text` (string, required): Text to process
- `task` (string, required): Processing task type
- `parameters` (object, optional): Task-specific parameters

**Available Tasks:**
- `summarize`: Extractive text summarization
- `extract_keywords`: Keyword extraction
- `classify`: Text classification
- `translate`: Text translation (placeholder)
- `sentiment_analysis`: Sentiment analysis

**Example Usage:**
```json
{
  "text": "This is a long document that needs to be summarized.",
  "task": "summarize"
}
```

### 4. **dataframe_operations**
Perform DataFrame operations on CSV data.

**Parameters:**
- `operation` (string, required): DataFrame operation
- `data` (string, required): CSV data to process
- `parameters` (object, optional): Operation-specific parameters

**Available Operations:**
- `head`: Get first N rows
- `tail`: Get last N rows
- `describe`: Statistical summary
- `info`: DataFrame information
- `filter`: Filter by column value
- `sort`: Sort by column
- `groupby`: Group and aggregate

**Example Usage:**
```json
{
  "operation": "head",
  "data": "name,age,city\nJohn,25,NYC\nJane,30,LA",
  "parameters": {
    "rows": 5
  }
}
```

### 5. **split_text**
Split text using various methods.

**Parameters:**
- `text` (string, required): Text to split
- `method` (string, optional): Splitting method (default: "sentences")
- `parameters` (object, optional): Method-specific parameters

**Available Methods:**
- `sentences`: Split by sentence boundaries
- `words`: Split into individual words
- `paragraphs`: Split by paragraph breaks
- `chunks`: Split into fixed-size chunks

**Example Usage:**
```json
{
  "text": "This is sentence one. This is sentence two.",
  "method": "sentences"
}
```

### 6. **structured_output**
Extract structured data from text using schema.

**Parameters:**
- `text` (string, required): Text to extract from
- `schema` (object, required): Schema defining fields and patterns

**Example Usage:**
```json
{
  "text": "Contact: John Doe, Email: john@example.com, Phone: 555-1234",
  "schema": {
    "name": "Contact: ([^,]+)",
    "email": "Email: ([^,]+)",
    "phone": "Phone: ([^\\s]+)"
  }
}
```

### 7. **type_convert**
Convert data between different formats.

**Parameters:**
- `data` (string, required): Data to convert
- `target_type` (string, required): Target format
- `parameters` (object, optional): Conversion parameters

**Available Formats:**
- `json`: JSON format
- `csv`: CSV format
- `yaml`: YAML format
- `xml`: XML format

**Example Usage:**
```json
{
  "data": "[{\"name\":\"John\",\"age\":25}]",
  "target_type": "csv"
}
```

## LangFlow Integration Examples

### Example 1: Document Processing Pipeline

**Flow Structure:**
1. **Chat Node**: "Process this document"
2. **store_embedding**: Store document with metadata
3. **process_text_with_llm**: Summarize the document
4. **extract_keywords**: Extract key terms
5. **Write File**: Save results

### Example 2: Similarity Search System

**Flow Structure:**
1. **Chat Node**: "Find similar documents"
2. **similarity_search**: Search for similar content
3. **process_text_with_llm**: Analyze search results
4. **structured_output**: Extract structured information
5. **Write File**: Save search results

### Example 3: Data Analysis Pipeline

**Flow Structure:**
1. **Read File**: Load CSV data
2. **dataframe_operations**: Perform analysis
3. **split_text**: Process text columns
4. **type_convert**: Convert to different format
5. **Write File**: Save results

## Database Schema

The system automatically creates the following tables:

### embeddings
```sql
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### processing_tasks
```sql
CREATE TABLE processing_tasks (
    id SERIAL PRIMARY KEY,
    task_type VARCHAR(100) NOT NULL,
    input_data TEXT,
    output_data TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

### dataframes
```sql
CREATE TABLE dataframes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    data JSONB,
    schema JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Performance Considerations

### Vector Operations
- **Embedding Generation**: Uses hash-based approach for speed
- **Similarity Search**: Leverages pgvector's efficient indexing
- **Batch Processing**: Supports bulk operations

### Memory Management
- **Connection Pooling**: Efficient database connections
- **Streaming**: Large datasets processed in chunks
- **Caching**: Results cached for repeated queries

### Scalability
- **Horizontal Scaling**: PostgreSQL clustering support
- **Indexing**: Automatic vector index creation
- **Partitioning**: Large tables can be partitioned

## Error Handling

### Common Error Scenarios
1. **Database Connection**: Connection timeout or authentication
2. **Vector Operations**: Invalid vector format or dimension mismatch
3. **Text Processing**: Encoding issues or malformed input
4. **Memory Issues**: Large dataset processing

### Error Recovery
- **Automatic Retry**: Failed operations retried automatically
- **Graceful Degradation**: Fallback to simpler processing
- **Error Logging**: Comprehensive error tracking
- **Status Monitoring**: Real-time operation status

## Security Features

### Data Protection
- **Local Storage**: All data remains on local system
- **Access Control**: Database-level security
- **Encryption**: Optional data encryption
- **Audit Trail**: Complete operation logging

### Privacy Compliance
- **GDPR Ready**: Data retention and deletion controls
- **No External Calls**: Complete privacy protection
- **Data Isolation**: Separate processing environments

## Troubleshooting

### Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d postgres

# Verify pgvector extension
psql -d postgres -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Performance Issues
```sql
-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables WHERE schemaname = 'public';

-- Analyze vector performance
EXPLAIN ANALYZE SELECT * FROM embeddings ORDER BY embedding <-> '[0.1,0.2,...]'::vector LIMIT 5;
```

### Common Solutions
1. **Slow Queries**: Add vector indexes
2. **Memory Issues**: Reduce batch sizes
3. **Connection Errors**: Check PostgreSQL configuration
4. **Encoding Issues**: Verify text encoding settings

## Advanced Usage

### Custom Embeddings
```python
# Integrate with external embedding models
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["Your text here"])
```

### Batch Operations
```python
# Process multiple documents efficiently
documents = [
    {"name": "doc1", "content": "content1"},
    {"name": "doc2", "content": "content2"}
]

for doc in documents:
    store_embedding(doc["name"], doc["content"])
```

### Custom Processing Tasks
```python
# Extend with custom processing functions
def custom_text_processor(text, parameters):
    # Your custom logic here
    return processed_result
```

## Integration with Existing Tools

### File Operations
- **Read File** → **process_text_with_llm** → **store_embedding**
- **list_files** → **similarity_search** → **structured_output**

### Data Processing
- **dataframe_operations** → **type_convert** → **Write File**
- **split_text** → **process_text_with_llm** → **structured_output**

### Workflow Automation
- **Batch Processing**: Process multiple files automatically
- **Pipeline Integration**: Chain multiple operations
- **Result Aggregation**: Combine results from multiple tools

## Best Practices

### Performance Optimization
1. **Use Indexes**: Create vector indexes for similarity search
2. **Batch Operations**: Process multiple items together
3. **Connection Management**: Reuse database connections
4. **Memory Monitoring**: Monitor memory usage for large operations

### Data Management
1. **Regular Backups**: Backup PostgreSQL database regularly
2. **Data Cleanup**: Remove old embeddings periodically
3. **Schema Evolution**: Plan for schema changes
4. **Monitoring**: Track database performance metrics

### Security
1. **Access Control**: Limit database access
2. **Data Validation**: Validate all inputs
3. **Error Handling**: Don't expose sensitive information in errors
4. **Audit Logging**: Log all operations for compliance

## Future Enhancements

### Planned Features
- **Advanced Embeddings**: Integration with more embedding models
- **Real-time Processing**: Streaming data processing
- **Distributed Processing**: Multi-node processing support
- **Advanced Analytics**: Statistical analysis tools

### Integration Opportunities
- **External APIs**: Hybrid local/external processing
- **Machine Learning**: Custom model integration
- **Visualization**: Data visualization tools
- **Workflow Automation**: Advanced workflow orchestration

This PostgreSQL+Vector LLM integration provides a powerful foundation for local AI processing, significantly reducing dependency on external APIs while maintaining high performance and scalability. 