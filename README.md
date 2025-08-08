# LangFlow Connect MVP - Integrated Dashboard

## 🎯 Project Overview

This is a **Capstone Project** demonstration of the LangFlow Connect MCP (Model Context Protocol) server with integrated Content Preview and Performance Monitoring systems.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run MCP server
python src/mcp_server_enhanced_tools.py

# Run integrated dashboard
streamlit run streamlit_app_integrated.py
```

## 🛠 Features

### Core Tools
- **5 Core Tools**: ping, read_file, list_files, get_system_status, analyze_code
- **Universal File Access**: Local, GitHub, and HTTP file support
- **Web Interface**: Streamlit-based unified dashboard
- **API Access**: RESTful API for programmatic access

### Content Preview System
- **Syntax Highlighting**: Support for 20+ programming languages
- **Markdown Rendering**: Full markdown to HTML conversion
- **Image Preview**: Base64 encoding for inline display
- **Batch Processing**: Preview multiple files simultaneously
- **File Analysis**: Automatic type detection and capabilities

### Performance Monitoring
- **Real-time Metrics**: Response times, success rates, error counts
- **System Monitoring**: CPU, memory, disk usage tracking
- **Performance Alerts**: Automated alerting for issues
- **Health Monitoring**: Comprehensive system health checks
- **Tool-specific Metrics**: Individual tool performance tracking

## 📊 Dashboard Sections

1. **🏠 Dashboard** - Overview and quick actions
2. **🛠️ Tool Testing** - Interactive tool execution
3. **👁️ Content Preview** - File preview and analysis
4. **📊 Performance Monitoring** - Real-time metrics and alerts
5. **📚 API Docs** - Complete API documentation
6. **🔧 System Status** - System health and configuration

## 🔧 Configuration

The dashboard automatically connects to the deployed API at:
`https://capstone-project-api-jg3n.onrender.com`

You can change the API URL in the sidebar configuration.

## 📄 License

MIT License

## 🎯 Capstone Project Status

✅ **Complete** - All systems integrated and functional
- Core MCP tools operational
- Content Preview System active
- Performance Monitoring active
- Unified dashboard deployed
- Universal file access working
- Real-time metrics collection
- Comprehensive error handling
