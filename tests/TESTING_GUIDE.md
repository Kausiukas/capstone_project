# LangFlow Connect Testing Guide

This guide provides comprehensive information about testing the LangFlow Connect system, including how to run tests, interpret results, and troubleshoot issues.

## Table of Contents

1. [Overview](#overview)
2. [Test Suites](#test-suites)
3. [Quick Start](#quick-start)
4. [Running Tests](#running-tests)
5. [Test Results](#test-results)
6. [Troubleshooting](#troubleshooting)
7. [Performance Testing](#performance-testing)
8. [Continuous Integration](#continuous-integration)

## Overview

The LangFlow Connect testing suite consists of multiple test types designed to validate different aspects of the system:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and workflows
- **Performance Tests**: Measure system performance under various loads
- **MCP Server Tests**: Validate Model Context Protocol functionality
- **Comprehensive Tests**: End-to-end system validation

## Test Suites

### 1. Quick Test (`quick_test.py`)
**Purpose**: Immediate validation of critical system functionality
**Duration**: ~30-60 seconds
**Coverage**: Basic imports, component initialization, core functionality, MCP server basics

```bash
cd tests
python quick_test.py
```

### 2. Unit Tests (`unit_tests.py`)
**Purpose**: Test individual components using Python's unittest framework
**Duration**: ~1-2 minutes
**Coverage**: All major components with detailed assertions

```bash
cd tests
python unit_tests.py
```

### 3. Comprehensive Test Suite (`comprehensive_test_suite.py`)
**Purpose**: Full system validation with temporary test environments
**Duration**: ~5-10 minutes
**Coverage**: Unit tests, integration tests, MCP server tests, end-to-end workflows, performance tests, error handling

```bash
cd tests
python comprehensive_test_suite.py
```

### 4. Performance Tests (`performance_tests.py`)
**Purpose**: Measure system performance under various load conditions
**Duration**: ~10-15 minutes
**Coverage**: File operations, code analysis, cost tracking, concurrent operations, memory leak detection

```bash
cd tests
python performance_tests.py
```

### 5. Master Test Runner (`run_all_tests.py`)
**Purpose**: Orchestrate all test suites with unified reporting
**Duration**: ~20-30 minutes
**Coverage**: All test suites with comprehensive reporting

```bash
cd tests
python run_all_tests.py --test-types all
```

## Quick Start

For immediate validation of the system:

1. **Ensure you're in the virtual environment**:
   ```bash
   .\venv\Scripts\Activate.ps1
   ```

2. **Run quick tests**:
   ```bash
   cd tests
   python quick_test.py
   ```

3. **Check results**: Look for the summary at the end showing all tests passed.

## Running Tests

### Command Line Options

The master test runner supports various options:

```bash
# Run all tests
python run_all_tests.py --test-types all

# Run specific test types
python run_all_tests.py --test-types unit performance

# Run only quick validation
python run_all_tests.py --test-types comprehensive
```

### Test Types Available

- `comprehensive`: Full comprehensive test suite
- `unit`: Unit tests using unittest framework
- `performance`: Performance and load testing
- `mcp`: MCP server specific tests
- `integration`: Integration tests
- `all`: All test types

### Environment Setup

Before running tests, ensure:

1. **Virtual environment is activated**:
   ```bash
   .\venv\Scripts\Activate.ps1
   ```

2. **Dependencies are installed**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Working directory is correct**:
   ```bash
   cd tests
   ```

## Test Results

### Understanding Test Output

Test results are displayed in real-time with the following format:

```
✓ PASS Test Name (0.25s)
✗ FAIL Test Name (0.10s)
    Error: Detailed error message
```

### Result Files Generated

1. **`comprehensive_test_results.json`**: Results from comprehensive test suite
2. **`performance_test_report.json`**: Performance metrics and benchmarks
3. **`final_test_report.json`**: Combined results from all test suites
4. **`comprehensive_test_suite.log`**: Detailed logs from test execution

### Success Criteria

- **Quick Tests**: All tests must pass (100% success rate)
- **Unit Tests**: ≥90% success rate
- **Performance Tests**: All operations within time thresholds
- **MCP Server Tests**: All expected tools registered and functional
- **Integration Tests**: All component interactions working correctly

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Symptoms**: `ModuleNotFoundError` or `ImportError`
**Solutions**:
- Ensure virtual environment is activated
- Verify `src` directory is in Python path
- Check that all dependencies are installed

#### 2. Initialization Errors
**Symptoms**: `AttributeError: 'Component' object has no attribute 'initialize'`
**Solutions**:
- Ensure all components have `initialize()` methods
- Check component imports are correct
- Verify component implementations

#### 3. File System Errors
**Symptoms**: `FileNotFoundError` or permission errors
**Solutions**:
- Ensure test directories exist
- Check file permissions
- Verify temporary directory creation

#### 4. MCP Server Issues
**Symptoms**: Server fails to start or tools not registered
**Solutions**:
- Check MCP server implementation
- Verify tool registration syntax
- Ensure FastMCP is properly configured

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Isolation

Each test suite creates isolated test environments to prevent interference:

- Temporary directories for file operations
- Mock external services where appropriate
- Cleanup after each test

## Performance Testing

### Performance Benchmarks

The system includes predefined performance benchmarks:

| Operation | File Size | Max Time (ms) |
|-----------|-----------|---------------|
| Read File | 1KB | 100 |
| Read File | 10KB | 200 |
| Read File | 100KB | 500 |
| Write File | 1KB | 150 |
| Write File | 10KB | 300 |
| Write File | 100KB | 800 |
| Code Analysis | 1KB | 200 |
| Code Analysis | 10KB | 500 |
| Code Analysis | 100KB | 2000 |

### Performance Metrics

Tests measure:
- **Execution Time**: How long operations take
- **Memory Usage**: Memory consumption during operations
- **CPU Usage**: CPU utilization
- **Concurrent Performance**: System behavior under load
- **Memory Leaks**: Long-term memory usage patterns

### Interpreting Performance Results

1. **Check if operations meet time thresholds**
2. **Monitor memory usage for leaks**
3. **Verify CPU usage stays within limits**
4. **Ensure concurrent operations scale properly**

## Continuous Integration

### Automated Testing

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
name: Test LangFlow Connect
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd tests
          python quick_test.py
          python run_all_tests.py --test-types all
```

### Test Reports

CI systems can parse the JSON reports for:
- Test pass/fail status
- Performance metrics
- Coverage information
- Detailed error reports

## Configuration

### Test Configuration (`test_config.json`)

The test configuration file controls:
- Test suite settings
- Performance thresholds
- Test data parameters
- Reporting options
- Environment settings

### Customizing Tests

To customize test behavior:

1. **Modify thresholds** in `test_config.json`
2. **Add new test cases** to existing test files
3. **Create custom test suites** following the established patterns
4. **Extend performance benchmarks** for specific use cases

## Best Practices

### Writing Tests

1. **Use descriptive test names**
2. **Test one thing per test method**
3. **Include proper setup and teardown**
4. **Use meaningful assertions**
5. **Handle cleanup properly**

### Running Tests

1. **Start with quick tests** for immediate validation
2. **Run comprehensive tests** before major changes
3. **Monitor performance tests** for regressions
4. **Check all result files** for detailed analysis

### Maintenance

1. **Update tests** when adding new features
2. **Review performance benchmarks** regularly
3. **Monitor test execution times** for degradation
4. **Keep test data** current and relevant

## Support

For testing issues or questions:

1. **Check the troubleshooting section** above
2. **Review test logs** for detailed error information
3. **Run tests in isolation** to identify specific problems
4. **Consult the main documentation** for system architecture

---

**Note**: This testing guide is part of the LangFlow Connect system. For system-specific documentation, see the main README.md and other documentation files. 