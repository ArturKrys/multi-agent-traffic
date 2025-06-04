from .environment import CircularHighway
from .visualization import HighwayVisualizer
from .agents import IDMAgent, ConsensusBasedControlAgent, MiddleDistanceRuleAgent
import numpy as np

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
    while True:
        print("\nSelect AV agent type:")
        print("1. Random (default)")
        print("2. Greedy (proportional control)")
        print("3. Consensus-Based Control")
        print("4. In-the-middle Rule Control")
        agent_choice = input("Enter choice [1-4]: ").strip()
        if agent_choice == '4':
            agent_type = 'in_the_middle'
            break
        elif agent_choice == '3':
            agent_type = 'consensus'
            break
        elif agent_choice == '2':
            agent_type = 'greedy'
            break
        elif agent_choice == '1':
            agent_type = 'random'
            break
        else:
            print("Please enter a valid choice (1, 2, 3, 4).")
    
    return num_vehicles, av_percentage, position_type, agent_type

def main():
    # Get user input for simulation parameters
    num_vehicles, av_percentage, position_type, agent_type = get_user_input()

    # Create the environment with user-specified parameters
    if agent_type == 'consensus' or agent_type == 'in_the_middle':
        class IntelligentHighway(CircularHighway):
            def __init__(self, num_vehicles, track_length, av_percentage, position_type):
                super().__init__(num_vehicles, track_length, av_percentage, position_type)
                self.agents = []
                self.av_indices = set()  # Initialize av_indices set
                for i in range(num_vehicles):
                    if i < self.num_av:
                        if agent_type == 'consensus':
                            self.agents.append(ConsensusBasedControlAgent())
                            self.av_indices.add(i)
                        else:
                            self.agents.append(MiddleDistanceRuleAgent())
                            self.av_indices.add(i)
                    else:
                        self.agents.append(IDMAgent())
        env = IntelligentHighway(num_vehicles=num_vehicles, track_length=1000, av_percentage=av_percentage, position_type=position_type)
        av_agent_name = "Consensus-Based Control" if agent_type == 'consensus' else "In-the-middle Rule Control"
    else:
        env = CircularHighway(num_vehicles=num_vehicles, track_length=1000, av_percentage=av_percentage, position_type=position_type)
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
            if agent_type == 'consensus' or agent_type == 'in_the_middle':
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