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
        radius = self.env.track_length / (2 * np.pi)  # Base radius calculated from track length
        circle = plt.Circle((0, 0), radius, fill=False, color='black')
        self.ax.add_patch(circle)
        
        # Set plot limits and aspects
        limit = radius + 50  # Add some padding
        plt.xlim(-limit, limit)
        plt.ylim(-limit, limit)
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
        
        # Calculate radius once
        radius = self.env.track_length / (2 * np.pi)
        
        # Draw each vehicle
        for i in range(self.env.num_vehicles):
            position = state[i*2]
            speed = state[i*2 + 1]
            
            # Convert position to angle (in radians)
            angle = (position / self.env.track_length) * 2 * np.pi
            
            # Calculate vehicle position using the same radius as the track
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Create vehicle patch with different colors for AV and human drivers
            color = 'blue' if i < self.env.num_av else 'red'
            vehicle_width = 10
            vehicle_height = 5
            
            # Create vehicle patch centered at (x,y)
            vehicle = patches.Rectangle(
                (x - vehicle_width/2, y - vehicle_height/2),  # Center the rectangle
                vehicle_width, vehicle_height,
                angle=np.degrees(angle) + 90,  # Angle in degrees
                rotation_point='center',  # Rotate around center
                color=color,
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