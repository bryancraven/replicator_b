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
- Test traditional mode: `python3 self_replicating_factory_sim.py`
- Test modular mode: Create a test script using `ModularFactory`
- Verify visualizations generate correctly
- Check that your changes don't break existing functionality

### Documentation
- Update README.md for user-facing changes
- Update CLAUDE.md for technical implementation details
- Include docstrings in your code
- Add configuration examples if applicable

## Development Setup

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