import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
import sys

class HighwayVisualizer:
    def __init__(self, env):
        self.env = env
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.vehicle_patches = []
        self.speed_texts = []  # Keep track of text objects
        self.braking_vehicles = set()  # Track which vehicles are braking
        self.running = True  # Flag to control simulation loop
        
        # Setup the visualization
        self.setup_plot()
        
        # Connect the pick event
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        # Connect close event
        self.fig.canvas.mpl_connect('close_event', self.on_close)
        
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
        
    def on_close(self, event):
        """Handle window closing."""
        self.running = False
        self.fig.canvas.stop_event_loop()
        plt.close(self.fig)
        sys.exit(0)  # Exit the program
        
    def on_pick(self, event):
        """Handle pick events when a vehicle is clicked."""
        if event.artist in self.vehicle_patches:
            # Get the index of the clicked vehicle
            i = self.vehicle_patches.index(event.artist)
            
            # Toggle braking state
            is_braking = i not in self.braking_vehicles
            self.env.set_braking(i, is_braking)
            
            if is_braking:
                self.braking_vehicles.add(i)
                event.artist.set_color('#FF0000')  # Bright red for braking
            else:
                self.braking_vehicles.remove(i)
                event.artist.set_color('#0066CC' if i < self.env.num_av else '#FFA500')  # Blue for AVs, Orange for IDM
            self.fig.canvas.draw()
    
    def update(self, state):
        """Update the visualization with the current state."""
        if not self.running:
            return False
            
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
            
            # Calculate acceleration for this vehicle
            lead_dist, lead_speed = self.env._get_leading_vehicle(i)
            if i in self.env.braking_vehicles:
                acceleration = self.env.braking_deceleration
            elif i < self.env.num_av:
                # For autonomous vehicles, we don't have direct access to their actions
                # So we'll show a placeholder
                acceleration = 0.0
            else:
                # For human drivers, calculate using IDM
                acceleration = self.env.agents[i].act(speed, lead_dist, lead_speed)
            
            # Convert position to angle (in radians)
            angle = (position / self.env.track_length) * 2 * np.pi
            
            # Calculate vehicle position using the same radius as the track
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Create vehicle patch with different colors for AV and human drivers
            if i in self.env.braking_vehicles:
                color = '#FF0000'  # Bright red for braking
            else:
                color = '#0066CC' if i < self.env.num_av else '#FFA500'  # Blue for AVs, Orange for IDM
            vehicle_width = 10
            vehicle_height = 5
            
            # Create vehicle patch centered at (x,y)
            vehicle = patches.Rectangle(
                (x - vehicle_width/2, y - vehicle_height/2),  # Center the rectangle
                vehicle_width, vehicle_height,
                angle=np.degrees(angle) + 90,  # Angle in degrees
                rotation_point='center',  # Rotate around center
                color=color,
                alpha=0.7,
                picker=True  # Make the vehicle clickable
            )
            
            self.ax.add_patch(vehicle)
            self.vehicle_patches.append(vehicle)
            
            # Add speed and acceleration indicator text
            # Calculate offset position for text (to the side of the vehicle)
            text_offset = 15  # Distance from vehicle center
            text_x = x + text_offset * np.cos(angle)  # Parallel to vehicle direction
            text_y = y + text_offset * np.sin(angle)
            
            # Format the text to show both speed and acceleration
            info_text = f'v: {speed:.1f}\na: {acceleration:.1f}'
            speed_text = self.ax.text(text_x, text_y, info_text, fontsize=8,
                                    horizontalalignment='center',
                                    verticalalignment='center')
            self.speed_texts.append(speed_text)
        
        # Update the plot
        self.fig.canvas.draw()
        plt.pause(0.01)
        return self.running

    def close(self):
        """Close the visualization window."""
        self.running = False
        self.fig.canvas.stop_event_loop()
        plt.close(self.fig) 