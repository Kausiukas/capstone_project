#!/usr/bin/env python3
"""
LangFlow Connect MVP - Tool Configuration Optimizer
This script analyzes test results and optimizes tool configurations for better performance.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import re

class ToolConfigurationOptimizer:
    def __init__(self):
        self.optimization_rules = {
            'file_path_handling': {
                'issues': ['path not found', 'no such file', 'file not found'],
                'solutions': [
                    'Implement cross-platform path normalization',
                    'Add path validation before execution',
                    'Provide better error messages for invalid paths'
                ]
            },
            'performance': {
                'thresholds': {
                    'response_time': 500,  # ms
                    'success_rate': 0.95,  # 95%
                    'error_rate': 0.05     # 5%
                },
                'optimizations': [
                    'Implement result caching',
                    'Add connection pooling',
                    'Optimize database queries',
                    'Use async processing for long operations'
                ]
            },
            'reliability': {
                'error_patterns': {
                    'timeout': 'Request timeout',
                    'connection': 'Connection error',
                    'authentication': 'Authentication failed',
                    'validation': 'Validation error'
                },
                'improvements': [
                    'Add retry mechanisms',
                    'Implement circuit breaker pattern',
                    'Add request validation',
                    'Improve error handling'
                ]
            }
        }
    
    def analyze_test_report(self, report_file: str) -> Dict[str, Any]:
        """Analyze test report and generate optimization recommendations"""
        print(f"📊 Analyzing test report: {report_file}")
        
        try:
            with open(report_file, 'r') as f:
                report = json.load(f)
        except FileNotFoundError:
            print(f"❌ Report file not found: {report_file}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in report file: {report_file}")
            return {}
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'report_file': report_file,
            'issues_found': [],
            'optimizations': [],
            'configuration_changes': [],
            'priority_actions': []
        }
        
        # Analyze error patterns
        if 'error_log' in report:
            analysis['issues_found'].extend(self._analyze_errors(report['error_log']))
        
        # Analyze performance data
        if 'performance_data' in report:
            analysis['optimizations'].extend(self._analyze_performance(report['performance_data']))
        
        # Analyze tool-specific issues
        if 'results' in report:
            analysis['issues_found'].extend(self._analyze_tool_results(report['results']))
        
        # Generate configuration changes
        analysis['configuration_changes'] = self._generate_configuration_changes(analysis['issues_found'])
        
        # Prioritize actions
        analysis['priority_actions'] = self._prioritize_actions(analysis)
        
        return analysis
    
    def _analyze_errors(self, error_log: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze error patterns and categorize issues"""
        issues = []
        
        # Group errors by tool
        tool_errors = {}
        for error in error_log:
            tool = error.get('tool', 'unknown')
            if tool not in tool_errors:
                tool_errors[tool] = []
            tool_errors[tool].append(error)
        
        # Analyze each tool's errors
        for tool, errors in tool_errors.items():
            error_messages = [e.get('error', '') for e in errors]
            
            # Check for file path issues
            path_errors = [msg for msg in error_messages if any(issue in msg.lower() for issue in self.optimization_rules['file_path_handling']['issues'])]
            if path_errors:
                issues.append({
                    'category': 'file_path_handling',
                    'tool': tool,
                    'issue': 'File path handling problems',
                    'count': len(path_errors),
                    'examples': path_errors[:3],
                    'priority': 'high'
                })
            
            # Check for timeout issues
            timeout_errors = [msg for msg in error_messages if 'timeout' in msg.lower()]
            if timeout_errors:
                issues.append({
                    'category': 'performance',
                    'tool': tool,
                    'issue': 'Request timeouts',
                    'count': len(timeout_errors),
                    'examples': timeout_errors[:3],
                    'priority': 'high'
                })
            
            # Check for connection issues
            connection_errors = [msg for msg in error_messages if 'connection' in msg.lower()]
            if connection_errors:
                issues.append({
                    'category': 'reliability',
                    'tool': tool,
                    'issue': 'Connection problems',
                    'count': len(connection_errors),
                    'examples': connection_errors[:3],
                    'priority': 'critical'
                })
        
        return issues
    
    def _analyze_performance(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze performance data and identify optimization opportunities"""
        optimizations = []
        
        for test_name, data in performance_data.items():
            if 'average_response_time' in data:
                response_time = data['average_response_time']
                if response_time > self.optimization_rules['performance']['thresholds']['response_time']:
                    optimizations.append({
                        'category': 'performance',
                        'test': test_name,
                        'issue': f'High response time: {response_time:.2f}ms',
                        'target': f'<{self.optimization_rules["performance"]["thresholds"]["response_time"]}ms',
                        'priority': 'medium'
                    })
            
            if 'success_rate' in data:
                success_rate = data['success_rate']
                if success_rate < self.optimization_rules['performance']['thresholds']['success_rate']:
                    optimizations.append({
                        'category': 'reliability',
                        'test': test_name,
                        'issue': f'Low success rate: {success_rate:.1%}',
                        'target': f'>{self.optimization_rules["performance"]["thresholds"]["success_rate"]:.1%}',
                        'priority': 'high'
                    })
        
        return optimizations
    
    def _analyze_tool_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze individual tool test results"""
        issues = []
        
        for tool_name, result in results.items():
            if isinstance(result, dict):
                # Check for specific tool issues
                if tool_name == 'list_files_tool':
                    issues.extend(self._analyze_list_files_issues(result))
                elif tool_name == 'read_file_tool':
                    issues.extend(self._analyze_read_file_issues(result))
                elif tool_name == 'analyze_code_tool':
                    issues.extend(self._analyze_analyze_code_issues(result))
        
        return issues
    
    def _analyze_list_files_issues(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze list_files tool specific issues"""
        issues = []
        
        if isinstance(result, dict):
            for path, path_result in result.items():
                if isinstance(path_result, dict) and not path_result.get('success', True):
                    # Check if it's a path-related error
                    error = path_result.get('result', {}).get('error', '')
                    if any(issue in error.lower() for issue in self.optimization_rules['file_path_handling']['issues']):
                        issues.append({
                            'category': 'file_path_handling',
                            'tool': 'list_files',
                            'issue': f'Path not accessible: {path}',
                            'error': error,
                            'priority': 'medium'
                        })
        
        return issues
    
    def _analyze_read_file_issues(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze read_file tool specific issues"""
        issues = []
        
        if isinstance(result, dict):
            for file_path, file_result in result.items():
                if isinstance(file_result, dict) and not file_result.get('success', True):
                    error = file_result.get('result', {}).get('error', '')
                    if 'not found' in error.lower():
                        issues.append({
                            'category': 'file_path_handling',
                            'tool': 'read_file',
                            'issue': f'File not found: {file_path}',
                            'error': error,
                            'priority': 'medium'
                        })
        
        return issues
    
    def _analyze_analyze_code_issues(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze analyze_code tool specific issues"""
        issues = []
        
        if isinstance(result, dict):
            for file_path, file_result in result.items():
                if isinstance(file_result, dict) and not file_result.get('success', True):
                    error = file_result.get('result', {}).get('error', '')
                    if 'not found' in error.lower():
                        issues.append({
                            'category': 'file_path_handling',
                            'tool': 'analyze_code',
                            'issue': f'Code file not found: {file_path}',
                            'error': error,
                            'priority': 'medium'
                        })
        
        return issues
    
    def _generate_configuration_changes(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific configuration changes based on issues"""
        changes = []
        
        for issue in issues:
            if issue['category'] == 'file_path_handling':
                changes.append({
                    'type': 'code_improvement',
                    'target': 'src/mcp_server_http.py',
                    'description': 'Improve file path handling',
                    'changes': [
                        'Add path normalization for cross-platform compatibility',
                        'Implement better error messages for invalid paths',
                        'Add path validation before file operations'
                    ],
                    'priority': issue.get('priority', 'medium')
                })
            
            elif issue['category'] == 'performance':
                changes.append({
                    'type': 'optimization',
                    'target': 'src/mcp_server_http.py',
                    'description': 'Optimize response times',
                    'changes': [
                        'Add result caching for frequently accessed data',
                        'Implement async processing for long operations',
                        'Add connection pooling for external services'
                    ],
                    'priority': issue.get('priority', 'medium')
                })
            
            elif issue['category'] == 'reliability':
                changes.append({
                    'type': 'reliability_improvement',
                    'target': 'src/mcp_server_http.py',
                    'description': 'Improve error handling and reliability',
                    'changes': [
                        'Add retry mechanisms for failed requests',
                        'Implement circuit breaker pattern',
                        'Add comprehensive error logging'
                    ],
                    'priority': issue.get('priority', 'high')
                })
        
        return changes
    
    def _prioritize_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize actions based on impact and effort"""
        actions = []
        
        # Critical issues first
        critical_issues = [issue for issue in analysis['issues_found'] if issue.get('priority') == 'critical']
        for issue in critical_issues:
            actions.append({
                'action': f'Fix {issue["issue"]}',
                'priority': 'critical',
                'effort': 'high',
                'impact': 'critical',
                'timeline': 'immediate'
            })
        
        # High priority issues
        high_priority_issues = [issue for issue in analysis['issues_found'] if issue.get('priority') == 'high']
        for issue in high_priority_issues:
            actions.append({
                'action': f'Address {issue["issue"]}',
                'priority': 'high',
                'effort': 'medium',
                'impact': 'high',
                'timeline': 'this week'
            })
        
        # Medium priority optimizations
        medium_optimizations = [opt for opt in analysis['optimizations'] if opt.get('priority') == 'medium']
        for opt in medium_optimizations:
            actions.append({
                'action': f'Optimize {opt["issue"]}',
                'priority': 'medium',
                'effort': 'low',
                'impact': 'medium',
                'timeline': 'next week'
            })
        
        return actions
    
    def generate_optimization_report(self, analysis: Dict[str, Any], output_file: str = None) -> str:
        """Generate a comprehensive optimization report"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"optimization_report_{timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 🚀 LangFlow Connect MVP - Tool Optimization Report\n\n")
            f.write(f"**Generated:** {analysis['timestamp']}\n")
            f.write(f"**Source Report:** {analysis['report_file']}\n\n")
            
            # Summary
            f.write("## 📊 Summary\n\n")
            f.write(f"- **Issues Found:** {len(analysis['issues_found'])}\n")
            f.write(f"- **Optimizations Suggested:** {len(analysis['optimizations'])}\n")
            f.write(f"- **Configuration Changes:** {len(analysis['configuration_changes'])}\n")
            f.write(f"- **Priority Actions:** {len(analysis['priority_actions'])}\n\n")
            
            # Issues Found
            if analysis['issues_found']:
                f.write("## ❌ Issues Found\n\n")
                for issue in analysis['issues_found']:
                    f.write(f"### {issue['tool']} - {issue['issue']}\n")
                    f.write(f"- **Category:** {issue['category']}\n")
                    f.write(f"- **Priority:** {issue.get('priority', 'medium')}\n")
                    f.write(f"- **Count:** {issue.get('count', 1)}\n")
                    if 'examples' in issue:
                        f.write("- **Examples:**\n")
                        for example in issue['examples']:
                            f.write(f"  - `{example}`\n")
                    f.write("\n")
            
            # Optimizations
            if analysis['optimizations']:
                f.write("## ⚡ Performance Optimizations\n\n")
                for opt in analysis['optimizations']:
                    f.write(f"### {opt['test']} - {opt['issue']}\n")
                    f.write(f"- **Target:** {opt['target']}\n")
                    f.write(f"- **Priority:** {opt.get('priority', 'medium')}\n\n")
            
            # Configuration Changes
            if analysis['configuration_changes']:
                f.write("## 🔧 Configuration Changes\n\n")
                for change in analysis['configuration_changes']:
                    f.write(f"### {change['target']} - {change['description']}\n")
                    f.write(f"- **Type:** {change['type']}\n")
                    f.write(f"- **Priority:** {change['priority']}\n")
                    f.write("- **Changes:**\n")
                    for c in change['changes']:
                        f.write(f"  - {c}\n")
                    f.write("\n")
            
            # Priority Actions
            if analysis['priority_actions']:
                f.write("## 🎯 Priority Actions\n\n")
                f.write("| Action | Priority | Effort | Impact | Timeline |\n")
                f.write("|--------|----------|--------|--------|----------|\n")
                for action in analysis['priority_actions']:
                    f.write(f"| {action['action']} | {action['priority']} | {action['effort']} | {action['impact']} | {action['timeline']} |\n")
                f.write("\n")
            
            # Recommendations
            f.write("## 💡 General Recommendations\n\n")
            f.write("1. **Implement comprehensive logging** for better debugging\n")
            f.write("2. **Add automated testing** for all tools\n")
            f.write("3. **Set up monitoring** for performance metrics\n")
            f.write("4. **Create user documentation** for common issues\n")
            f.write("5. **Implement error recovery** mechanisms\n\n")
        
        print(f"📄 Optimization report saved to: {output_file}")
        return output_file

def main():
    """Main function to run the configuration optimizer"""
    print("🔧 LangFlow Connect MVP - Tool Configuration Optimizer")
    print("=" * 60)
    
    optimizer = ToolConfigurationOptimizer()
    
    # Find the most recent test report
    report_files = [f for f in os.listdir('.') if f.startswith('tool_optimization_report_') and f.endswith('.json')]
    
    if not report_files:
        print("❌ No test reports found. Please run the test suite first.")
        return
    
    # Use the most recent report
    latest_report = max(report_files)
    print(f"📊 Using test report: {latest_report}")
    
    # Analyze the report
    analysis = optimizer.analyze_test_report(latest_report)
    
    if not analysis:
        print("❌ Failed to analyze test report.")
        return
    
    # Generate optimization report
    report_file = optimizer.generate_optimization_report(analysis)
    
    # Display summary
    print("\n" + "=" * 60)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Issues Found: {len(analysis['issues_found'])}")
    print(f"Optimizations: {len(analysis['optimizations'])}")
    print(f"Configuration Changes: {len(analysis['configuration_changes'])}")
    print(f"Priority Actions: {len(analysis['priority_actions'])}")
    
    # Show top priority actions
    if analysis['priority_actions']:
        print("\n🎯 TOP PRIORITY ACTIONS:")
        for i, action in enumerate(analysis['priority_actions'][:5], 1):
            print(f"{i}. {action['action']} ({action['priority']} priority)")
    
    print(f"\n✅ Analysis completed! Check {report_file} for detailed recommendations.")

if __name__ == "__main__":
    main()
