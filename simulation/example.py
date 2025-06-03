from .environment import CircularHighway
from .visualization import HighwayVisualizer
from .agents import AutonomousAgent, ConsensusBasedControlAgent
from .agent_factory import AgentFactory
import numpy as np
import keyboard

def get_user_input():
    """Get user input for simulation parameters."""
    # Get number of vehicles
    while True:
        try:
            num_vehicles = int(input("Enter the number of vehicles (recommended: 4-12): "))
            if num_vehicles < 2:
                print("Please enter at least 2 vehicles.")
                continue
            if num_vehicles > 20:
                print("Warning: Large number of vehicles may affect performance.")
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Get autonomous vehicle percentage
    while True:
        try:
            av_percentage = float(input("Enter the percentage of autonomous vehicles (0 to 100): "))
            if not 0 <= av_percentage <= 100:
                print("Please enter a value between 0 and 100.")
                continue
            av_percentage = av_percentage / 100  # Convert to decimal
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Get AV positioning
    while True:
        print("\nSelect AV positioning:")
        print("1. Interleaved (AVs and human vehicles alternate)")
        print("2. Grouped (AVs stay together)")
        print("3. Random")
        position_choice = input("Enter choice [1-3]: ").strip()
        if position_choice in ['1', '2', '3']:
            position_type = 'interleaved' if position_choice == '1' else 'grouped' if position_choice == '2' else 'random'
            break
        print("Please enter a valid choice (1, 2, or 3).")
    
    # Get agent type
    available_agents = AgentFactory.get_available_agent_types()
    while True:
        print("\nSelect AV agent type:")
        for i, agent_type in enumerate(available_agents, 1):
            print(f"{i}. {agent_type.capitalize()}")
        agent_choice = input(f"Enter choice [1-{len(available_agents)}]: ").strip()
        if agent_choice.isdigit() and 1 <= int(agent_choice) <= len(available_agents):
            agent_type = available_agents[int(agent_choice) - 1]
            break
        print(f"Please enter a valid choice (1-{len(available_agents)}).")
    
    return num_vehicles, av_percentage, position_type, agent_type

def main():
    # Get user input for simulation parameters
    num_vehicles, av_percentage, position_type, agent_type = get_user_input()

    # Create the environment with user-specified parameters
    env = CircularHighway(
        num_vehicles=num_vehicles,
        track_length=1000,
        av_percentage=av_percentage,
        position_type=position_type,
        agent_type=agent_type
    )

    # Create the visualizer
    vis = HighwayVisualizer(env)
    
    # Reset the environment
    state, _ = env.reset(seed=42)
    
    print("\nSimulation running...")
    print(f"Total vehicles: {num_vehicles}")
    print(f"Autonomous vehicles: {int(num_vehicles * av_percentage)}")
    print(f"Human-driven vehicles: {num_vehicles - int(num_vehicles * av_percentage)}")
    print(f"AV agent type: {agent_type.capitalize()}")
    
    try:
        # Run simulation indefinitely
        while vis.running:
            if agent_type == 'consensus':
                # No need to provide actions; environment computes them
                state, rewards, terminated, truncated, _ = env.step()
            else:
                # Random or greedy actions for autonomous vehicles
                av_actions = np.random.uniform(
                    env.max_deceleration,
                    env.max_acceleration,
                    size=env.num_av
                )
                state, rewards, terminated, truncated, _ = env.step(av_actions)
            
            # Update visualization
            if not vis.update(state):
                break
            
            if terminated or truncated:
                print("Collision detected! Closing simulation...")
                break
                
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    finally:
        vis.close()

if __name__ == "__main__":
    main() 