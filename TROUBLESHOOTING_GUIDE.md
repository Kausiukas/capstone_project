# LangFlow MCP Connector Troubleshooting Guide

## 🚨 Quick Diagnosis

### 1. Run System Diagnostic
```bash
python system_stability_diagnostic.py
```

### 2. Check Python Version Compatibility
```bash
python --version
```
**Required**: Python 3.7+ (Python 3.8+ recommended)

### 3. Verify MCP Server Health
```bash
python test_list_files_tool.py
```

## 🔧 Common Issues & Solutions

### Issue 1: LangFlow Python Version Lagging

**Symptoms:**
- Slow response times in LangFlow
- MCP tools not loading properly
- Timeout errors

**Solutions:**

#### A. Optimize MCP Server Performance
```bash
# Run stability enhancement
python stability_enhancement.py

# Use optimized startup script
python start_mcp_server.py
```

#### B. Memory Optimization
- **Reduce batch sizes**: Set `batch_size` to 10-20 instead of 50
- **Limit directory depth**: Use `max_depth: 1` for large directories
- **Enable caching**: Set `use_cache: true`

#### C. Network Optimization
- **Increase timeouts**: Set connection timeout to 60 seconds
- **Enable keepalive**: Maintain persistent connections
- **Use compression**: Enable gzip compression for large responses

### Issue 2: MCP Server Connection Problems

**Symptoms:**
- "Failed to load tools from MCP server"
- Connection timeout errors
- Server not responding

**Solutions:**

#### A. Check Server Status
```bash
# Test MCP server directly
python mcp_langflow_connector_simple.py
```

#### B. Verify Configuration
```json
{
  "server": {
    "name": "langflow-connect-simple",
    "version": "1.0.0",
    "protocol_version": "2024-11-05"
  }
}
```

#### C. Restart with Monitoring
```bash
# Use reliable startup script
python start_mcp_server.py

# Monitor system health
python simple_stability_monitor.py
```

### Issue 3: File Listing Performance Issues

**Symptoms:**
- Slow directory listing
- Memory usage spikes
- Timeout errors on large directories

**Solutions:**

#### A. Use Metadata-Only Listing
```python
# The updated list_files tool now shows only metadata
# No file content is loaded, improving performance significantly
```

#### B. Implement Pagination
```python
# Use batch_size and offset parameters
{
  "directory": ".",
  "batch_size": 20,
  "offset": 0
}
```

#### C. Filter by File Type
```python
# Only list specific file types
{
  "directory": ".",
  "file_types": [".py", ".md"]
}
```

### Issue 4: System Resource Exhaustion

**Symptoms:**
- High memory usage
- CPU spikes
- System becomes unresponsive

**Solutions:**

#### A. Monitor System Resources
```bash
# Run continuous monitoring
python simple_stability_monitor.py
```

#### B. Set Resource Limits
```python
# In MCP server configuration
{
  "performance": {
    "max_memory_mb": 50,
    "batch_size_limit": 20,
    "cache_size_limit": 100
  }
}
```

#### C. Optimize File Operations
- Use async I/O operations
- Implement proper garbage collection
- Limit concurrent operations

## 🛠️ Advanced Troubleshooting

### Performance Profiling

#### 1. Memory Profiling
```bash
# Install memory profiler
pip install memory-profiler

# Profile MCP server
python -m memory_profiler mcp_langflow_connector_simple.py
```

#### 2. CPU Profiling
```bash
# Install cProfile
python -m cProfile -o profile.stats mcp_langflow_connector_simple.py

# Analyze results
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

### Network Diagnostics

#### 1. Check MCP Protocol
```bash
# Test MCP protocol compliance
python -c "
import json
request = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'initialize',
    'params': {}
}
print(json.dumps(request))
"
```

#### 2. Test Connection Stability
```bash
# Monitor network connectivity
ping localhost
netstat -an | grep 7860  # LangFlow default port
```

### Log Analysis

#### 1. Enable Detailed Logging
```python
# In mcp_langflow_connector_simple.py
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mcp_server.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. Analyze Log Files
```bash
# Check for errors
grep "ERROR" logs/mcp_server.log

# Check performance
grep "processing_time" logs/mcp_server.log
```

## 🔄 Recovery Procedures

### Automatic Recovery

#### 1. Use Startup Script
```bash
# Automatically restarts on failure
python start_mcp_server.py
```

#### 2. Monitor and Alert
```bash
# Continuous health monitoring
python simple_stability_monitor.py
```

### Manual Recovery

#### 1. Restart MCP Server
```bash
# Kill existing process
pkill -f mcp_langflow_connector_simple.py

# Restart with monitoring
python start_mcp_server.py
```

#### 2. Clear Cache
```bash
# Remove cached data
rm -rf cache/file_listings/*

# Restart server
python mcp_langflow_connector_simple.py
```

#### 3. Reset Configuration
```bash
# Backup current config
cp config/langflow_config.py config/langflow_config.py.backup

# Restore default config
python stability_enhancement.py
```

## 📊 Performance Optimization

### 1. Memory Management
- **Limit batch sizes**: 10-20 files per batch
- **Enable garbage collection**: Force GC after large operations
- **Use streaming**: Process files incrementally

### 2. File Operations
- **Async I/O**: Use asyncio for file operations
- **Caching**: Cache directory listings for 5 minutes
- **Compression**: Compress large responses

### 3. Network Optimization
- **Connection pooling**: Reuse connections
- **Timeout management**: Set appropriate timeouts
- **Retry logic**: Implement exponential backoff

## 🎯 Best Practices

### 1. Regular Maintenance
```bash
# Weekly system check
python system_stability_diagnostic.py

# Monthly performance review
python simple_stability_monitor.py
```

### 2. Monitoring Setup
```bash
# Set up continuous monitoring
nohup python simple_stability_monitor.py > monitoring.log 2>&1 &
```

### 3. Backup Strategy
```bash
# Backup configuration
cp config/* config/backup/

# Backup logs
cp logs/* logs/backup/
```

## 🆘 Emergency Procedures

### Critical Issues

#### 1. Server Not Responding
```bash
# Emergency restart
pkill -f mcp_langflow_connector_simple.py
sleep 5
python start_mcp_server.py
```

#### 2. High Memory Usage
```bash
# Force garbage collection
python -c "import gc; gc.collect()"

# Restart with reduced limits
export MCP_MAX_MEMORY=25
python mcp_langflow_connector_simple.py
```

#### 3. LangFlow Integration Failure
```bash
# Reset MCP connection
# 1. Stop LangFlow
# 2. Clear MCP cache
# 3. Restart MCP server
# 4. Restart LangFlow
```

## 📞 Support Information

### Diagnostic Files
- `stability_report.json` - System stability report
- `enhancement_summary.json` - Optimization results
- `logs/stability_monitoring.json` - Continuous monitoring data

### Key Metrics to Monitor
- Memory usage: < 80%
- CPU usage: < 70%
- Response time: < 5 seconds
- Error rate: < 1%

### Contact Information
- Check logs in `logs/` directory
- Review diagnostic reports
- Monitor system health continuously

---

**Remember**: The updated `list_files` tool is optimized for metadata-only operations, significantly improving performance and stability. Always use the latest version and monitor system health regularly. 