#!/usr/bin/env python3
"""
LangFlow Connect MVP - Monitoring Dashboard
Web-based dashboard for visualizing system status and health metrics.
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from typing import Dict, List, Any
import requests

# Configuration
API_BASE_URL = "https://capstone-project-api-jg3n.onrender.com"
API_KEY = "demo_key_123"

class MonitoringDashboard:
    def __init__(self):
        self.api_url = API_BASE_URL
        self.headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
    
    def load_monitoring_data(self, filename: str = None) -> Dict[str, Any]:
        """Load monitoring data from file"""
        if filename is None:
            # Find the most recent monitoring data file
            monitoring_files = [f for f in os.listdir('.') if f.startswith('monitoring_data_') and f.endswith('.json')]
            if not monitoring_files:
                return {}
            filename = max(monitoring_files)
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading monitoring data: {str(e)}")
            return {}
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current system status by making live API calls"""
        try:
            # Check health endpoint
            health_start = datetime.now()
            health_response = requests.get(f"{self.api_url}/health", timeout=10)
            health_time = (datetime.now() - health_start).total_seconds() * 1000
            
            # Check tools endpoint
            tools_start = datetime.now()
            tools_response = requests.get(f"{self.api_url}/tools/list", headers=self.headers, timeout=10)
            tools_time = (datetime.now() - tools_start).total_seconds() * 1000
            
            # Test tool execution
            tool_start = datetime.now()
            tool_payload = {'name': 'ping', 'arguments': {}}
            tool_response = requests.post(
                f"{self.api_url}/api/v1/tools/call",
                headers=self.headers,
                data=json.dumps(tool_payload),
                timeout=30
            )
            tool_time = (datetime.now() - tool_start).total_seconds() * 1000
            
            # Calculate metrics
            health_success = health_response.status_code == 200
            tools_success = tools_response.status_code == 200
            tool_success = tool_response.status_code == 200
            
            successful_checks = sum([health_success, tools_success, tool_success])
            total_checks = 3
            success_rate = (successful_checks / total_checks) * 100
            
            avg_response_time = (health_time + tools_time + tool_time) / 3
            
            return {
                'status': 'healthy' if success_rate == 100 else 'degraded' if success_rate > 50 else 'down',
                'success_rate': success_rate,
                'average_response_time': avg_response_time,
                'health_check': {
                    'success': health_success,
                    'response_time': health_time,
                    'status_code': health_response.status_code
                },
                'tools_check': {
                    'success': tools_success,
                    'response_time': tools_time,
                    'status_code': tools_response.status_code
                },
                'tool_execution': {
                    'success': tool_success,
                    'response_time': tool_time,
                    'status_code': tool_response.status_code
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'success_rate': 0,
                'average_response_time': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def create_response_time_chart(self, health_checks: List[Dict[str, Any]]) -> go.Figure:
        """Create response time chart"""
        if not health_checks:
            return go.Figure()
        
        df = pd.DataFrame(health_checks)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        
        # Add response time line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['response_time'],
            mode='lines+markers',
            name='Response Time (ms)',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
        
        # Add success/failure indicators
        success_df = df[df['success'] == True]
        failure_df = df[df['success'] == False]
        
        if not success_df.empty:
            fig.add_trace(go.Scatter(
                x=success_df['timestamp'],
                y=success_df['response_time'],
                mode='markers',
                name='Successful',
                marker=dict(color='green', size=8, symbol='circle')
            ))
        
        if not failure_df.empty:
            fig.add_trace(go.Scatter(
                x=failure_df['timestamp'],
                y=failure_df['response_time'],
                mode='markers',
                name='Failed',
                marker=dict(color='red', size=8, symbol='x')
            ))
        
        fig.update_layout(
            title='Response Time Over Time',
            xaxis_title='Time',
            yaxis_title='Response Time (ms)',
            hovermode='x unified'
        )
        
        return fig
    
    def create_success_rate_chart(self, health_checks: List[Dict[str, Any]]) -> go.Figure:
        """Create success rate chart"""
        if not health_checks:
            return go.Figure()
        
        df = pd.DataFrame(health_checks)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Group by hour and calculate success rate
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_success = df.groupby('hour')['success'].agg(['count', 'sum']).reset_index()
        hourly_success['success_rate'] = (hourly_success['sum'] / hourly_success['count']) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=hourly_success['hour'],
            y=hourly_success['success_rate'],
            name='Success Rate (%)',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title='Success Rate by Hour',
            xaxis_title='Hour',
            yaxis_title='Success Rate (%)',
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    def create_endpoint_performance_chart(self, health_checks: List[Dict[str, Any]]) -> go.Figure:
        """Create endpoint performance comparison chart"""
        if not health_checks:
            return go.Figure()
        
        df = pd.DataFrame(health_checks)
        
        # Group by endpoint and calculate average response time
        endpoint_performance = df.groupby('endpoint')['response_time'].agg(['mean', 'count']).reset_index()
        
        fig = go.Figure(data=[
            go.Bar(
                x=endpoint_performance['endpoint'],
                y=endpoint_performance['mean'],
                text=[f"{val:.1f}ms" for val in endpoint_performance['mean']],
                textposition='auto',
                name='Average Response Time'
            )
        ])
        
        fig.update_layout(
            title='Endpoint Performance Comparison',
            xaxis_title='Endpoint',
            yaxis_title='Average Response Time (ms)'
        )
        
        return fig

def main():
    """Main dashboard function"""
    st.set_page_config(
        page_title="LangFlow Connect - Monitoring Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 LangFlow Connect MVP - Monitoring Dashboard")
    st.markdown("**Real-time system monitoring and health metrics**")
    
    # Initialize dashboard
    dashboard = MonitoringDashboard()
    
    # Sidebar
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Data source selection
    data_source = st.sidebar.selectbox(
        "Data Source",
        ["Live Status", "Historical Data"],
        help="Choose between live API status or historical monitoring data"
    )
    
    if data_source == "Live Status":
        # Live status section
        st.header("🔴 Live System Status")
        
        # Get current status
        with st.spinner("Checking system status..."):
            current_status = dashboard.get_current_status()
        
        # Status overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = {
                'healthy': '🟢',
                'degraded': '🟡',
                'down': '🔴',
                'error': '🔴'
            }.get(current_status.get('status', 'unknown'), '⚪')
            
            st.metric(
                "System Status",
                f"{status_color} {current_status.get('status', 'unknown').title()}"
            )
        
        with col2:
            st.metric(
                "Success Rate",
                f"{current_status.get('success_rate', 0):.1f}%"
            )
        
        with col3:
            st.metric(
                "Avg Response Time",
                f"{current_status.get('average_response_time', 0):.1f}ms"
            )
        
        with col4:
            st.metric(
                "Last Check",
                datetime.now().strftime("%H:%M:%S")
            )
        
        # Detailed status
        st.subheader("📋 Detailed Status")
        
        if 'error' in current_status:
            st.error(f"Error checking system status: {current_status['error']}")
        else:
            # Health check details
            col1, col2, col3 = st.columns(3)
            
            with col1:
                health_check = current_status.get('health_check', {})
                st.metric(
                    "Health Endpoint",
                    f"{'✅' if health_check.get('success') else '❌'} {health_check.get('response_time', 0):.1f}ms"
                )
            
            with col2:
                tools_check = current_status.get('tools_check', {})
                st.metric(
                    "Tools Endpoint",
                    f"{'✅' if tools_check.get('success') else '❌'} {tools_check.get('response_time', 0):.1f}ms"
                )
            
            with col3:
                tool_execution = current_status.get('tool_execution', {})
                st.metric(
                    "Tool Execution",
                    f"{'✅' if tool_execution.get('success') else '❌'} {tool_execution.get('response_time', 0):.1f}ms"
                )
        
        # Performance indicators
        st.subheader("📈 Performance Indicators")
        
        # Create performance gauge
        success_rate = current_status.get('success_rate', 0)
        response_time = current_status.get('average_response_time', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Success rate gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=success_rate,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Success Rate (%)"},
                delta={'reference': 95},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 80], 'color': "lightgray"},
                        {'range': [80, 95], 'color': "yellow"},
                        {'range': [95, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            # Response time gauge
            fig_response = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=response_time,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Avg Response Time (ms)"},
                delta={'reference': 200},
                gauge={
                    'axis': {'range': [None, 500]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 200], 'color': "green"},
                        {'range': [200, 300], 'color': "yellow"},
                        {'range': [300, 500], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 400
                    }
                }
            ))
            fig_response.update_layout(height=300)
            st.plotly_chart(fig_response, use_container_width=True)
    
    else:
        # Historical data section
        st.header("📚 Historical Monitoring Data")
        
        # Load monitoring data
        monitoring_data = dashboard.load_monitoring_data()
        
        if not monitoring_data:
            st.warning("No historical monitoring data found. Run the monitoring system first.")
            return
        
        # System status overview
        system_status = monitoring_data.get('system_status', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall Status",
                system_status.get('status', 'unknown').title()
            )
        
        with col2:
            st.metric(
                "Success Rate",
                f"{system_status.get('success_rate', 0):.1f}%"
            )
        
        with col3:
            st.metric(
                "Avg Response Time",
                f"{system_status.get('average_response_time', 0):.1f}ms"
            )
        
        with col4:
            st.metric(
                "Uptime",
                f"{system_status.get('uptime_percentage', 0):.1f}%"
            )
        
        # Charts
        health_checks = monitoring_data.get('health_checks', [])
        
        if health_checks:
            st.subheader("📊 Historical Charts")
            
            # Response time chart
            fig_response = dashboard.create_response_time_chart(health_checks)
            st.plotly_chart(fig_response, use_container_width=True)
            
            # Success rate chart
            fig_success = dashboard.create_success_rate_chart(health_checks)
            st.plotly_chart(fig_success, use_container_width=True)
            
            # Endpoint performance chart
            fig_endpoint = dashboard.create_endpoint_performance_chart(health_checks)
            st.plotly_chart(fig_endpoint, use_container_width=True)
        
        # Alerts section
        alerts = monitoring_data.get('alerts', [])
        if alerts:
            st.subheader("🚨 Alerts")
            
            for alert in alerts[-10:]:  # Show last 10 alerts
                severity_color = {
                    'critical': '🔴',
                    'warning': '🟡',
                    'info': '🔵'
                }.get(alert.get('severity', 'info'), '⚪')
                
                st.write(f"{severity_color} **{alert.get('type', 'Unknown')}** - {alert.get('message', 'No message')}")
                st.write(f"*{alert.get('timestamp', 'Unknown time')}*")
                st.divider()
    
    # Footer
    st.markdown("---")
    st.markdown("*Monitoring Dashboard - LangFlow Connect MVP*")

if __name__ == "__main__":
    main()
