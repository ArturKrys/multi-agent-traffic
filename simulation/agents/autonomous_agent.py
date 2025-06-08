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

class MiddleDistanceRuleAgent(AutonomousAgent):
    """
    Rule‐based agent that tries to stay in the middle between the car in front and behind.
    - Dynamically computes braking_distance = v^2 / (2 * |max_deceleration|) each timestep.
    - If front_gap < braking_distance, apply max_deceleration (hard brake).
    - If front_gap > 2 * braking_distance, just target desired_speed.
    - Otherwise, use a proportional “middle‐distance” law.
    """

    def __init__(
        self,
        desired_speed=30.0,
        max_acceleration=2.0,
        max_deceleration=-5.0,
        track_length=1000
    ):
        super().__init__(desired_speed)
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration  # negative number, e.g. -5.0
        self.track_length = track_length

    @staticmethod
    def _circular_distance(pos1, pos2, track_length):
        """Compute forward distance from pos1 to pos2 on a circular track."""
        return (pos2 - pos1) % track_length

    def get_actions(self, state, num_av):
        """
        For each AV (indices 0..num_av-1), compute its acceleration based on dynamic
        braking distance and middle-distance rule.

        Args:
            state: [pos0, speed0, pos1, speed1, …, posN, speedN]
            num_av: number of AVs (assumed to occupy indices 0..num_av-1)

        Returns:
            actions: np.ndarray of length num_av, containing one accel for each AV.
        """
        num_vehicles = len(state) // 2
        positions = [state[2*i] for i in range(num_vehicles)]
        speeds    = [state[2*i+1] for i in range(num_vehicles)]
        actions = np.zeros(num_av)

        for i in range(num_av):
            my_pos   = positions[i]
            my_speed = speeds[i]

            # 1) Compute dynamic braking distance for this AV:
            #    d_b = v^2 / (2 * |a_max|)
            a_max = abs(self.max_deceleration)
            
            braking_dist = (my_speed**2) / (2.0 * a_max)

            # 2) Find nearest front_gap and back_gap (circular)
            min_front_gap = float('inf')
            min_back_gap  = float('inf')
            front_idx = None
            back_idx  = None

            for j in range(num_vehicles):
                if j == i:
                    continue
                gap_forward = (positions[j] - my_pos) % self.track_length
                if 0 < gap_forward < min_front_gap:
                    min_front_gap = gap_forward
                    front_idx = j

                gap_backward = (my_pos - positions[j]) % self.track_length
                if 0 < gap_backward < min_back_gap:
                    min_back_gap = gap_backward
                    back_idx = j

            # 3) SAFETY BRAKE if too close to front
            if front_idx is not None and min_front_gap < braking_dist:
                # apply hardest braking immediately
                acc = self.max_deceleration

            else:
                # 4) If front is "very far" (> 2 * braking_dist), just recover to desired speed
                if front_idx is not None and min_front_gap > 2.0 * braking_dist:
                    # simple P‐control on speed
                    gain_speed = 1.5
                    acc = gain_speed * (self.desired_speed - my_speed)

                else:
                    # 5) Otherwise, use “stay-in-the-middle” between front & back
                    #    If no front_idx (e.g. single vehicle), treat front_gap as very large:
                    front_gap = min_front_gap if front_idx is not None else (2.0 * braking_dist)
                    #    If no back_idx, treat back_gap = front_gap (so target_distance = front_gap)
                    back_gap  = min_back_gap  if back_idx  is not None else front_gap

                    target_dist = 0.5 * (front_gap + back_gap)
                    dist_error  = target_dist - back_gap

                    # P‐controller on distance + P on speed difference
                    k_p_dist  = 0.1
                    k_p_speed = 0.3
                    acc = k_p_dist  * dist_error \
                        + k_p_speed * (self.desired_speed - my_speed)

            # 6) Clip to [max_deceleration, max_acceleration]
            if acc > self.max_acceleration:
                acc = self.max_acceleration
            if acc < self.max_deceleration:
                acc = self.max_deceleration

            actions[i] = acc

        return actions

