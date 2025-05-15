import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches

class HighwayVisualizer:
    def __init__(self, env):
        self.env = env
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.vehicle_patches = []
        self.speed_texts = []  # Keep track of text objects
        
        # Setup the visualization
        self.setup_plot()
        
    def setup_plot(self):
        """Initialize the plot with the circular highway."""
        self.ax.clear()
        self.vehicle_patches = []
        self.speed_texts = []  # Clear text objects list
        
        # Draw the single-lane circular highway
        radius = 150  # Base radius
        circle = plt.Circle((0, 0), radius, fill=False, color='black')
        self.ax.add_patch(circle)
        
        # Set plot limits and aspects
        plt.xlim(-200, 200)
        plt.ylim(-200, 200)
        self.ax.set_aspect('equal')
        plt.grid(True)
        
    def update(self, state):
        """Update the visualization with the current state."""
        # Remove old vehicle patches and text
        for patch in self.vehicle_patches:
            patch.remove()
        for text in self.speed_texts:
            text.remove()
        
        self.vehicle_patches = []
        self.speed_texts = []
        
        # Draw each vehicle
        for i in range(self.env.num_vehicles):
            position = state[i*2]
            speed = state[i*2 + 1]
            
            # Convert position to angle (in radians)
            angle = (position / self.env.track_length) * 2 * np.pi
            
            # Calculate vehicle position
            radius = 150  # Fixed radius for single lane
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Create vehicle patch with different colors for AV and human drivers
            color = 'blue' if i < self.env.num_av else 'red'
            vehicle = patches.Rectangle(
                (x-5, y-2.5), 10, 5,  # Position and size
                angle=np.degrees(angle) + 90,  # Angle in degrees
                color=color,  # Blue for AVs, Red for human drivers
                alpha=0.7
            )
            
            self.ax.add_patch(vehicle)
            self.vehicle_patches.append(vehicle)
            
            # Add speed indicator text
            speed_text = self.ax.text(x, y, f'{speed:.1f}', fontsize=8,
                                    horizontalalignment='center',
                                    verticalalignment='center')
            self.speed_texts.append(speed_text)
        
        # Update the plot
        self.fig.canvas.draw()
        plt.pause(0.01)

    def close(self):
        """Close the visualization window."""
        plt.close() 