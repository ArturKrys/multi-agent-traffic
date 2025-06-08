import os
import json
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend for matplotlib == not displaying plots
from concurrent.futures import ProcessPoolExecutor, as_completed
import itertools
import json
import os

def run_simulation(agent, av, parameters):
    from simulation.run import main  # Import here to avoid issues with multiprocessing

    metrics = main(
        user_input=False,
        num_vehicles=parameters['num_vehicles'],
        av_percentage=av,
        position_type=parameters['position_type'],
        agent_type=agent,
        controlled_braking=parameters['controlled_braking'],
        brake_every_x_loops=parameters['brake_every_x_loops'],
        brake_duration=parameters['brake_duration'],
        brake_acceleration=parameters['brake_acceleration'],
        braking_agent_index=parameters['braking_agent_index'],
        sim_duration=parameters['sim_duration']*10, # convert to time steps
        track_length=parameters['track_length']
    )

    # Add all simulation parameters to the metrics
    metrics["simulation_parameters"] = {
        "num_vehicles": parameters['num_vehicles'],
        "av_percentage": av,
        "position_type": parameters['position_type'],
        "agent_type": agent,
        "controlled_braking": parameters['controlled_braking'],
        "brake_every_x_loops": parameters['brake_every_x_loops'],
        "brake_duration": parameters['brake_duration'],
        "brake_acceleration": parameters['brake_acceleration'],
        "braking_agent_index": parameters['braking_agent_index'],
        "sim_duration": parameters['sim_duration'],
        "track_length": parameters['track_length']
    }
    
    # Also keep backward compatibility
    metrics["av_percentage"] = av
    metrics["agent_type"] = agent
    return metrics


if __name__ == "__main__":
    # Run the simulation for all combinations of parameters
    simulation_parameters = {
        'num_vehicles': 12,
        'track_length': 1000,  # in meters
        'position_type': 'random',
        'controlled_braking': True,
        'brake_every_x_loops': 3,
        'brake_duration': 50,
        'brake_acceleration': -6.0,
        'braking_agent_index': None,
        'sim_duration': 1800 # in seconds
    }
    
    av_percentage = [0.1 * i for i in range(1, 10)]
    agent_type = ['random', 'greedy', 'consensus', 'in_the_middle']
    # agent_type = ['greedy']

    save_dir = "results"
    results = []
    os.makedirs(save_dir, exist_ok=True)

    run_in_parallel = True

    if not run_in_parallel:
        for agent in agent_type:
            for av in av_percentage:
                print(f"Running simulation with AV percentage: {av}, Agent type: {agent}")

                user_metrics = run_simulation(agent, av, simulation_parameters)
                results.append(user_metrics)
    else:
        all_combinations = list(itertools.product(agent_type, av_percentage))
        def _indexed_run(args): #needed to order results correctly just for consistency
            index, (agent, av) = args
            result = run_simulation(agent, av, simulation_parameters)
            return index, result
        results = [None] * len(all_combinations)
        with ProcessPoolExecutor() as executor:
            futures = executor.map(_indexed_run, enumerate(all_combinations))
            for index, result in futures:
                results[index] = result

    # Create a comprehensive results dictionary with metadata
    comprehensive_results = {
        "simulation_metadata": {
            "description": "Multi-agent traffic simulation results",
            "total_runs": len(results),
            "varied_parameters": ["av_percentage", "agent_type"],
            "fixed_parameters": simulation_parameters
        },
        "results": results
    }

    # Save all results to a single JSON file
    filename = f"{simulation_parameters['num_vehicles']}veh_{simulation_parameters['track_length']}m_AvPenVar_{simulation_parameters['position_type']}_AgTypeVar_{simulation_parameters['controlled_braking']}_{simulation_parameters['brake_every_x_loops']}_{simulation_parameters['brake_duration']}_{simulation_parameters['brake_acceleration']}_None_{simulation_parameters['sim_duration']}seconds.json"
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "w") as f:
        json.dump(comprehensive_results, f, indent=2)

    print(f"Results saved to: {save_path}")
    print(f"Total simulations: {len(results)}")
