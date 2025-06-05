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

### Interactive Simulation

To run the interactive simulation with customizable parameters:

```bash
python -m simulation.run
```

The simulation will prompt you to configure:

1. **Number of vehicles** (recommended: 4-12)
   - Minimum: 2 vehicles
   - Warning for >20 vehicles due to performance impact

2. **Percentage of autonomous vehicles** (0-100%)
   - Controls the ratio of AI-controlled vs human-driven vehicles

3. **AV positioning strategy**:
   - **Interleaved**: Autonomous and human vehicles alternate
   - **Grouped**: Autonomous vehicles stay together
   - **Random**: Random distribution

4. **Autonomous vehicle control strategy**:
   - **Random**: Random acceleration/deceleration within limits
   - **Greedy**: Proportional control based on traffic conditions
   - **Consensus-Based Control**: Coordinated behavior among autonomous vehicles
   - **In-the-middle Rule Control**: Maintains safe distances using middle-distance rules

5. **Controlled braking** (optional):
   - Enable periodic braking events to test traffic flow response
   - Configure braking frequency, duration, and intensity
   - Select which vehicle performs the braking maneuver

### Visualization

The simulation displays a real-time visualization showing:
- **Blue rectangles**: Autonomous vehicles
- **Red rectangles**: Human-driven vehicles (using Intelligent Driver Model)
- **Numbers**: Current speed of each vehicle (m/s)
- **Circular track**: Single-lane highway with configurable length

### Controls

- **Close window** or **Ctrl+C**: Stop the simulation
- The simulation runs indefinitely until manually stopped or a collision occurs

### Example Usage

```bash
# Run with default settings (will prompt for configuration)
python -m simulation.run

# The simulation will guide you through setup with prompts like:
# Enter the number of vehicles (recommended: 4-12): 8
# Enter the percentage of autonomous vehicles (0 to 100): 50
# Select AV positioning: [1] Interleaved [2] Grouped [3] Random: 1
# Select AV agent type: [1] Random [2] Greedy [3] Consensus [4] In-the-middle: 3
```

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
