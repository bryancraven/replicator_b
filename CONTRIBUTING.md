# Contributing to Ultra-Realistic Self-Replicating Factory Simulation

Thank you for your interest in contributing!

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs or suggest features
- Include simulation configuration and error messages
- Describe expected vs actual behavior

### Submitting Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes (`./run_simulation.sh`)
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to new functions/classes
- Keep line length under 100 characters

### Adding Custom Subsystems
1. Implement the `ISubsystem` interface from `modular_framework.py`
2. Add your subsystem to `custom_subsystems.py` or create a new file
3. Register with `SubsystemRegistry`
4. Include example usage and tests
5. Update documentation

### Testing
- Run the test suite: `pytest tests/ -v`
- Run with coverage: `pytest tests/ --cov=. --cov-report=html`
- Verify type checking passes: `mypy .`
- Test traditional mode: `python3 self_replicating_factory_sim.py`
- Test modular mode: Create a test script using `ModularFactory`
- Verify visualizations generate correctly
- Ensure code coverage is maintained or improved
- Add tests for new functionality in `tests/unit/` or `tests/integration/`

### Documentation
- Update README.md for user-facing changes
- Update CLAUDE.md for technical implementation details
- Include docstrings in your code
- Add configuration examples if applicable

## Development Setup

### Option 1: Modern Installation (Recommended)
```bash
# Clone the repo
git clone <repo-url>
cd replicator_b

# Install with development dependencies
pip install -e ".[dev]"

# This installs:
# - Core simulation
# - pytest (testing framework)
# - pytest-cov (coverage reporting)
# - mypy (static type checking)
# - black (code formatting)
# - pydantic (configuration validation)

# Run tests
pytest tests/ -v

# Run simulation
./run_simulation.sh
```

### Option 2: Traditional Setup
```bash
# Clone the repo
git clone <repo-url>
cd replicator_b

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run simulation
./run_simulation.sh
```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   - Write code following PEP 8 guidelines
   - Add type hints to new functions
   - Use custom exceptions from `exceptions.py`
   - Add tests for new functionality

3. **Run the development checklist**
   ```bash
   # Run type checking
   mypy .

   # Run tests with coverage
   pytest tests/ -v --cov=.

   # Check coverage report
   open htmlcov/index.html

   # Run simulation to verify
   python3 self_replicating_factory_sim.py --spec specs/minimal.json --max-hours 100
   ```

4. **Pre-commit Checklist**
   - [ ] All tests pass: `pytest tests/ -v`
   - [ ] Type checking passes: `mypy .`
   - [ ] Code coverage maintained or improved
   - [ ] New exceptions added for error cases (use `exceptions.py`)
   - [ ] Configuration validation updated for new config fields (use `config_validation.py`)
   - [ ] Docstrings added to new functions/classes
   - [ ] README.md updated for user-facing changes
   - [ ] CLAUDE.md updated for technical details
   - [ ] No commented-out code or debug prints

5. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "feat: Add new feature description"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/my-new-feature
   ```

### Best Practices

#### Exception Handling
Use custom exceptions from `exceptions.py`:

```python
from exceptions import (
    SpecValidationError,
    ResourceNotFoundError,
    SubsystemNotFoundError
)

# Raise specific exceptions with context
if resource not in available_resources:
    raise ResourceNotFoundError(resource, context="recipe validation")

# Catch and handle appropriately
try:
    load_spec(spec_path)
except SpecValidationError as e:
    logger.error(f"Spec validation failed: {e.errors}")
    raise
```

#### Configuration Validation
Validate configurations using Pydantic models:

```python
from config_validation import FactoryConfig, validate_config

# Validate before using
config = validate_config(user_config_dict)

# Or use Pydantic models directly
config = FactoryConfig(
    energy=EnergyConfig(initial_solar_capacity_kw=200)
)
```

#### Performance Optimization
Use performance utilities when appropriate:

```python
from performance_utils import cached_resource_calculation, profiler

# Cache expensive calculations
@cached_resource_calculation
def calculate_requirements(resource, quantity):
    # ...expensive calculation...
    return result

# Profile performance bottlenecks
@profiler.profile("my_function")
def expensive_function():
    pass
```

#### Type Hints
Add type hints to all new code:

```python
from typing import Dict, List, Optional, Any

def process_resources(
    resources: Dict[str, float],
    max_capacity: Optional[float] = None
) -> List[str]:
    """Process resources with optional capacity limit.

    Args:
        resources: Resource name to quantity mapping
        max_capacity: Optional maximum capacity limit

    Returns:
        List of processed resource names

    Raises:
        ResourceNotFoundError: If resource not in registry
    """
    pass
```

#### Testing
Write tests for new functionality:

```python
# tests/unit/test_my_feature.py
import pytest
from my_module import my_function

def test_my_function_with_valid_input(event_bus):
    """Test my_function with valid input."""
    result = my_function(valid_input)
    assert result == expected_output

def test_my_function_raises_exception():
    """Test my_function raises appropriate exception."""
    with pytest.raises(MyCustomError):
        my_function(invalid_input)
```

## Areas for Contribution

- **New Subsystems**: Implement novel manufacturing strategies
- **Optimization Algorithms**: Improve routing, scheduling, quality control
- **Visualization**: Enhance analysis dashboards
- **Performance**: Optimize simulation speed and memory usage
- **Documentation**: Improve guides and examples
- **Testing**: Add unit tests and integration tests
- **Research Applications**: Share interesting use cases

## Questions?

Feel free to open an issue for discussion or clarification.