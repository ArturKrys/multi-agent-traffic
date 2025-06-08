from .environment import CircularHighway
from .visualization import HighwayVisualizer
from .agents import IDMAgent, ConsensusBasedControlAgent, MiddleDistanceRuleAgent, GreedyAgent, RandomAgent
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

def get_braking_parameters():
    """Get user input for controlled braking parameters."""
    print("\nControlled Braking Configuration:")
    use_controlled_braking = input("Enable controlled braking? (y/N): ").lower().startswith('y')
    
    if not use_controlled_braking:
        return False, 10, 50, -3.0, None
    
    while True:
        try:
            brake_every_x_loops = int(input("Brake every X loops through measurement point (default 3): ") or "3")
            if brake_every_x_loops < 1:
                print("Please enter a positive number.")
                continue
                
            brake_duration = int(input("Brake duration in time steps (default 50, 1 step = 0.1s): ") or "50")
            if brake_duration < 1:
                print("Please enter a positive number.")
                continue
                
            brake_acceleration = float(input("Brake acceleration in m/s² (negative value, default -6.0): ") or "-6.0")
            if brake_acceleration > 0:
                print("Brake acceleration should be negative.")
                continue
                
            agent_choice = input("Which agent should brake? (enter agent number or leave empty for first human driver): ").strip()
            braking_agent_index = None
            if agent_choice:
                braking_agent_index = int(agent_choice)
                
            return True, brake_every_x_loops, brake_duration, brake_acceleration, braking_agent_index
            
        except ValueError:
            print("Please enter valid numbers.")

def main(user_input = True, num_vehicles=None, av_percentage=None, position_type=None, agent_type=None,
         controlled_braking=None, brake_every_x_loops=None, brake_duration=None, 
         brake_acceleration=None, braking_agent_index=None, sim_duration=None):
    if user_input:
        # Get user input for simulation parameters
        num_vehicles, av_percentage, position_type, agent_type = get_user_input()
        controlled_braking, brake_every_x_loops, brake_duration, brake_acceleration, braking_agent_index = get_braking_parameters()

    # Create the environment with user-specified parameters
    if agent_type == 'consensus' or agent_type == 'in_the_middle' or agent_type == 'greedy' or agent_type == 'random':
        class IntelligentHighway(CircularHighway):
            def __init__(self, num_vehicles, track_length, av_percentage, position_type, controlled_braking=False, 
                        brake_every_x_loops=10, brake_duration=50, brake_acceleration=-3.0, 
                        braking_agent_index=None):
                super().__init__(num_vehicles, track_length, av_percentage, position_type, controlled_braking, 
                               brake_every_x_loops, brake_duration, brake_acceleration, braking_agent_index)
                self.agents = []
                self.av_indices = set()  # Initialize av_indices set
                for i in range(num_vehicles):
                    if i < self.num_av:
                        if agent_type == 'consensus':
                            self.agents.append(ConsensusBasedControlAgent())
                            self.av_indices.add(i)
                        elif agent_type == 'in_the_middle':
                            self.agents.append(MiddleDistanceRuleAgent())
                            self.av_indices.add(i)
                        elif agent_type == 'greedy':
                            self.agents.append(GreedyAgent())
                            self.av_indices.add(i)
                        else:  # random
                            self.agents.append(RandomAgent())
                            self.av_indices.add(i)
                    else:
                        self.agents.append(IDMAgent())
        env = IntelligentHighway(num_vehicles=num_vehicles, track_length=1000, av_percentage=av_percentage, position_type=position_type,
                               controlled_braking=controlled_braking, brake_every_x_loops=brake_every_x_loops,
                               brake_duration=brake_duration, brake_acceleration=brake_acceleration,
                               braking_agent_index=braking_agent_index)
        av_agent_name = {
            'consensus': "Consensus-Based Control",
            'in_the_middle': "In-the-middle Rule Control",
            'greedy': "Greedy Control",
            'random': "Random Control"
        }[agent_type]
    else:
        env = CircularHighway(num_vehicles=num_vehicles, track_length=1000, av_percentage=av_percentage, position_type=position_type,
                            controlled_braking=controlled_braking, brake_every_x_loops=brake_every_x_loops,
                            brake_duration=brake_duration, brake_acceleration=brake_acceleration,
                            braking_agent_index=braking_agent_index)
        av_agent_name = "Random" if agent_type == 'random' else "Greedy (proportional control)"

    # Create the visualizer
    vis = HighwayVisualizer(env)
    if not user_input:
        vis.plot_graphs = False
    
    # Reset the environment
    state, _ = env.reset(seed=42)
    
    print("\nSimulation running...")
    print(f"Total vehicles: {num_vehicles}")
    print(f"Autonomous vehicles: {int(num_vehicles * av_percentage)}")
    print(f"Human-driven vehicles: {num_vehicles - int(num_vehicles * av_percentage)}")
    print(f"AV agent type: {av_agent_name}")
    
    if controlled_braking:
        braking_status = env.get_braking_status()
        print(f"\nControlled Braking Enabled:")
        print(f"  Braking agent: {braking_status['braking_agent']}")
        print(f"  Brake every {braking_status['brake_every_x_loops']} loops")
        print(f"  Brake duration: {braking_status['brake_duration']} steps ({braking_status['brake_duration'] * 0.1:.1f}s)")
        print(f"  Brake acceleration: {braking_status['brake_acceleration']} m/s²")
    
    try:
        # Run simulation
        step_count = 0
        max_steps = sim_duration if sim_duration is not None else None
        
        while vis.running:
            if agent_type in ['consensus', 'in_the_middle', 'greedy', 'random']:
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
            
            step_count += 1
            
            # Check time-based termination (for non-interactive mode)
            if max_steps is not None and step_count >= max_steps:
                break
            
            # Update visualization
            if not vis.update(state):
                break
            
            if terminated or truncated:
                print("Collision detected! Closing simulation...")
                break
                
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    finally:
        return vis.close()

if __name__ == "__main__":
    main() 