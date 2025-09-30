# Performance Optimization Files

This directory contains all performance optimization related files that were moved from various locations in the project.

## 📁 Directory Structure

```
tests/performance_optimization/
├── run_performance_optimization.py          # Main performance optimization runner
├── requirements-performance.txt             # Performance optimization dependencies
├── create_performance_optimization_diagrams.py  # Diagram generation script
├── libs_performance/                        # Performance optimization libraries
│   ├── __init__.py                          # Module initialization
│   ├── optimization.py                     # Core optimization classes
│   └── monitoring.py                       # Performance monitoring classes
└── README.md                               # This file
```

## 🚀 Files Moved

### From Root Directory:
- `run_performance_optimization.py` → `tests/performance_optimization/run_performance_optimization.py`
- `requirements-performance.txt` → `tests/performance_optimization/requirements-performance.txt`

### From libs/performance/:
- `libs/performance/` → `tests/performance_optimization/libs_performance/`
  - `__init__.py` - Module initialization with all exports
  - `optimization.py` - Core performance optimization classes
  - `monitoring.py` - Performance monitoring and benchmarking classes

### From devops/:
- `devops/create_performance_optimization_diagrams.py` → `tests/performance_optimization/create_performance_optimization_diagrams.py`

## 🔧 Usage

### Running Performance Optimization:
```bash
cd tests/performance_optimization
python run_performance_optimization.py --help
```

### Installing Dependencies:
```bash
cd tests/performance_optimization
pip install -r requirements-performance.txt
```

### Generating Performance Diagrams:
```bash
cd tests/performance_optimization
python create_performance_optimization_diagrams.py
```

## 📝 Import Path Updates

The `run_performance_optimization.py` file has been updated to use the correct import paths:
- Updated PROJECT_ROOT to point to the correct project root (`../../..`)
- Added local `libs_performance` directory to Python path
- Changed imports from `libs.performance` to `libs_performance`

## 🎯 Integration

These files are now organized within the tests directory structure but maintain their full functionality. The performance optimization system can still be run independently or integrated with the main test suite.

## 🔗 Related Files

- Main test runner: `../../run_tests.py` (includes performance test execution)
- Performance tests: `../performance/test_performance_benchmarks.py`
- Performance diagrams: `../../docs/architecture/performance_*.png/svg`