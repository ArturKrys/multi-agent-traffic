import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
from .metrics import MetricsTracker

class HighwayVisualizer:
    def __init__(self, env):
        self.env = env
        self.fig = plt.figure(figsize=(15, 10))
        
        # Create subplots for highway and metrics
        self.ax_highway = self.fig.add_subplot(121)
        self.ax_metrics = self.fig.add_subplot(122)
        
        self.vehicle_patches = []
        self.speed_texts = []
        self.braking_vehicles = set()
        self.running = True
        
        # Initialize metrics tracker
        self.metrics_tracker = MetricsTracker(env.track_length, env.num_vehicles)
        
        # Setup the visualization
        self.setup_plot()
        
        # Connect the pick event
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        # Connect close event
        self.fig.canvas.mpl_connect('close_event', self.on_close)
        
    def setup_plot(self):
        """Initialize the plot with the circular highway and metrics display."""
        # Setup highway plot
        self.ax_highway.clear()
        self.vehicle_patches = []
        self.speed_texts = []
        
        # Draw the single-lane circular highway
        radius = self.env.track_length / (2 * np.pi)
        circle = plt.Circle((0, 0), radius, fill=False, color='black')
        self.ax_highway.add_patch(circle)
        
        # Draw measurement point
        measurement_angle = (self.metrics_tracker.measurement_point / self.env.track_length) * 2 * np.pi
        measurement_x = radius * np.cos(measurement_angle)
        measurement_y = radius * np.sin(measurement_angle)
        measurement_point = plt.Circle((measurement_x, measurement_y), 5, color='red', alpha=0.5)
        self.ax_highway.add_patch(measurement_point)
        
        # Add measurement point label
        label_offset = 20
        label_x = measurement_x + label_offset * np.cos(measurement_angle)
        label_y = measurement_y + label_offset * np.sin(measurement_angle)
        self.ax_highway.text(label_x, label_y, 'Flow\nMeasurement\nPoint', 
                           horizontalalignment='center',
                           verticalalignment='center',
                           color='red',
                           fontsize=8)
        
        # Set plot limits and aspects
        limit = radius + 50
        self.ax_highway.set_xlim(-limit, limit)
        self.ax_highway.set_ylim(-limit, limit)
        self.ax_highway.set_aspect('equal')
        self.ax_highway.grid(True)
        self.ax_highway.set_title('Circular Highway')
        
        # Setup metrics plot
        self.ax_metrics.clear()
        self.ax_metrics.set_title('Traffic Metrics')
        self.ax_metrics.axis('off')
        
    def update_metrics_display(self):
        """Update the metrics display with current values."""
        self.ax_metrics.clear()
        self.ax_metrics.axis('off')
        
        metrics = self.metrics_tracker.get_metrics()
        
        # Format metrics text
        metrics_text = (
            f"Traffic Flow Rate: {metrics['traffic_flow_rate']:.2f} veh/s\n"
            f"Average Speed: {metrics['average_speed']:.2f} m/s\n"
            f"Speed Variance: {metrics['speed_variance']:.2f} m²/s²\n"
        )
        
        if metrics['wave_formation_time'] is not None:
            metrics_text += f"Wave Formation Time: {metrics['wave_formation_time']:.2f} s\n"
        if metrics['wave_dissipation_time'] is not None:
            metrics_text += f"Wave Dissipation Time: {metrics['wave_dissipation_time']:.2f} s\n"
        
        if metrics['wave_detected']:
            metrics_text += "\nStatus: Traffic Wave Detected"
        
        # Display metrics
        self.ax_metrics.text(0.1, 0.9, metrics_text,
                           transform=self.ax_metrics.transAxes,
                           verticalalignment='top',
                           fontsize=10,
                           family='monospace')
    
    def on_close(self, event):
        """Handle window closing."""
        print("\nSimulation stopped by user")
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources and close the visualization."""
        if not self.running:  # Prevent multiple cleanup calls
            return
            
        self.running = False
        
        # Stop the event loop
        try:
            self.fig.canvas.stop_event_loop()
        except Exception:
            pass
            
        # Close the figure
        try:
            plt.close(self.fig)
        except Exception:
            pass
            
    def on_pick(self, event):
        """Handle pick events when a vehicle is clicked."""
        if event.artist in self.vehicle_patches:
            i = self.vehicle_patches.index(event.artist)
            is_braking = i not in self.braking_vehicles
            self.env.set_braking(i, is_braking)
            
            if is_braking:
                self.braking_vehicles.add(i)
                event.artist.set_color('#FF0000')
            else:
                self.braking_vehicles.remove(i)
                event.artist.set_color('#0066CC' if i in self.env.av_indices else '#FFA500')
            self.fig.canvas.draw()
    
    def update(self, state):
        """Update the visualization with the current state."""
        if not self.running:
            return False
            
        # Update metrics
        self.metrics_tracker.update(state)
        
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
            elif i in self.env.av_indices:
                acceleration = 0.0
            else:
                acceleration = self.env.agents[i].act(speed, lead_dist, lead_speed)
            
            # Convert position to angle (in radians)
            angle = (position / self.env.track_length) * 2 * np.pi
            
            # Calculate vehicle position
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Create vehicle patch
            if i in self.env.braking_vehicles:
                color = '#FF0000'  # Red for braking
            else:
                color = '#0066CC' if i in self.env.av_indices else '#FFA500'  # Blue for AVs, Orange for humans
            
            vehicle_width = 10
            vehicle_height = 5
            
            vehicle = patches.Rectangle(
                (x - vehicle_width/2, y - vehicle_height/2),
                vehicle_width, vehicle_height,
                angle=np.degrees(angle) + 90,
                rotation_point='center',
                color=color,
                alpha=0.7,
                picker=True
            )
            
            self.ax_highway.add_patch(vehicle)
            self.vehicle_patches.append(vehicle)
            
            # Add speed and acceleration indicator text
            text_offset = 15
            text_x = x + text_offset * np.cos(angle)
            text_y = y + text_offset * np.sin(angle)
            
            info_text = f'v: {speed:.1f}\na: {acceleration:.1f}'
            speed_text = self.ax_highway.text(text_x, text_y, info_text, fontsize=8,
                                            horizontalalignment='center',
                                            verticalalignment='center')
            self.speed_texts.append(speed_text)
        
        # Update metrics display
        self.update_metrics_display()
        
        # Update the plot
        self.fig.canvas.draw()
        plt.pause(0.01)
        return self.running

    def close(self):
        """Close the visualization window and show metrics plot."""
        self.cleanup()
        
        # Show metrics plot
        self.metrics_tracker.plot_metrics() 