class GreedyAgent(AutonomousAgent):
    """
    A greedy agent that tries to maximize its speed while maintaining safety.
    - Always tries to accelerate to maximum speed
    - Only brakes when necessary to avoid collision
    - Tries to match the speed of the vehicle ahead when close
    """
    
    def __init__(
        self,
        desired_speed=30.0,
        max_acceleration=3.0,
        max_deceleration=-5.0,
        track_length=1000,
        safety_margin=20.0  # Minimum safe distance in meters
    ):
        super().__init__(desired_speed)
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.track_length = track_length
        self.safety_margin = safety_margin

    @staticmethod
    def _circular_distance(pos1, pos2, track_length):
        """Compute forward distance from pos1 to pos2 on a circular track."""
        return (pos2 - pos1) % track_length

    def get_actions(self, state, num_av):
        """
        For each AV, compute acceleration based on greedy strategy:
        - Accelerate as much as possible
        - Only brake when necessary to avoid collision
        - Try to match speed of vehicle ahead when close

        Args:
            state: [pos0, speed0, pos1, speed1, …, posN, speedN]
            num_av: number of AVs (assumed to occupy indices 0..num_av-1)

        Returns:
            actions: np.ndarray of length num_av, containing one accel for each AV.
        """
        num_vehicles = len(state) // 2
        positions = [state[2*i] for i in range(num_vehicles)]
        speeds = [state[2*i+1] for i in range(num_vehicles)]
        actions = np.zeros(num_av)

        for i in range(num_av):
            my_pos = positions[i]
            my_speed = speeds[i]

            # Find the vehicle ahead
            min_front_gap = float('inf')
            front_idx = None
            front_speed = None

            for j in range(num_vehicles):
                if j == i:
                    continue
                gap_forward = (positions[j] - my_pos) % self.track_length
                if 0 < gap_forward < min_front_gap:
                    min_front_gap = gap_forward
                    front_idx = j
                    front_speed = speeds[j]

            # Default to maximum acceleration
            acc = self.max_acceleration

            if front_idx is not None:
                # If we're too close to the vehicle ahead, we need to brake
                if min_front_gap < self.safety_margin:
                    # Emergency braking
                    acc = self.max_deceleration
                # If we're close but not too close, try to match speed
                elif min_front_gap < 2 * self.safety_margin:
                    # Match speed of vehicle ahead with some margin
                    speed_diff = front_speed - my_speed
                    if speed_diff > 0:
                        # Vehicle ahead is faster, accelerate to match
                        acc = min(self.max_acceleration, speed_diff * 2.0)
                    else:
                        # Vehicle ahead is slower, brake to match
                        acc = max(self.max_deceleration, speed_diff * 2.0)
                # If we're far enough, accelerate to desired speed
                else:
                    acc = min(self.max_acceleration, 2.0 * (self.desired_speed - my_speed))

            # Clip acceleration to valid range
            actions[i] = np.clip(acc, self.max_deceleration, self.max_acceleration)

        return actions

class RandomAgent(AutonomousAgent):
    """
    An agent that chooses random actions within safe acceleration limits.
    Each agent independently selects a random acceleration value between max_deceleration and max_acceleration.
    """
    
    def __init__(
        self,
        desired_speed=30.0,
        max_acceleration=3.0,
        max_deceleration=-5.0,
        track_length=1000
    ):
        super().__init__(desired_speed)
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.track_length = track_length

    def get_actions(self, state, num_av):
        """
        Generate random actions for each autonomous vehicle.
        
        Args:
            state: [pos0, speed0, pos1, speed1, …, posN, speedN]
            num_av: number of AVs (assumed to occupy indices 0..num_av-1)
            
        Returns:
            actions: np.ndarray of length num_av, containing random accelerations for each AV
        """
        # Generate random actions between max_deceleration and max_acceleration
        actions = np.random.uniform(
            low=self.max_deceleration,
            high=self.max_acceleration,
            size=num_av
        )
        return actions
