import streamlit as st

st.title("🚀 LangFlow Connect MCP Server Demo")
st.markdown("Capstone Project - Basic MCP Server Demo")

st.header("Available Tools")
st.markdown("""
- **ping**: Test server connectivity
- **read_file**: Read file contents
- **list_files**: List directory contents
- **get_system_status**: Get server status
- **analyze_code**: Analyze code files
""")

st.header("Quick Test")
if st.button("Test Ping"):
    st.success("✅ Server is running!")
