import numpy as np
import gymnasium as gym
from gymnasium import spaces
from .agents import IDMAgent, AutonomousAgent
from .agent_factory import AgentFactory

class CircularHighway(gym.Env):
    """
    A single-lane circular highway environment for mixed autonomous and human-driven traffic.
    """
    
    def __init__(self, num_vehicles=8, track_length=1000, av_percentage=0.5, position_type='random', agent_type='random'):
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
        
        # Store position type and agent type
        self.position_type = position_type
        self.agent_type = agent_type
        
        # Initialize agents and state using the factory
        self.agents, self.av_indices = AgentFactory.create_agents(
            num_vehicles=num_vehicles,
            av_percentage=av_percentage,
            position_type=position_type,
            agent_type=agent_type
        )
        
        self.state = np.zeros(self.num_vehicles * 2)
        
        # Calculate base spacing between vehicles
        self.spacing = self.track_length / self.num_vehicles
        
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
        
        print(self.state)
        print(self.agents)
    
    def set_braking(self, vehicle_index, is_braking):
        """Set the braking state of a vehicle."""
        if is_braking:
            self.braking_vehicles.add(vehicle_index)
        else:
            self.braking_vehicles.discard(vehicle_index)
    
    def reset(self, seed=None, options=None):
        """Reset the environment to initial state."""
        super().reset(seed=seed)
        
        # Initialize positions and speeds of vehicles
        self.state = np.zeros(self.num_vehicles * 2)
        
        if self.position_type == 'interleaved':
            self._reset_interleaved()
        elif self.position_type == 'grouped':
            self._reset_grouped()
        else:  # random
            self._reset_random()
        
        # Clear braking state
        self.braking_vehicles.clear()
        
        return self.state, {}
    
    def _reset_interleaved(self):
        """Reset vehicle positions in an alternating pattern."""
        av_count = 0
        human_count = 0
        for i in range(self.num_vehicles):
            if i in self.av_indices:
                # Position AVs in even positions
                self.state[i*2] = (av_count * 2 * self.spacing) % self.track_length
                av_count += 1
            else:
                # Position human vehicles in odd positions
                self.state[i*2] = ((human_count * 2 + 1) * self.spacing) % self.track_length
                human_count += 1
            self.state[i*2 + 1] = 0  # initial speed
    
    def _reset_grouped(self):
        """Reset vehicle positions in groups (AVs together, then humans)."""
        # Calculate spacing for each group
        av_spacing = (self.track_length / 2) / self.num_av if self.num_av > 0 else 0
        human_spacing = (self.track_length / 2) / self.num_human if self.num_human > 0 else 0
        
        # First, position all AVs in the first half of the track
        av_count = 0
        for i in range(self.num_vehicles):
            if i in self.av_indices:
                # Position AVs in the first half of the track
                self.state[i*2] = (av_count * av_spacing) % (self.track_length / 2)
                av_count += 1
            self.state[i*2 + 1] = 0  # initial speed
        
        # Then, position all human vehicles in the second half of the track
        human_count = 0
        for i in range(self.num_vehicles):
            if i not in self.av_indices:
                # Position humans in the second half of the track
                self.state[i*2] = (self.track_length / 2 + human_count * human_spacing) % self.track_length
                human_count += 1
    
    def _reset_random(self):
        """Reset vehicle positions randomly."""
        positions = np.random.permutation(self.num_vehicles)
        for i in range(self.num_vehicles):
            self.state[i*2] = (positions[i] * self.spacing) % self.track_length
            self.state[i*2 + 1] = 0  # initial speed
    
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
        av_count = 0  # Counter for AV actions
        
        for i in range(self.num_vehicles):
            speed = self.state[i*2 + 1]
            lead_dist, lead_speed = self._get_leading_vehicle(i)
            
            if i in self.braking_vehicles:
                all_actions[i] = self.braking_deceleration
            elif i in self.av_indices:
                all_actions[i] = av_actions[av_count]
                av_count += 1
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