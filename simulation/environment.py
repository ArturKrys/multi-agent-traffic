import numpy as np
import gymnasium as gym
from gymnasium import spaces
from .agents import IDMAgent, AutonomousAgent

class CircularHighway(gym.Env):
    """
    A single-lane circular highway environment for mixed autonomous and human-driven traffic.
    """
    
    def __init__(self, num_vehicles=8, track_length=1000, av_percentage=0.5):
        super().__init__()
        
        # Environment parameters
        self.num_vehicles = num_vehicles
        self.track_length = track_length  # Length of the circular track in meters
        self.max_speed = 33.33  # Maximum speed in m/s (approximately 120 km/h)
        self.min_speed = 16.67  # Minimum speed in m/s (approximately 60 km/h)
        self.max_acceleration = 3.0  # Maximum acceleration in m/s^2
        self.max_deceleration = -5.0  # Maximum deceleration in m/s^2
        self.braking_deceleration = -8.0  # Stronger deceleration when braking
        
        # Calculate number of autonomous vehicles
        self.num_av = int(num_vehicles * av_percentage)
        self.num_human = num_vehicles - self.num_av
        
        # Initialize agents
        self.agents = []
        for i in range(num_vehicles):
            if i < self.num_av:
                self.agents.append(AutonomousAgent())
            else:
                self.agents.append(IDMAgent())
        
        # State space: [position, speed] for each vehicle
        self.observation_space = spaces.Box(
            low=np.array([0, self.min_speed] * num_vehicles, dtype=np.float32),
            high=np.array([track_length, self.max_speed] * num_vehicles, dtype=np.float32),
            dtype=np.float32
        )
        
        # Action space: acceleration/deceleration for autonomous vehicles only
        self.action_space = spaces.Box(
            low=np.array([self.max_deceleration] * self.num_av, dtype=np.float32),
            high=np.array([self.max_acceleration] * self.num_av, dtype=np.float32),
            dtype=np.float32
        )
        
        # Initialize state and braking state
        self.braking_vehicles = set()
        self.reset()
    
    def set_braking(self, vehicle_index, is_braking):
        """Set the braking state of a vehicle."""
        if is_braking:
            self.braking_vehicles.add(vehicle_index)
        else:
            self.braking_vehicles.discard(vehicle_index)
    
    def reset(self, seed=None, options=None):
        """Reset the environment to initial state."""
        super().reset(seed=seed)
        
        # Initialize vehicles with random positions and speeds
        self.state = np.zeros(self.num_vehicles * 2)
        
        # Distribute vehicles roughly evenly around the track
        spacing = self.track_length / self.num_vehicles
        for i in range(self.num_vehicles):
            # Position with some random offset
            self.state[i*2] = (i * spacing + self.np_random.uniform(-spacing/4, spacing/4)) % self.track_length
            # Random initial speed
            self.state[i*2 + 1] = self.np_random.uniform(self.min_speed, self.max_speed)
        
        # Clear braking state
        self.braking_vehicles.clear()
        
        return self.state, {}
    
    def _get_leading_vehicle(self, index):
        """Get distance and speed of the leading vehicle."""
        pos = self.state[index*2]
        min_dist = float('inf')
        lead_speed = None
        
        for i in range(self.num_vehicles):
            if i != index:
                other_pos = self.state[i*2]
                # Calculate distance considering circular track
                dist = (other_pos - pos) % self.track_length
                if dist < min_dist:
                    min_dist = dist
                    lead_speed = self.state[i*2 + 1]
        
        return min_dist, lead_speed
    
    def step(self, av_actions=None):
        """
        Take a step in the environment. If using consensus-based AVs, compute actions internally.
        Otherwise, use provided av_actions for AVs and IDM for human drivers.
        """
        # Determine if using consensus-based control
        use_consensus = self.num_av > 0 and hasattr(self.agents[0], 'get_actions')
        
        if use_consensus:
            # Compute AV actions using consensus-based control
            av_actions = self.agents[0].get_actions(self.state, self.num_av)
        elif av_actions is not None:
            # Ensure actions are within bounds
            av_actions = np.clip(av_actions, self.max_deceleration, self.max_acceleration)
        else:
            # Fallback: random actions for AVs if none provided
            av_actions = np.random.uniform(self.max_deceleration, self.max_acceleration, size=self.num_av)

        # Calculate actions for all vehicles
        all_actions = np.zeros(self.num_vehicles)
        
        for i in range(self.num_vehicles):
            speed = self.state[i*2 + 1]
            lead_dist, lead_speed = self._get_leading_vehicle(i)
            if i in self.braking_vehicles:
                all_actions[i] = self.braking_deceleration
            elif i < self.num_av:
                all_actions[i] = av_actions[i]
            else:
                all_actions[i] = self.agents[i].act(speed, lead_dist, lead_speed)
        
        # Update speeds and positions
        dt = 0.1  # Time step in seconds
        for i in range(self.num_vehicles):
            # Update speed
            new_speed = self.state[i*2 + 1] + all_actions[i] * dt
            self.state[i*2 + 1] = np.clip(new_speed, self.min_speed, self.max_speed)
            
            # Update position
            new_position = (self.state[i*2] + self.state[i*2 + 1] * dt) % self.track_length
            self.state[i*2] = new_position
        
        # Calculate rewards (for autonomous vehicles only)
        rewards = np.zeros(self.num_av)
        for i in range(self.num_av):
            # Reward staying within desired speed range
            speed = self.state[i*2 + 1]
            target_speed = (self.max_speed + self.min_speed) / 2
            speed_reward = -abs(speed - target_speed) / self.max_speed
            
            # Penalty for being too close to other vehicles
            position = self.state[i*2]
            lead_dist, _ = self._get_leading_vehicle(i)
            distance_penalty = 0
            if lead_dist < 50:  # Safe distance threshold
                distance_penalty = -(50 - lead_dist) / 50
            
            rewards[i] = speed_reward + distance_penalty
        
        # Check for collisions
        terminated = self._check_collisions()
        truncated = False
        
        return self.state, rewards, terminated, truncated, {}
    
    def _check_collisions(self):
        """Check for collisions between vehicles."""
        vehicle_width = 10
        
        for i in range(self.num_vehicles):
            pos_i = self.state[i*2]
            for j in range(i + 1, self.num_vehicles):
                pos_j = self.state[j*2]
                # Calculate minimum distance considering circular track
                dist = min(
                    abs(pos_i - pos_j),
                    abs(pos_i - pos_j + self.track_length),
                    abs(pos_i - pos_j - self.track_length)
                )
                if dist < vehicle_width:  # Collision threshold (10 meters)
                    return True
        return False 