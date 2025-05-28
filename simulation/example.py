from .environment import CircularHighway
from .visualization import HighwayVisualizer
import numpy as np
import keyboard

def main():
    # Create the environment with 8 vehicles, 50% autonomous
    env = CircularHighway(num_vehicles=8, track_length=1000, av_percentage=0.5)
    
    # Create the visualizer
    vis = HighwayVisualizer(env)
    
    # Reset the environment
    state, _ = env.reset(seed=42)
    
    print("Simulation running... Press 'q' to quit")
    
    try:
        # Run simulation indefinitely
        while True:
            # Random actions for autonomous vehicles
            av_actions = np.random.uniform(
                env.max_deceleration,
                env.max_acceleration,
                size=env.num_av
            )
            
            # Step the environment (IDM agents will automatically determine their actions)
            state, rewards, terminated, truncated, _ = env.step(av_actions)
            
            # Update visualization
            vis.update(state)
            
            if terminated or truncated:
                print("Collision detected! Closing simulation...")
                break
            
            # Check for quit key
            if keyboard.is_pressed('q'):
                print("Simulation stopped by user")
                break
                
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    finally:
        vis.close()

if __name__ == "__main__":
    main() 