import numpy as np

class IDMAgent:
    """
    Human driver agent using the Intelligent Driver Model (IDM) with realistic human behavior.
    
    Parameters:
        desired_speed: Desired velocity in m/s
        min_spacing: Minimum desired distance to leading vehicle in m
        time_headway: Desired time headway to leading vehicle in s
        acceleration: Maximum acceleration in m/s^2
        comfortable_deceleration: Comfortable deceleration in m/s^2
        delta: Acceleration exponent (usually 4)
        reaction_time: Human reaction time in seconds
        perception_noise: Standard deviation of perception noise
        behavior_noise: Standard deviation of behavioral noise
    """
    
    def __init__(self,
                 desired_speed=25.0,  # 90 km/h
                 min_spacing=2.0,
                 time_headway=1.5,
                 acceleration=1.4,
                 comfortable_deceleration=2.0,
                 delta=4,
                 reaction_time=0.5,
                 perception_noise=0.1,
                 behavior_noise=0.2):
        self.desired_speed = desired_speed
        self.min_spacing = min_spacing
        self.time_headway = time_headway
        self.acceleration = acceleration
        self.comfortable_deceleration = comfortable_deceleration
        self.delta = delta
        self.reaction_time = reaction_time
        self.perception_noise = perception_noise
        self.behavior_noise = behavior_noise
        
        # Buffer for delayed reactions
        self.speed_buffer = []
        self.lead_distance_buffer = []
        self.lead_speed_buffer = []
    
    def _add_noise(self, value, noise_level):
        """Add Gaussian noise to a value."""
        return value + np.random.normal(0, noise_level)
    
    def _get_delayed_values(self):
        """Get values from the reaction time buffer."""
        if len(self.speed_buffer) < 2:
            return self.speed_buffer[-1], self.lead_distance_buffer[-1], self.lead_speed_buffer[-1]
        
        # Get values from reaction_time seconds ago
        buffer_index = max(0, len(self.speed_buffer) - int(self.reaction_time / 0.1))
        return (self.speed_buffer[buffer_index],
                self.lead_distance_buffer[buffer_index],
                self.lead_speed_buffer[buffer_index])
    
    def act(self, speed, lead_distance=None, lead_speed=None):
        """
        Calculate acceleration using the IDM model with human-like behavior.
        
        Args:
            speed: Current speed of the vehicle in m/s
            lead_distance: Distance to leading vehicle in m (None if no leader)
            lead_speed: Speed of leading vehicle in m/s (None if no leader)
            
        Returns:
            acceleration: Calculated acceleration in m/s^2
        """
        # Add current values to buffer
        self.speed_buffer.append(speed)
        self.lead_distance_buffer.append(lead_distance)
        self.lead_speed_buffer.append(lead_speed)
        
        # Keep buffer size reasonable
        max_buffer_size = int(2.0 / 0.1)  # 2 seconds of history
        if len(self.speed_buffer) > max_buffer_size:
            self.speed_buffer.pop(0)
            self.lead_distance_buffer.pop(0)
            self.lead_speed_buffer.pop(0)
        
        # Get delayed values for reaction time simulation
        delayed_speed, delayed_lead_distance, delayed_lead_speed = self._get_delayed_values()
        
        # Add perception noise
        if delayed_lead_distance is not None:
            delayed_lead_distance = self._add_noise(delayed_lead_distance, self.perception_noise)
        if delayed_lead_speed is not None:
            delayed_lead_speed = self._add_noise(delayed_lead_speed, self.perception_noise)
        
        # Free road term
        free_road_term = 1 - (delayed_speed / self.desired_speed) ** self.delta
        
        # If no leading vehicle, accelerate freely
        if delayed_lead_distance is None or delayed_lead_speed is None:
            base_acceleration = self.acceleration * free_road_term
        else:
            # Desired minimum gap
            desired_gap = (self.min_spacing + 
                          delayed_speed * self.time_headway + 
                          (delayed_speed * (delayed_speed - delayed_lead_speed)) / 
                          (2 * np.sqrt(self.acceleration * self.comfortable_deceleration)))
            
            # Interaction term
            interaction_term = (desired_gap / delayed_lead_distance) ** 2
            
            # Calculate base acceleration
            base_acceleration = self.acceleration * (free_road_term - interaction_term)
        
        # Add behavioral noise
        final_acceleration = self._add_noise(base_acceleration, self.behavior_noise)
        
        return final_acceleration