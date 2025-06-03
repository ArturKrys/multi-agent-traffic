from .environment import CircularHighway
from .visualization import HighwayVisualizer
from .agents import AutonomousAgent, ConsensusBasedControlAgent
import numpy as np
import keyboard

def get_user_input():
    """Get user input for simulation parameters."""
    while True:
        try:
            num_vehicles = int(input("Enter the number of vehicles (recommended: 4-12): "))
            if num_vehicles < 2:
                print("Please enter at least 2 vehicles.")
                continue
            if num_vehicles > 20:
                print("Warning: Large number of vehicles may affect performance.")
            
            av_percentage = float(input("Enter the percentage of autonomous vehicles (0 to 100): "))
            if not 0 <= av_percentage <= 100:
                print("Please enter a value between 0 and 100.")
                continue
            
            # Convert percentage to decimal
            av_percentage = av_percentage / 100
            
            return num_vehicles, av_percentage
        except ValueError:
            print("Please enter valid numbers.")

def get_agent_type():
    print("Select AV agent type:")
    print("1. Random (default)")
    print("2. Greedy (proportional control)")
    print("3. Consensus-Based Control")
    choice = input("Enter choice [1-3]: ").strip()
    if choice == '3':
        return 'consensus'
    elif choice == '2':
        return 'greedy'
    else:
        return 'random'

def main():
    # Get user input for simulation parameters
    num_vehicles, av_percentage = get_user_input()
    agent_type = get_agent_type()

    # Create the environment with user-specified parameters
    if agent_type == 'consensus':
        # Use ConsensusBasedControlAgent for all AVs
        from .environment import CircularHighway
        from .agents import IDMAgent
        class ConsensusHighway(CircularHighway):
            def __init__(self, num_vehicles, track_length, av_percentage):
                super().__init__(num_vehicles, track_length, av_percentage)
                self.agents = []
                for i in range(num_vehicles):
                    if i < self.num_av:
                        self.agents.append(ConsensusBasedControlAgent())
                    else:
                        self.agents.append(IDMAgent())
        env = ConsensusHighway(num_vehicles=num_vehicles, track_length=1000, av_percentage=av_percentage)
        av_agent_name = "Consensus-Based Control"
    else:
        env = CircularHighway(num_vehicles=num_vehicles, track_length=1000, av_percentage=av_percentage)
        av_agent_name = "Random" if agent_type == 'random' else "Greedy (proportional control)"

    # Create the visualizer
    vis = HighwayVisualizer(env)
    
    # Reset the environment
    state, _ = env.reset(seed=42)
    
    print("\nSimulation running...")
    print(f"Total vehicles: {num_vehicles}")
    print(f"Autonomous vehicles: {int(num_vehicles * av_percentage)}")
    print(f"Human-driven vehicles: {num_vehicles - int(num_vehicles * av_percentage)}")
    print(f"AV agent type: {av_agent_name}")
    
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