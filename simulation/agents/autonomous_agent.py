import numpy as np

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

class ConsensusBasedControlAgent(AutonomousAgent):
    """
    Autonomous agent using Consensus Based Control (CBC) for multi-vehicle coordination.
    Each AV updates its acceleration based on the speed difference with all other AVs, and recovers to its desired speed.
    """
    def __init__(self, consensus_gain=0.5, recovery_gain=0.2, desired_speed=30.0, safe_distance=50, max_acceleration=3.0, max_deceleration=-5.0, track_length=1000):
        super().__init__(desired_speed=desired_speed)
        self.consensus_gain = consensus_gain
        self.recovery_gain = recovery_gain
        self.safe_distance = safe_distance
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.track_length = track_length

    @staticmethod
    def _circular_distance(pos1, pos2, track_length):
        """Compute minimum distance on a circular track."""
        return min(abs(pos1 - pos2), abs(pos1 - pos2 + track_length), abs(pos1 - pos2 - track_length))

    def get_actions(self, state, num_av):
        """
        Get actions for all autonomous vehicles using Consensus Based Control (CBC).
        Args:
            state: The full state vector [pos0, speed0, pos1, speed1, ...]
            num_av: Number of autonomous vehicles (assumed to be the first num_av vehicles)
        Returns:
            actions: np.ndarray of accelerations for each AV
        """
        actions = np.zeros(num_av)
        num_vehicles = len(state) // 2
        positions = [state[i * 2] for i in range(num_vehicles)]
        speeds = [state[i * 2 + 1] for i in range(num_vehicles)]
        for i in range(num_av):
            my_pos = positions[i]
            my_speed = speeds[i]
            # Find the leading vehicle (any type)
            min_dist = float('inf')
            idx_ahead = None
            for j in range(num_vehicles):
                if j == i:
                    continue
                dist = (positions[j] - my_pos) % self.track_length
                if 0 < dist < min_dist:
                    min_dist = dist
                    idx_ahead = j
            # Safety check: slow down if too close to the vehicle ahead
            if idx_ahead is not None and min_dist < self.safe_distance:
                actions[i] = self.max_deceleration
            else:
                # Consensus with other AVs + recovery to desired speed
                av_neighbors = [j for j in range(num_av) if j != i]
                consensus_term = 0.0
                if av_neighbors:
                    consensus_term = self.consensus_gain * sum(speeds[j] - my_speed for j in av_neighbors)
                recovery_term = self.recovery_gain * (self.desired_speed - my_speed)
                acc = consensus_term + recovery_term
                actions[i] = np.clip(acc, self.max_deceleration, self.max_acceleration)
        return actions 