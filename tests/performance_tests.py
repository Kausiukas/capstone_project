"""
Performance Tests for LangFlow Connect System

This module contains performance tests to evaluate system performance under various load conditions.
"""

import asyncio
import time
import os
import sys
import tempfile
import statistics
import psutil
import json
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modules.module_1_main import (
    WorkspaceManager, RepositoryIngestor, CodeAnalyzer, 
    CodeRefactorer, ExternalServiceManager
)
from modules.module_2_support import (
    PostgreSQLVectorAgent, SystemCoordinator, HealthMonitor,
    PerformanceTracker, MemoryManager
)
from modules.module_3_economy import (
    CostTracker, BudgetManager, OptimizationEngine,
    CostAnalyzer, AlertSystem
)
from modules.module_4_langflow import (
    LangflowConnector, DataVisualizer, FlowManager, ConnectionMonitor
)


class PerformanceMetrics:
    """Container for performance metrics"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.execution_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.success_count = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None
    
    def add_execution_time(self, duration: float):
        """Add execution time measurement"""
        self.execution_times.append(duration)
    
    def add_memory_usage(self, memory_mb: float):
        """Add memory usage measurement"""
        self.memory_usage.append(memory_mb)
    
    def add_cpu_usage(self, cpu_percent: float):
        """Add CPU usage measurement"""
        self.cpu_usage.append(cpu_percent)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.execution_times:
            return {}
        
        return {
            'operation_name': self.operation_name,
            'total_executions': len(self.execution_times),
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_count / len(self.execution_times) * 100,
            'execution_time': {
                'min': min(self.execution_times),
                'max': max(self.execution_times),
                'mean': statistics.mean(self.execution_times),
                'median': statistics.median(self.execution_times),
                'std_dev': statistics.stdev(self.execution_times) if len(self.execution_times) > 1 else 0
            },
            'memory_usage': {
                'min': min(self.memory_usage) if self.memory_usage else 0,
                'max': max(self.memory_usage) if self.memory_usage else 0,
                'mean': statistics.mean(self.memory_usage) if self.memory_usage else 0,
                'median': statistics.median(self.memory_usage) if self.memory_usage else 0
            },
            'cpu_usage': {
                'min': min(self.cpu_usage) if self.cpu_usage else 0,
                'max': max(self.cpu_usage) if self.cpu_usage else 0,
                'mean': statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
                'median': statistics.median(self.cpu_usage) if self.cpu_usage else 0
            }
        }


class PerformanceTestSuite:
    """Performance testing suite for LangFlow Connect system"""
    
    def __init__(self):
        self.logger = self.setup_logging()
        self.test_workspace = None
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.process = psutil.Process()
        
    def setup_logging(self):
        """Setup logging configuration"""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def setup_test_environment(self):
        """Setup test environment"""
        self.test_workspace = tempfile.mkdtemp(prefix="perf_test_")
        self.logger.info(f"Created performance test workspace: {self.test_workspace}")
        
        # Create test files
        await self.create_test_files()
    
    async def create_test_files(self):
        """Create test files for performance testing"""
        import aiofiles
        
        # Create files of different sizes
        file_sizes = [1, 10, 100, 1000]  # KB
        
        for size_kb in file_sizes:
            filename = f"test_{size_kb}kb.py"
            filepath = os.path.join(self.test_workspace, filename)
            
            # Generate code with specified size
            code_lines = self.generate_code_by_size(size_kb)
            content = '\n'.join(code_lines)
            
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(content)
    
    def generate_code_by_size(self, size_kb: int) -> List[str]:
        """Generate Python code of specified size"""
        lines = []
        lines_per_kb = 50  # Approximate lines per KB
        
        total_lines = size_kb * lines_per_kb
        
        for i in range(total_lines):
            if i % 10 == 0:
                lines.append(f'def function_{i}():')
                lines.append(f'    """Function {i} for performance testing"""')
                lines.append(f'    result = {i} * 2')
                lines.append(f'    return result')
            else:
                lines.append(f'    # Line {i} for size generation')
        
        return lines
    
    async def measure_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """Measure performance of an operation"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = PerformanceMetrics(operation_name)
        
        metrics = self.metrics[operation_name]
        
        # Record initial system state
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = self.process.cpu_percent()
        
        # Execute operation and measure time
        start_time = time.time()
        try:
            result = await operation_func(*args, **kwargs)
            success = True
            metrics.success_count += 1
        except Exception as e:
            self.logger.error(f"Operation {operation_name} failed: {e}")
            success = False
            metrics.error_count += 1
            result = None
        
        end_time = time.time()
        
        # Record final system state
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = self.process.cpu_percent()
        
        # Calculate metrics
        duration = end_time - start_time
        memory_delta = final_memory - initial_memory
        cpu_avg = (initial_cpu + final_cpu) / 2
        
        # Store metrics
        metrics.add_execution_time(duration)
        metrics.add_memory_usage(memory_delta)
        metrics.add_cpu_usage(cpu_avg)
        
        return result, success
    
    # ============================================================================
    # PERFORMANCE TESTS
    # ============================================================================
    
    async def test_file_operations_performance(self):
        """Test file operations performance"""
        workspace_manager = WorkspaceManager()
        await workspace_manager.initialize()
        
        try:
            # Test file read performance
            test_files = ['test_1kb.py', 'test_10kb.py', 'test_100kb.py']
            
            for filename in test_files:
                filepath = os.path.join(self.test_workspace, filename)
                
                # Test read operation
                for i in range(10):  # 10 iterations per file
                    await self.measure_operation(
                        f"read_file_{filename}",
                        workspace_manager.read_file,
                        filepath
                    )
                
                # Test write operation
                content = "Test content for performance testing" * 100
                for i in range(10):  # 10 iterations per file
                    test_file = os.path.join(self.test_workspace, f"write_test_{i}.txt")
                    await self.measure_operation(
                        f"write_file_{filename}_size",
                        workspace_manager.write_file,
                        test_file,
                        content
                    )
        
        finally:
            await workspace_manager.cleanup()
    
    async def test_code_analysis_performance(self):
        """Test code analysis performance"""
        code_analyzer = CodeAnalyzer()
        await code_analyzer.initialize()
        
        try:
            # Test analysis of different file sizes
            test_files = ['test_1kb.py', 'test_10kb.py', 'test_100kb.py']
            
            for filename in test_files:
                filepath = os.path.join(self.test_workspace, filename)
                
                # Read file content
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Test analysis performance
                for i in range(5):  # 5 iterations per file
                    await self.measure_operation(
                        f"analyze_code_{filename}",
                        code_analyzer.analyze_code,
                        content,
                        'python'
                    )
        
        finally:
            await code_analyzer.cleanup()
    
    async def test_cost_tracking_performance(self):
        """Test cost tracking performance"""
        cost_tracker = CostTracker()
        await cost_tracker.initialize()
        
        try:
            # Test token usage tracking
            for i in range(100):  # 100 iterations
                await self.measure_operation(
                    "track_token_usage",
                    cost_tracker.track_token_usage,
                    f"model_{i % 5}",
                    100 + i,
                    0.001 + (i * 0.0001)
                )
            
            # Test API call tracking
            for i in range(100):  # 100 iterations
                await self.measure_operation(
                    "track_api_call",
                    cost_tracker.track_api_call,
                    f"api_{i % 10}",
                    0.05 + (i * 0.001)
                )
            
            # Test cost summary retrieval
            for i in range(10):  # 10 iterations
                await self.measure_operation(
                    "get_cost_summary",
                    cost_tracker.get_cost_summary
                )
        
        finally:
            await cost_tracker.cleanup()
    
    async def test_health_monitoring_performance(self):
        """Test health monitoring performance"""
        health_monitor = HealthMonitor()
        await health_monitor.initialize()
        
        try:
            # Test health check performance
            for i in range(50):  # 50 iterations
                await self.measure_operation(
                    "check_system_health",
                    health_monitor.check_system_health
                )
        
        finally:
            await health_monitor.cleanup()
    
    async def test_concurrent_operations(self):
        """Test performance under concurrent load"""
        workspace_manager = WorkspaceManager()
        code_analyzer = CodeAnalyzer()
        cost_tracker = CostTracker()
        
        await workspace_manager.initialize()
        await code_analyzer.initialize()
        await cost_tracker.initialize()
        
        try:
            # Create test content
            test_content = self.generate_code_by_size(10)  # 10KB
            content_str = '\n'.join(test_content)
            
            # Define concurrent operations
            async def concurrent_file_operation():
                test_file = os.path.join(self.test_workspace, f"concurrent_test_{time.time()}.py")
                await workspace_manager.write_file(test_file, content_str)
                return await workspace_manager.read_file(test_file)
            
            async def concurrent_analysis_operation():
                return await code_analyzer.analyze_code(content_str, 'python')
            
            async def concurrent_cost_operation():
                await cost_tracker.track_token_usage('concurrent_model', 100, 0.001)
                return await cost_tracker.get_cost_summary()
            
            # Run concurrent operations
            operations = [
                concurrent_file_operation,
                concurrent_analysis_operation,
                concurrent_cost_operation
            ]
            
            # Test with different concurrency levels
            concurrency_levels = [1, 5, 10, 20]
            
            for level in concurrency_levels:
                self.logger.info(f"Testing concurrency level: {level}")
                
                start_time = time.time()
                
                # Create tasks
                tasks = []
                for i in range(level):
                    for operation in operations:
                        tasks.append(operation())
                
                # Execute concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Record metrics
                metrics = PerformanceMetrics(f"concurrent_{level}_operations")
                metrics.add_execution_time(duration)
                metrics.success_count = len([r for r in results if not isinstance(r, Exception)])
                metrics.error_count = len([r for r in results if isinstance(r, Exception)])
                
                self.metrics[f"concurrent_{level}_operations"] = metrics
        
        finally:
            await workspace_manager.cleanup()
            await code_analyzer.cleanup()
            await cost_tracker.cleanup()
    
    async def test_memory_leak_detection(self):
        """Test for memory leaks during extended operations"""
        workspace_manager = WorkspaceManager()
        code_analyzer = CodeAnalyzer()
        cost_tracker = CostTracker()
        
        await workspace_manager.initialize()
        await code_analyzer.initialize()
        await cost_tracker.initialize()
        
        try:
            # Initial memory measurement
            initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform extended operations
            for i in range(1000):  # 1000 iterations
                # File operations
                test_file = os.path.join(self.test_workspace, f"leak_test_{i}.py")
                content = f"# Test file {i}\ndef test_function_{i}():\n    return {i}"
                await workspace_manager.write_file(test_file, content)
                
                # Code analysis
                await code_analyzer.analyze_code(content, 'python')
                
                # Cost tracking
                await cost_tracker.track_token_usage(f"model_{i % 10}", 50, 0.001)
                
                # Memory measurement every 100 iterations
                if i % 100 == 0:
                    current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                    memory_increase = current_memory - initial_memory
                    
                    self.logger.info(f"Iteration {i}: Memory increase = {memory_increase:.2f} MB")
                    
                    # Alert if memory increase is significant
                    if memory_increase > 100:  # 100 MB threshold
                        self.logger.warning(f"Potential memory leak detected at iteration {i}")
            
            # Final memory measurement
            final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            total_memory_increase = final_memory - initial_memory
            
            self.logger.info(f"Total memory increase: {total_memory_increase:.2f} MB")
        
        finally:
            await workspace_manager.cleanup()
            await code_analyzer.cleanup()
            await cost_tracker.cleanup()
    
    # ============================================================================
    # TEST RUNNER
    # ============================================================================
    
    async def run_performance_tests(self):
        """Run all performance tests"""
        self.logger.info("Starting performance test suite...")
        
        # Setup test environment
        await self.setup_test_environment()
        
        try:
            # Run performance tests
            await self.test_file_operations_performance()
            await self.test_code_analysis_performance()
            await self.test_cost_tracking_performance()
            await self.test_health_monitoring_performance()
            await self.test_concurrent_operations()
            await self.test_memory_leak_detection()
            
        finally:
            # Cleanup
            import shutil
            if self.test_workspace and os.path.exists(self.test_workspace):
                shutil.rmtree(self.test_workspace)
        
        # Generate performance report
        self.generate_performance_report()
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
                'platform': sys.platform
            },
            'performance_metrics': {}
        }
        
        # Process metrics
        for operation_name, metrics in self.metrics.items():
            report['performance_metrics'][operation_name] = metrics.get_statistics()
        
        # Save report
        with open('performance_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self.print_performance_summary()
    
    def print_performance_summary(self):
        """Print performance test summary"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST RESULTS SUMMARY")
        print("="*80)
        
        for operation_name, metrics in self.metrics.items():
            stats = metrics.get_statistics()
            if not stats:
                continue
            
            print(f"\n{operation_name}:")
            print(f"  Total executions: {stats['total_executions']}")
            print(f"  Success rate: {stats['success_rate']:.1f}%")
            print(f"  Execution time (seconds):")
            print(f"    Mean: {stats['execution_time']['mean']:.4f}")
            print(f"    Median: {stats['execution_time']['median']:.4f}")
            print(f"    Min: {stats['execution_time']['min']:.4f}")
            print(f"    Max: {stats['execution_time']['max']:.4f}")
            
            if stats['memory_usage']['mean'] > 0:
                print(f"  Memory usage (MB):")
                print(f"    Mean: {stats['memory_usage']['mean']:.2f}")
                print(f"    Max: {stats['memory_usage']['max']:.2f}")
        
        print(f"\nDetailed report saved to: performance_test_report.json")
        print("="*80)


async def main():
    """Main entry point for performance tests"""
    test_suite = PerformanceTestSuite()
    await test_suite.run_performance_tests()


if __name__ == "__main__":
    asyncio.run(main()) 