from .environment import CircularHighway
from .visualization import HighwayVisualizer
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

def main():
    # Get user input for simulation parameters
    num_vehicles, av_percentage = get_user_input()
    
    # Create the environment with user-specified parameters
    env = CircularHighway(num_vehicles=num_vehicles, track_length=1000, av_percentage=av_percentage)
    
    # Create the visualizer
    vis = HighwayVisualizer(env)
    
    # Reset the environment
    state, _ = env.reset(seed=42)
    
    print("\nSimulation running...")
    print(f"Total vehicles: {num_vehicles}")
    print(f"Autonomous vehicles: {int(num_vehicles * av_percentage)}")
    print(f"Human-driven vehicles: {num_vehicles - int(num_vehicles * av_percentage)}")
    
    try:
        # Run simulation indefinitely
        while vis.running:
            # Random actions for autonomous vehicles
            av_actions = np.random.uniform(
                env.max_deceleration,
                env.max_acceleration,
                size=env.num_av
            )
            
            # Step the environment (IDM agents will automatically determine their actions)
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