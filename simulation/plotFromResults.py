import os
import json
import matplotlib.pyplot as plt

# Path to the merged JSON file
JSON_PATH = os.path.join('results', '12_AvPenVar_random_AgTypeVar_True_3_50_-6.0_None_180seconds.json')

# Extract metadata from filename
basename = os.path.splitext(os.path.basename(JSON_PATH))[0]
parts = basename.split('_')
keys = [
    'num_vehicles', 'av_percentage', 'position_type', 'agent_type',
    'controlled_braking', 'brake_every_x_loops', 'brake_duration',
    'brake_acceleration', 'braking_agent_index', 'sim_duration'
]
metadata = dict(zip(keys, parts))

# Load simulation data
with open(JSON_PATH, 'r') as f:
    data = json.load(f)

# Discover unique AV percentages and agent types
av_percentages = sorted({entry['av_percentage'] for entry in data})
agent_types    = sorted({entry['agent_type']   for entry in data})

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
        rec = next((r for r in data 
                    if r['agent_type']==agent and r['av_percentage']==av), None)
        if rec is None:
            rec = {k: float('nan') for k,_ in metrics}
        grouped[agent].append(rec)

# Prepare a sidebar text block
note_lines = [f"{k}: {v}" for k, v in metadata.items()]
note_text = "\n".join(note_lines)

# Plot each metric
for field, label in metrics:
    fig, ax = plt.subplots(figsize=(8, 5))
    for agent in agent_types:
        y = [ rec[field] if rec[field] is not None else float('nan') 
              for rec in grouped[agent] ]
        ax.plot(av_percentages, y, marker='o', label=agent)
    ax.set_xlabel('AV Percentage')
    ax.set_ylabel(label)
    ax.set_title(f'{label} vs. AV Percentage')
    ax.grid(True)
    ax.legend(title='Agent Type')

    # Make room on the right for the note
    plt.tight_layout(rect=[0, 0, 0.75, 1])
    # Add note on the right
    fig.text(0.78, 0.5, note_text, va='center', ha='left', fontsize=8, family='monospace')

    plt.show()
