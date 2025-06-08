# Multi-Agent Traffic Simulation
### AASMA (Autonomous Agents and Multi-Agent Systems) 2024/2025 Course Project

A multi-agent traffic simulation environment featuring autonomous and human-driven vehicles on a circular highway. The environment is built using Gymnasium and features:
- Single-lane circular highway with customizable parameters
- Mixed traffic with configurable ratio of autonomous and human-driven vehicles
- Human drivers modeled using the Intelligent Driver Model (IDM)
- Multiple autonomous vehicle control strategies including consensus-based and rule-based approaches
- Real-time visualization with performance metrics
- Comprehensive simulation analytics and results plotting

## Features

- **Mixed Traffic Simulation**: Combine autonomous vehicles with human-driven vehicles using IDM
- **Multiple AV Strategies**: Random, Greedy, Consensus-Based Control, and In-the-middle Rule Control
- **Flexible Configuration**: Adjustable vehicle counts, AV ratios, and positioning strategies
- **Real-time Visualization**: Live simulation display with vehicle speeds and positions
- **Performance Analytics**: Built-in metrics collection and analysis tools
- **Batch Processing**: Support for multiple simulation runs with statistical analysis

## Prerequisites

- Python 3.8 or higher
- One of the following installation methods:
  - devenv/Nix (recommended for reproducible environments)
  - Traditional Python package management (pip)

## Installation

### Option 1: Using devenv/Nix (Recommended)

If you have devenv and Nix installed:

1. Navigate to the project directory
2. Enter the development environment:
```bash
devenv shell
```

The environment will automatically set up all required dependencies and add the project to your Python path.

### Option 2: Using pip

1. Navigate to the project directory

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Add the project directory to your Python path:
```bash
export PYTHONPATH="$PYTHONPATH:."  # On Windows: set PYTHONPATH=%PYTHONPATH%;.
```

## Quick Start

### Basic Simulation

Run the interactive simulation with guided configuration:

```bash
python -m simulation.run
```

The simulation will prompt you to configure:

1. **Track length** (meters)
   - Defines the circumference of the circular highway
   - Affects vehicle density and traffic dynamics

2. **Number of vehicles** (recommended: 4-12)
   - Minimum: 2 vehicles
   - Performance warning for >20 vehicles

3. **Percentage of autonomous vehicles** (0-100%)
   - Controls the ratio of AI-controlled vs human-driven vehicles

4. **AV positioning strategy**:
   - **Interleaved**: Autonomous and human vehicles alternate positions
   - **Grouped**: Autonomous vehicles stay together in clusters
   - **Random**: Random distribution throughout the track

5. **Autonomous vehicle control strategy**:
   - **Random**: Random acceleration/deceleration within safety limits
   - **Greedy**: Proportional control based on local traffic conditions
   - **Consensus-Based Control**: Coordinated behavior among autonomous vehicles
   - **In-the-middle Rule Control**: Maintains safe distances using middle-distance rules

6. **Controlled braking** (optional):
   - Enable periodic braking events to test traffic flow response
   - Configure braking frequency, duration, and intensity
   - Select which vehicle performs the braking maneuver
   - If not enabled, the user can still manually brake the vehicles by clicking on the vehicles

### Visualization

The simulation displays a real-time visualization showing:
- **Blue rectangles**: Autonomous vehicles with their control strategy
- **Red rectangles**: Human-driven vehicles (using Intelligent Driver Model)
- **Numbers on vehicles**: Current speed of each vehicle (m/s)
- **Circular track**: Single-lane highway with configurable length and parameters
- **Performance metrics**: Real-time display of traffic flow metrics

### Controls

- **Close window** or **Ctrl+C**: Stop the simulation gracefully
- The simulation runs indefinitely until manually stopped or a collision occurs

## Project Structure

```
simulation/
├── __init__.py
├── run.py                  # Main interactive simulation runner
├── multipleRuns.py         # Batch simulation executor
├── plotFromResults.py      # Results analysis and plotting
├── environment.py          # Core simulation environment (Gymnasium-based)
├── visualization.py        # Real-time visualization system
├── metrics.py             # Performance metrics and data collection
├── agents/
    ├── __init__.py
    ├── idm_agent.py       # Intelligent Driver Model implementation
    └── autonomous_agent.py # Autonomous vehicle strategies and base classes
results/                   # Simulation output data and analysis
reports/                  # Generated reports and documentation
```
