import numpy as np

class IDMAgent:
    """
    Human driver agent using the Intelligent Driver Model (IDM).
    
    Parameters:
        desired_speed: Desired velocity in m/s
        min_spacing: Minimum desired distance to leading vehicle in m
        time_headway: Desired time headway to leading vehicle in s
        acceleration: Maximum acceleration in m/s^2
        comfortable_deceleration: Comfortable deceleration in m/s^2
        delta: Acceleration exponent (usually 4)
    """
    
    def __init__(self,
                 desired_speed=25.0,  # 90 km/h
                 min_spacing=2.0,
                 time_headway=1.5,
                 acceleration=1.4,
                 comfortable_deceleration=2.0,
                 delta=4):
        self.desired_speed = desired_speed
        self.min_spacing = min_spacing
        self.time_headway = time_headway
        self.acceleration = acceleration
        self.comfortable_deceleration = comfortable_deceleration
        self.delta = delta
    
    def act(self, speed, lead_distance=None, lead_speed=None):
        """
        Calculate acceleration using the IDM model.
        
        Args:
            speed: Current speed of the vehicle in m/s
            lead_distance: Distance to leading vehicle in m (None if no leader)
            lead_speed: Speed of leading vehicle in m/s (None if no leader)
            
        Returns:
            acceleration: Calculated acceleration in m/s^2
        """
        # Free road term
        free_road_term = 1 - (speed / self.desired_speed) ** self.delta
        
        # If no leading vehicle, accelerate freely
        if lead_distance is None or lead_speed is None:
            return self.acceleration * free_road_term
        
        # Desired minimum gap
        desired_gap = (self.min_spacing + 
                      speed * self.time_headway + 
                      (speed * (speed - lead_speed)) / 
                      (2 * np.sqrt(self.acceleration * self.comfortable_deceleration)))
        
        # Interaction term
        interaction_term = (desired_gap / lead_distance) ** 2
        
        # Calculate acceleration
        acceleration = self.acceleration * (free_road_term - interaction_term)
        
        return acceleration 