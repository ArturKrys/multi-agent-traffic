import numpy as np
from collections import deque
import time
import matplotlib.pyplot as plt

class MetricsTracker:
    def __init__(self, track_length, num_vehicles, window_size=10):
        """
        Initialize the metrics tracker.
        
        Args:
            track_length: Length of the circular track in meters
            num_vehicles: Number of vehicles in the simulation
            window_size: Size of the rolling window for metrics calculation
        """
        self.track_length = track_length
        self.num_vehicles = num_vehicles
        self.window_size = window_size
        
        # Fixed point for traffic flow measurement (in meters from start)
        self.measurement_point = track_length / 4
        
        # Initialize metrics storage
        self.vehicle_speeds = np.zeros(num_vehicles)
        self.vehicle_positions = np.zeros(num_vehicles)
        self.last_positions = None  # Will be initialized on first update
        self.last_crossing_times = np.zeros(num_vehicles)
        self.vehicles_crossed = 0
        
        # Simulation time tracking
        self.simulation_time = 0.0
        self.last_flow_calculation_time = 0.0
        self.flow_rate_interval = 1.0  # 1 second intervals
        self.next_flow_calculation_time = 1.0  # First calculation at t=1.0
        
        # Rolling windows for metrics
        self.flow_rate_window = deque(maxlen=window_size)
        self.speed_window = deque(maxlen=window_size)
        self.speed_variance_window = deque(maxlen=window_size)
        
        # Wave detection
        self.wave_detected = False
        self.wave_start_time = None
        self.wave_end_time = None
        self.wave_formation_time = None
        self.wave_dissipation_time = None
        self.speed_threshold = 2.0
        
        # Historical data for plotting
        self.timestamps = []
        self.historical_flow_rates = []
        self.historical_avg_speeds = []
        self.historical_speed_variances = []
        self.wave_events = []  # List of (time, event_type) tuples
        
        # Track vehicles that have crossed in the current interval
        self.crossed_vehicles = set()
        
        # Initialize flow rate window with zeros
        for _ in range(window_size):
            self.flow_rate_window.append(0.0)
        
        # Flag to skip first update
        self.first_update = True
    
    def update(self, state, dt=0.1):
        """
        Update metrics based on current simulation state.
        
        Args:
            state: Current state array containing [position, speed] for each vehicle
            dt: Time step of the simulation in seconds
        """
        # Update simulation time
        self.simulation_time += dt
        
        # Extract current positions and speeds
        positions = state[::2]
        speeds = state[1::2]
        
        # Initialize last positions on first update
        if self.first_update:
            self.last_positions = positions.copy()
            self.first_update = False
            return
        
        # Calculate current metrics
        avg_speed = np.mean(speeds)
        speed_variance = np.var(speeds)
        
        # Use exponential moving average for smoother but more responsive updates
        if not self.speed_window:
            self.speed_window.append(avg_speed)
            self.speed_variance_window.append(speed_variance)
        else:
            alpha = 0.3  # Smoothing factor (0 < alpha < 1)
            self.speed_window.append(alpha * avg_speed + (1 - alpha) * self.speed_window[-1])
            self.speed_variance_window.append(alpha * speed_variance + (1 - alpha) * self.speed_variance_window[-1])
        
        # Check for vehicle crossings
        for i in range(self.num_vehicles):
            # Check if vehicle crossed measurement point
            if self.last_positions[i] > positions[i]:  # Vehicle wrapped around
                if (self.last_positions[i] < self.measurement_point or 
                    positions[i] >= self.measurement_point):
                    if i not in self.crossed_vehicles:
                        self.vehicles_crossed += 1
                        self.last_crossing_times[i] = self.simulation_time
                        self.crossed_vehicles.add(i)
            else:  # Normal crossing
                if (self.last_positions[i] < self.measurement_point and 
                    positions[i] >= self.measurement_point and
                    i not in self.crossed_vehicles):
                    self.vehicles_crossed += 1
                    self.last_crossing_times[i] = self.simulation_time
                    self.crossed_vehicles.add(i)
        
        # Update traffic flow rate (calculate at the start of each interval)
        if self.simulation_time >= self.next_flow_calculation_time:
            # Calculate flow rate (vehicles per second)
            flow_rate = self.vehicles_crossed / self.flow_rate_interval
            
            # Add to flow rate window
            self.flow_rate_window.append(flow_rate)
            
            # Store all metrics at the same time
            self.timestamps.append(self.next_flow_calculation_time)
            self.historical_flow_rates.append(flow_rate)
            self.historical_avg_speeds.append(self.speed_window[-1])
            self.historical_speed_variances.append(self.speed_variance_window[-1])
            
            # Reset counters and set next calculation time
            self.vehicles_crossed = 0
            self.last_flow_calculation_time = self.next_flow_calculation_time
            self.next_flow_calculation_time += self.flow_rate_interval
            self.crossed_vehicles.clear()
        
        # Wave detection with hysteresis
        if not self.wave_detected:
            # Check if wave is forming (significant speed variance)
            if speed_variance > self.speed_threshold:
                self.wave_detected = True
                self.wave_start_time = self.simulation_time
                self.wave_events.append((self.simulation_time, 'formation'))
        else:
            # Check if wave has dissipated (using a lower threshold for hysteresis)
            if speed_variance < (self.speed_threshold * 0.7):  # 70% of formation threshold
                self.wave_detected = False
                self.wave_end_time = self.simulation_time
                self.wave_events.append((self.simulation_time, 'dissipation'))
                if self.wave_formation_time is None:
                    self.wave_formation_time = self.wave_end_time - self.wave_start_time
                else:
                    self.wave_dissipation_time = self.wave_end_time - self.wave_start_time
        
        # Update last positions
        self.last_positions = positions.copy()
    
    def get_metrics(self):
        """Get current metrics values."""
        # Calculate average flow rate over the window
        avg_flow_rate = np.mean(list(self.flow_rate_window))
        
        return {
            'traffic_flow_rate': avg_flow_rate,
            'average_speed': self.speed_window[-1] if self.speed_window else 0,
            'speed_variance': self.speed_variance_window[-1] if self.speed_variance_window else 0,
            'wave_formation_time': self.wave_formation_time,
            'wave_dissipation_time': self.wave_dissipation_time,
            'wave_detected': self.wave_detected
        }
    
    def plot_metrics(self):
        """Plot all collected metrics."""
        if not self.timestamps:
            return

        # Create figure with subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle('Traffic Simulation Metrics', fontsize=16, y=1)  # Position title above plots
        
        # Plot flow rate with moving average
        ax1.plot(self.timestamps, self.historical_flow_rates, 'b-', label='Vehicles per Second', alpha=0.3)
        
        # Calculate and plot moving average
        window_size = min(5, len(self.historical_flow_rates))  # Reduced window size for more responsive average
        if window_size > 0:
            moving_avg = np.convolve(self.historical_flow_rates, 
                                   np.ones(window_size)/window_size, 
                                   mode='valid')
            moving_avg_times = self.timestamps[window_size-1:]
            ax1.plot(moving_avg_times, moving_avg, 'r-', label='Moving Average', linewidth=2)
        
        ax1.set_ylabel('Vehicles per Second')
        ax1.grid(True)
        ax1.legend()

        # Plot average speed
        ax2.plot(self.timestamps, self.historical_avg_speeds, 'g-')
        ax2.set_ylabel('Speed (m/s)')
        ax2.grid(True)

        # Plot speed variance
        ax3.plot(self.timestamps, self.historical_speed_variances, 'r-')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Speed Variance (m²/s²)')
        ax3.grid(True)

        # Add wave events to the plots
        for time, event_type in self.wave_events:
            color = 'red' if event_type == 'formation' else 'green'
            label = 'Wave Formation' if event_type == 'formation' else 'Wave Dissipation'
            
            # Add vertical lines to all subplots
            for ax in [ax1, ax2, ax3]:
                ax.axvline(x=time, color=color, linestyle='--', alpha=0.5)
                # Add label only to the first occurrence
                if ax == ax1:
                    ax.text(time, ax.get_ylim()[1] * 1.05, f'{label}\n({time:.1f}s)', 
                           rotation=90, verticalalignment='bottom',
                           color=color, alpha=0.7)

        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for title
        
        # Connect close event to clean up the plot
        def on_close(event):
            plt.close('all')
            
        fig.canvas.mpl_connect('close_event', on_close)
        plt.show()