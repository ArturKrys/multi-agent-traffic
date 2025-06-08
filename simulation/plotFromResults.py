import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
import sys

# Path to the merged JSON file (can be overridden by command line argument)
if len(sys.argv) > 1:
    JSON_PATH = sys.argv[1]
else:
    JSON_PATH = os.path.join('results', '12veh_1000m_AvPenVar_random_AgTypeVar_True_3_50_-6.0_None_1800seconds.json')

print(f"Loading data from: {JSON_PATH}")

# Check if file exists
if not os.path.exists(JSON_PATH):
    print(f"Error: File {JSON_PATH} not found!")
    print("Available files in results directory:")
    if os.path.exists('results'):
        for file in os.listdir('results'):
            if file.endswith('.json'):
                print(f"  - {file}")
    sys.exit(1)

# Load simulation data
with open(JSON_PATH, 'r') as f:
    data = json.load(f)

# Check if data has the new format with metadata
if isinstance(data, dict) and 'simulation_metadata' in data:
    # New format with metadata
    metadata = data['simulation_metadata']
    results = data['results']
    
    # Get parameters from metadata and first result
    if results and 'simulation_parameters' in results[0]:
        simulation_params = results[0]['simulation_parameters'].copy()
        # Remove varied parameters from display since they'll be shown on the axes
        varied_params = metadata.get('varied_parameters', [])
        for param in varied_params:
            simulation_params.pop(param, None)
    else:
        # Fallback to fixed parameters from metadata
        simulation_params = metadata.get('fixed_parameters', {})
    
    print(f"Loaded {metadata.get('total_runs', len(results))} simulation results")
    print(f"Description: {metadata.get('description', 'N/A')}")
    print(f"Varied parameters: {metadata.get('varied_parameters', [])}")
    
else:
    # Legacy format - extract metadata from filename
    results = data
    basename = os.path.splitext(os.path.basename(JSON_PATH))[0]
    parts = basename.split('_')
    keys = [
        'num_vehicles', 'av_percentage', 'position_type', 'agent_type',
        'controlled_braking', 'brake_every_x_loops', 'brake_duration',
        'brake_acceleration', 'braking_agent_index', 'sim_duration'
    ]
    simulation_params = dict(zip(keys, parts))
    print("Loaded legacy format data - using filename parsing for parameters")

# Discover unique AV percentages and agent types from the results
av_percentages = sorted({entry['av_percentage'] for entry in results})
agent_types    = sorted({entry['agent_type']   for entry in results})

# Define metrics to plot
metrics = [
    ('avg_flow_rate_over_simulation', 'Average Flow Rate (vehicles/sec)'),
    ('avg_speed_over_simulation',      'Average Speed (m/s)'),
    ('avg_speed_variance_over_simulation', 'Speed Variance (m²/s²)'),
    ('wave_formation_time',            'Wave Formation Time (s)'),
    ('wave_dissipation_time',          'Wave Dissipation Time (s)'),
]

# Group data by agent
grouped = {agent: [] for agent in agent_types}
for agent in agent_types:
    for av in av_percentages:
        rec = next((r for r in results 
                    if r['agent_type']==agent and r['av_percentage']==av), None)
        if rec is None:
            rec = {k: float('nan') for k,_ in metrics}
        grouped[agent].append(rec)

# Format simulation parameters for display
def format_parameters(params):
    """Format parameters dictionary for nice display"""
    formatted_lines = []
    
    # Order parameters in a logical way
    param_order = [
        'num_vehicles', 'track_length', 'position_type', 'sim_duration',
        'controlled_braking', 'brake_every_x_loops', 'brake_duration', 
        'brake_acceleration', 'braking_agent_index'
    ]
    
    # Display ordered parameters first
    for key in param_order:
        if key in params:
            value = params[key]
            if key == 'controlled_braking':
                formatted_lines.append(f"Controlled Braking: {value}")
            elif key == 'brake_every_x_loops':
                formatted_lines.append(f"Brake Every: {value} loops")
            elif key == 'brake_duration':
                formatted_lines.append(f"Brake Duration: {value} steps")
            elif key == 'brake_acceleration':
                formatted_lines.append(f"Brake Accel: {value} m/s²")
            elif key == 'braking_agent_index':
                agent_str = "First IDM" if value is None or value == "None" else f"Agent {value}"
                formatted_lines.append(f"Braking Agent: {agent_str}")
            elif key == 'num_vehicles':
                formatted_lines.append(f"Vehicles: {value}")
            elif key == 'track_length':
                formatted_lines.append(f"Track Length: {value}m")
            elif key == 'position_type':
                formatted_lines.append(f"AV Positioning: {value}")
            elif key == 'sim_duration':
                formatted_lines.append(f"Duration: {value}s")
    
    # Add any remaining parameters
    for key, value in params.items():
        if key not in param_order:
            formatted_lines.append(f"{key.replace('_', ' ').title()}: {value}")
    
    return "\n".join(formatted_lines)

# Prepare parameter text for display
param_text = format_parameters(simulation_params)

# Plot each metric
for field, label in metrics:
    fig, ax = plt.subplots(figsize=(12, 6))  # Wider figure to accommodate parameter text
    
    for agent in agent_types:
        y = [ rec[field] if rec[field] is not None else float('nan') 
              for rec in grouped[agent] ]
        ax.plot(av_percentages, y, marker='o', label=agent, linewidth=2, markersize=6)
    
    ax.set_xlabel('AV Percentage', fontsize=12)
    ax.set_ylabel(label, fontsize=12)
    ax.set_title(f'{label} vs. AV Percentage', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(title='Agent Type', fontsize=10, title_fontsize=11)
    
    # Format x-axis to show percentages nicely
    ax.set_xticks(av_percentages)
    ax.set_xticklabels([f'{int(av*100)}%' for av in av_percentages])

    # Make room on the right for the parameter information
    plt.tight_layout(rect=[0, 0, 0.73, 1])
    
    # Add parameter information on the right side
    fig.text(0.75, 0.5, 'Simulation Parameters:\n\n' + param_text, 
             va='center', ha='left', fontsize=9, family='monospace',
             bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(0.75, 0.02, f'Generated: {timestamp}', 
             ha='left', fontsize=8, style='italic', alpha=0.7)

    plt.show()

print(f"\nPlotted {len(metrics)} metrics for {len(agent_types)} agent types and {len(av_percentages)} AV percentages")
print(f"Data source: {JSON_PATH}")
print("\nUsage: python -m simulation.plotFromResults [path_to_json_file]")
