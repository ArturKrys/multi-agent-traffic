class AutonomousAgent:
    """
    Base class for autonomous vehicle agents.
    Different control strategies can be implemented by subclassing this class.
    """
    
    def __init__(self, desired_speed=30.0):  # 108 km/h
        self.desired_speed = desired_speed
    
    def act(self, speed, lead_distance=None, lead_speed=None):
        """
        Calculate acceleration based on current state.
        This is a simple placeholder implementation.
        Subclasses should implement their own control strategies.
        
        Args:
            speed: Current speed of the vehicle in m/s
            lead_distance: Distance to leading vehicle in m (None if no leader)
            lead_speed: Speed of leading vehicle in m/s (None if no leader)
            
        Returns:
            acceleration: Calculated acceleration in m/s^2
        """
        # Simple proportional control to maintain desired speed
        return 2.0 * (self.desired_speed - speed) 