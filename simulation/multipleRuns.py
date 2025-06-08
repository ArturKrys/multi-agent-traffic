import os
import json
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend for matplotlib == not displaying plots
from concurrent.futures import ProcessPoolExecutor, as_completed
import itertools
import json
import os

def run_simulation(agent, av):
    from simulation.run import main  # Import here to avoid issues with multiprocessing

    metrics = main(
        user_input=False,
        num_vehicles=num_vehicles,
        av_percentage=av,
        position_type=position_type,
        agent_type=agent,
        controlled_braking=controlled_braking,
        brake_every_x_loops=brake_every_x_loops,
        brake_duration=brake_duration,
        brake_acceleration=brake_acceleration,
        braking_agent_index=braking_agent_index,
        sim_duration=sim_duration*10 # convert to time steps
    )

    metrics["av_percentage"] = av
    metrics["agent_type"] = agent
    return metrics


if __name__ == "__main__":
    # Run the simulation for all combinations of parameters
    num_vehicles = 12
    av_percentage = [0.1 * i for i in range(1, 10)]
    position_type = 'random'
    agent_type = ['random', 'greedy', 'consensus', 'in_the_middle']
    # agent_type = ['greedy']

    controlled_braking = True
    brake_every_x_loops = 3
    brake_duration = 50
    brake_acceleration = -6.0
    braking_agent_index = None

    sim_duration = 50 # in seconds
    save_dir = "results"
    results = []
    os.makedirs(save_dir, exist_ok=True)

    run_in_parallel = True

    if not run_in_parallel:
        for agent in agent_type:
            for av in av_percentage:
                print(f"Running simulation with AV percentage: {av}, Agent type: {agent}")

                user_metrics = run_simulation(agent, av)
                results.append(user_metrics)
    else:
        all_combinations = list(itertools.product(agent_type, av_percentage))
        def _indexed_run(args): #needed to order results correctly just for consistency
            index, (agent, av) = args
            result = run_simulation(agent, av)
            return index, result
        results = [None] * len(all_combinations)
        with ProcessPoolExecutor() as executor:
            futures = executor.map(_indexed_run, enumerate(all_combinations))
            for index, result in futures:
                results[index] = result

    # Save all results to a single JSON file
    filename = f"{num_vehicles}_AvPenVar_{position_type}_AgTypeVar_{controlled_braking}_{brake_every_x_loops}_{brake_duration}_{brake_acceleration}_None_{sim_duration}seconds.json"
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "w") as f:
        json.dump(results, f, indent=2)
