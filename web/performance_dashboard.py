#!/usr/bin/env python3
"""
Performance Monitoring Dashboard for LangFlow Connect MVP
Real-time performance metrics and monitoring
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import threading
import queue

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"
REFRESH_INTERVAL = 30  # seconds

# Page configuration
st.set_page_config(
    page_title="Performance Dashboard - LangFlow Connect MVP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .error-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .success-card {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
    .header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def fetch_api_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        headers = {"X-API-Key": API_KEY}
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def get_health_color(status):
    """Get color for health status"""
    colors = {
        "healthy": "green",
        "warning": "orange", 
        "error": "red",
        "critical": "darkred"
    }
    return colors.get(status, "gray")

def display_metric_card(title, value, subtitle="", color="blue"):
    """Display a metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="color: {color}; margin: 0;">{title}</h3>
        <h2 style="margin: 0.5rem 0;">{value}</h2>
        <p style="margin: 0; color: #666;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def display_alert_card(alert):
    """Display an alert card"""
    severity_colors = {
        "critical": "#dc3545",
        "error": "#fd7e14", 
        "warning": "#ffc107",
        "info": "#17a2b8"
    }
    color = severity_colors.get(alert['severity'], "#6c757d")
    
    st.markdown(f"""
    <div class="alert-card" style="border-left-color: {color};">
        <h4 style="margin: 0; color: {color};">{alert['type'].replace('_', ' ').title()}</h4>
        <p style="margin: 0.5rem 0;"><strong>Tool:</strong> {alert['tool']}</p>
        <p style="margin: 0.5rem 0;">{alert['message']}</p>
        <small style="color: #666;">{alert['timestamp']}</small>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="header">
        <h1>📊 Performance Monitoring Dashboard</h1>
        <p>LangFlow Connect MVP - Real-time Performance Metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 10, 60, 30)
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # API Status
    st.sidebar.subheader("🔗 API Status")
    health_data = fetch_api_data("/health")
    if health_data:
        st.sidebar.success("✅ API Connected")
        st.sidebar.info(f"Version: {health_data.get('version', 'Unknown')}")
    else:
        st.sidebar.error("❌ API Disconnected")
        return
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch performance data
    dashboard_data = fetch_api_data("/performance/dashboard")
    if not dashboard_data:
        st.error("Unable to fetch performance data")
        return
    
    dashboard = dashboard_data.get('dashboard', {})
    overview = dashboard.get('overview', {})
    system_metrics = dashboard.get('system_metrics', {})
    alerts = dashboard.get('alerts', {})
    
    # Overview metrics
    with col1:
        display_metric_card(
            "Total Requests",
            f"{overview.get('total_requests', 0):,}",
            "All time requests"
        )
    
    with col2:
        success_rate = overview.get('overall_success_rate', 0)
        color = "green" if success_rate >= 95 else "orange" if success_rate >= 90 else "red"
        display_metric_card(
            "Success Rate",
            f"{success_rate:.1f}%",
            "Overall success rate",
            color
        )
    
    with col3:
        uptime_hours = overview.get('uptime_hours', 0)
        display_metric_card(
            "Uptime",
            f"{uptime_hours:.1f}h",
            "System uptime"
        )
    
    with col4:
        system_health = overview.get('system_health', 'unknown')
        health_color = get_health_color(system_health)
        display_metric_card(
            "System Health",
            system_health.title(),
            "Overall system status",
            health_color
        )
    
    st.markdown("---")
    
    # System Resources
    st.subheader("💻 System Resources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cpu_usage = system_metrics.get('cpu_usage', 0)
        cpu_color = "green" if cpu_usage < 70 else "orange" if cpu_usage < 90 else "red"
        display_metric_card(
            "CPU Usage",
            f"{cpu_usage:.1f}%",
            "Current CPU utilization",
            cpu_color
        )
    
    with col2:
        memory_usage = system_metrics.get('memory_usage', 0)
        memory_color = "green" if memory_usage < 70 else "orange" if memory_usage < 90 else "red"
        display_metric_card(
            "Memory Usage",
            f"{memory_usage:.1f}%",
            "Current memory utilization",
            memory_color
        )
    
    with col3:
        disk_usage = system_metrics.get('disk_usage', 0)
        disk_color = "green" if disk_usage < 80 else "orange" if disk_usage < 95 else "red"
        display_metric_card(
            "Disk Usage",
            f"{disk_usage:.1f}%",
            "Current disk utilization",
            disk_color
        )
    
    st.markdown("---")
    
    # Alerts Section
    st.subheader("🚨 Performance Alerts")
    
    alert_count = alerts.get('count', 0)
    if alert_count == 0:
        st.success("✅ No active alerts - System performing well!")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Critical", alerts.get('critical', 0))
        with col2:
            st.metric("Errors", alerts.get('errors', 0))
        with col3:
            st.metric("Warnings", alerts.get('warnings', 0))
        
        # Fetch detailed alerts
        alerts_data = fetch_api_data("/performance/alerts")
        if alerts_data and alerts_data.get('alerts'):
            for alert in alerts_data['alerts']:
                display_alert_card(alert)
    
    st.markdown("---")
    
    # Tool Performance
    st.subheader("🛠️ Tool Performance")
    
    top_tools = dashboard.get('top_tools', [])
    if top_tools:
        # Create DataFrame for visualization
        df = pd.DataFrame(top_tools)
        
        # Response time chart
        fig_response = px.bar(
            df, 
            x='tool_name', 
            y='avg_response_time',
            title='Average Response Time by Tool',
            labels={'avg_response_time': 'Response Time (ms)', 'tool_name': 'Tool'},
            color='avg_response_time',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig_response, use_container_width=True)
        
        # Success rate chart
        fig_success = px.bar(
            df,
            x='tool_name',
            y='success_rate', 
            title='Success Rate by Tool',
            labels={'success_rate': 'Success Rate (%)', 'tool_name': 'Tool'},
            color='success_rate',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_success, use_container_width=True)
        
        # Tool usage table
        st.subheader("📋 Detailed Tool Metrics")
        st.dataframe(
            df[['tool_name', 'total_requests', 'success_rate', 'avg_response_time', 'error_count']],
            use_container_width=True
        )
    
    # Problematic tools
    problematic_tools = dashboard.get('problematic_tools', [])
    if problematic_tools:
        st.subheader("⚠️ Tools Requiring Attention")
        for tool in problematic_tools:
            issues = []
            if tool['success_rate'] < 90:
                issues.append(f"Low success rate: {tool['success_rate']:.1f}%")
            if tool['avg_response_time'] > 2000:
                issues.append(f"Slow response: {tool['avg_response_time']:.0f}ms")
            
            st.warning(f"**{tool['tool_name']}**: {', '.join(issues)}")
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
