# Multi-Agent Traffic Simulation
### AASMA (Autonomous and Semi-Autonomous Multi-Agent) 2024/2025 course Project.

A multi-agent traffic simulation environment featuring autonomous and human-driven vehicles on a circular highway. The environment is built using Gymnasium and features:
- Single-lane circular highway
- Mixed traffic with configurable ratio of autonomous and human-driven vehicles
- Human drivers modeled using the Intelligent Driver Model (IDM)
- Extensible autonomous vehicle control strategies
- Real-time visualization

## Prerequisites

- Python 3.8 or higher
- One of the following installation methods:
  - devenv/Nix (recommended)
  - Traditional Python package management (pip)

## Installation

### Option 1: Using devenv/Nix (Recommended)

If you have devenv and Nix installed:

1. Clone the repository:
```bash
git clone <repository-url>
cd multi_agent_traffic
```

2. Enter the development environment:
```bash
devenv shell
```

That's it! The environment will automatically set up all required dependencies and add the project to your Python path.

### Option 2: Using pip

1. Clone the repository:
```bash
git clone <repository-url>
cd multi_agent_traffic
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Add the project directory to your Python path:
```bash
export PYTHONPATH="$PYTHONPATH:."  # On Windows, use: set PYTHONPATH=%PYTHONPATH%;.
```

## Running the Simulation

To run the example simulation:

```bash
python -m circular_highway.example
```

This will start a visualization showing:
- Blue rectangles: Autonomous vehicles
- Red rectangles: Human-driven vehicles (using IDM)
- Numbers: Current speed of each vehicle

## Project Structure

```
simulation/
├── __init__.py
├── environment.py      # Main simulation environment
├── visualization.py    # Visualization tools
├── example.py         # Example usage
└── agents/
    ├── __init__.py
    ├── idm_agent.py       # Intelligent Driver Model implementation
    └── autonomous_agent.py # Base class for autonomous vehicles
```

## Extending the Project

### Adding New Autonomous Vehicle Strategies

Create a new class inheriting from `AutonomousAgent`:

```python
from circular_highway.agents import AutonomousAgent

class MyStrategy(AutonomousAgent):
    def act(self, speed, lead_distance=None, lead_speed=None):
        # Implement your control strategy here
        pass
```

## License

[Your chosen license]
