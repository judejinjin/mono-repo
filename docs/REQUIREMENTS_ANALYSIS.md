# Requirements Analysis: scripts vs build/requirements

## 📋 **Current Dependencies Comparison**

### **requirements-scripts.txt:**
```
requests>=2.28.0
python-dateutil>=2.8.0
dataclasses>=0.6; python_version<"3.7"
```

### **build/requirements/base.txt (relevant sections):**
```
requests==2.31.0
# python-dateutil - NOT PRESENT
# dataclasses - NOT PRESENT (but not needed for Python 3.7+)
```

## 🔍 **Analysis:**

### ✅ **Dependencies Already Covered:**
1. **`requests`**: 
   - **scripts**: `>=2.28.0` 
   - **base.txt**: `==2.31.0` (✅ Compatible - 2.31.0 >= 2.28.0)

### ❌ **Missing Dependencies:**
1. **`python-dateutil>=2.8.0`**: Not present in any build requirements
2. **`dataclasses>=0.6`**: Not needed (Python 3.7+ has built-in dataclasses)

### 🎯 **Dependency Usage Analysis:**

**`python-dateutil` is used in:**
- Risk API client for date/time parsing
- Market data processing scripts
- Report generation with date ranges

**`requests` is used in:**
- Risk API client for HTTP requests
- Airflow API client for REST calls
- External API integrations

## 💡 **Recommendation:**

### **Option 1: Merge into base.txt (Recommended)**
Add `python-dateutil>=2.8.0` to `build/requirements/base.txt` since:
- Date/time parsing is a common utility across all environments
- API clients are core infrastructure components
- No conflicts with existing dependencies

### **Option 2: Keep Separate**
Maintain `requirements-scripts.txt` if:
- Scripts are considered optional/separate from main application
- Want to minimize base application dependencies

## 🔧 **Proposed Merge:**

### **Add to build/requirements/base.txt:**
```python
# Date/time utilities (for API clients and scripts)
python-dateutil>=2.8.0
```

### **Remove requirements-scripts.txt:**
- No longer needed after merge
- Simplifies dependency management
- Reduces maintenance overhead

## ✅ **Benefits of Merging:**

1. **Unified Dependency Management**: Single source of truth
2. **Environment Consistency**: All environments include necessary dependencies
3. **Simplified Installation**: One requirements file per environment
4. **Better Maintenance**: Fewer files to track and update
5. **CI/CD Integration**: Build system handles all dependencies

## 🚀 **Implementation Steps:**

1. Add `python-dateutil>=2.8.0` to `build/requirements/base.txt`
2. Verify no version conflicts
3. Test API clients with updated requirements
4. Remove `requirements-scripts.txt`
5. Update documentation references

**Conclusion**: **RECOMMENDED TO MERGE** - The scripts dependencies are minimal and align well with the existing base requirements structure.
