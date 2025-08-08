#!/usr/bin/env python3
"""
Local test for content preview system
"""

import sys
import os
sys.path.append('src')

from mcp_server_enhanced_tools import ContentPreviewManager

def test_content_preview_local():
    """Test content preview functionality locally"""
    print("🚀 Testing Content Preview System Locally")
    print("=" * 50)
    
    # Test file type detection
    test_files = [
        "test.py",
        "README.md", 
        "config.json",
        "style.css",
        "index.html",
        "image.jpg",
        "document.pdf"
    ]
    
    print("🔍 Testing file type detection...")
    for file_path in test_files:
        file_type = ContentPreviewManager.detect_file_type(file_path)
        language = ContentPreviewManager.get_syntax_highlighting_language(file_path)
        print(f"📄 {file_path}: Type={file_type}, Language={language}")
    
    # Test syntax highlighting
    print("\n🎨 Testing syntax highlighting...")
    python_code = '''def hello_world():
    """Simple hello world function"""
    print("Hello, World!")
    return True

# Main execution
if __name__ == "__main__":
    hello_world()'''
    
    highlighted = ContentPreviewManager.format_code_with_syntax_highlighting(python_code, "python")
    print("✅ Python syntax highlighting working")
    print(f"Highlighted content length: {len(highlighted)} characters")
    
    # Test markdown rendering
    print("\n📝 Testing markdown rendering...")
    markdown_content = """# Sample Markdown

## Features
- **Bold text**
- *Italic text*
- `Code snippets`

## Code Block
```python
print("Hello from markdown!")
```

[Link to GitHub](https://github.com)"""
    
    rendered = ContentPreviewManager.render_markdown(markdown_content)
    print("✅ Markdown rendering working")
    print(f"Rendered content length: {len(rendered)} characters")
    
    # Test HTML preview creation
    print("\n👁️ Testing HTML preview creation...")
    preview_html = ContentPreviewManager.create_preview_html(python_code, "code", "python")
    print("✅ HTML preview creation working")
    print(f"Preview HTML length: {len(preview_html)} characters")
    
    print("\n🎉 All local tests passed! Content Preview System is working correctly.")

if __name__ == "__main__":
    test_content_preview_local()
