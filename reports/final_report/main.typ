#import "@preview/clean-acmart:0.0.1": acmart, acmart-ccs, acmart-keywords, acmart-ref, to-string

#let cuhk = super(sym.suit.spade)

#let title = [
  Autonomous Vehicles in Circular Highway Traffic System: A Multi-Agent Approach to Traffic Flow Optimization
]
#let authors = (
  (
    name: "Artur Krystopchuk",
    email: "arturkrystopchuk@tecnico.ulisboa.pt",
    mark: super(sym.suit.diamond),
    istid: "ist1104145",
  ),
  (
    name: "Tiago Caixinha",
    email: "tiago.caixinha@tecnico.ulisboa.pt",
    mark: super(sym.suit.diamond),
    istid: "ist1102437",
  ),
  (
    name: "Tiago Vieira da Silva",
    email: "tiagovsilva@tecnico.ulisboa.pt",
    mark: super(sym.suit.diamond),
    istid: "ist199335",
  ),
)
#let affiliations = (
  (
    name: "Instituto Superior Técnico",
    mark: cuhk,
    department: "Departmento de Engenharia Informática",
    course: "Agentes Autónomos e Sistemas Multi-Agentes",
    year: "2024/2025",
  ),
)

#show: acmart.with(
  title: title,
  authors: authors,
  affiliations: affiliations,
  conference: "AASMA",
  review: none,
  copyright: none,
)

= Abstract

This paper presents a multi-agent system framework for studying coordination strategies to mitigate phantom traffic jams in dynamic highway environments. Phantom jams—spontaneous traffic congestion that emerges without apparent causes—represent a significant challenge in transportation systems that autonomous vehicles could help address. Our simulation models autonomous vehicles operating in a shared circular highway environment, where they must coordinate their actions while interacting with human-driven vehicles to prevent and dissipate phantom jams. We implement and compare four multi-agent coordination strategies: random behavior, greedy local optimization, rule-based Spatial Control, and distributed Consensus-Based Control (CBC). The framework enables systematic analysis of phantom jam formation, dissipation patterns, and the effectiveness of different coordination mechanisms in maintaining traffic flow stability.

Results demonstrate that distributed coordination algorithms, particularly consensus-based approaches and spatial rule systems, achieve superior performance in phantom jam mitigation compared to random behavior. Up to 50% AV penetration rate, all coordinated strategies maintain higher average speeds and traffic flow rates while reducing phantom jam formation time. Beyond this threshold, Consensus-Based Control prioritizes stability and faster wave dissipation, while Greedy and Spatial Control strategies maintain higher throughput at the cost of increased speed variance. These findings highlight the importance of selecting coordination algorithms based on specific phantom jam mitigation objectives and user comfort preferences.

= Introduction

Phantom traffic jams—spontaneous congestion that emerges without visible causes such as accidents, construction, or bottlenecks—represent one of the most frustrating and economically costly phenomena in modern transportation systems. As demonstrated in CGP Grey's influential video "The Simple Solution to Traffic" @cgpgrey2017traffic, these mysterious traffic waves form when small disturbances in vehicle flow cascade through traffic, creating stop-and-go patterns that can persist for hours and affect thousands of vehicles. The video illustrates how even minor driver reactions can propagate backward through traffic, forming jams that seem to appear from nowhere, and proposes autonomous vehicles as a potential solution to this pervasive problem.

This project aims to expand on the scope of the video, investigating how introducing autonomous vehicles with different coordination strategies affects phantom jam dynamics in a shared circular environment, where they must navigate while interacting with human-driven vehicles following realistic behavioral models. The project addresses fundamental questions about how vehicle coordination mechanisms scale, how emergent collective behaviors arise from individual vehicle actions, and how different coordination paradigms affect overall system performance in the context of phantom jam mitigation.

= Methodology

== Simulation Environment

Our multi-agent simulation environment is built using the Gymnasium framework. The environment models a circular one-lane highway with configurable dimensions, with the default at 1000 units to ensure complex agent interactions while maintaining computational efficiency. This circular highway design is inspired by the experimental setup used by Sugiyama et al. @sugiyama2008, who demonstrated the spontaneous formation of phantom jams in controlled circular track experiments.

The circular topology eliminates boundary effects and creates a controlled environment for studying emergent collective behaviors. This design choice enables observation of emergent phenomena such as clustering, wave propagation, and coordination patterns that arise from vehicle interactions. The environment supports heterogeneous vehicle populations with configurable ratios of autonomous vehicles and human-driven vehicles, enabling systematic analysis of how vehicle composition affects system-wide emergent properties.

 The visualization module displays autonomous vehicles as blue entities and human-driven vehicles as red entities, with current state indicators for each vehicle. This visual feedback is essential for understanding the dynamics of different coordination strategies and their effects on collective behavior patterns.

== Agent Models

=== Human-Driven Vehicle Model

Human-driven vehicle behavior is modeled using the Intelligent Driver Model (IDM) @treiber2000, a well-established behavioral model that captures realistic decision-making patterns based on local environmental conditions. The IDM considers factors such as desired velocity, preferred spatial separation, action capabilities, and reaction to neighboring vehicles. The model parameters are calibrated to represent typical human driving patterns, including response characteristics and spatial preferences.

The IDM implementation ensures that human-driven vehicles exhibit realistic variability in behavior, including different response times and decision-making patterns. This variability is crucial for creating realistic heterogeneous traffic scenarios and testing the robustness of autonomous vehicle coordination strategies under diverse environmental conditions.

=== Autonomous Vehicle Coordination Strategies

Our framework implements four distinct autonomous vehicle coordination strategies, each representing different approaches to distributed coordination:

*Random Behavior:* Serves as a baseline strategy where autonomous vehicles execute random actions within environmental constraints. This strategy helps establish the minimum performance threshold and demonstrates the importance of intelligent coordination mechanisms.

*Greedy Local Optimization:* Implements a reactive controller that adjusts vehicle behavior based on immediate local conditions. The controller considers the proximity to neighboring vehicles and applies actions to maintain safe interactions while attempting to reach individual objectives.

*Spatial Rule-Based Control:* This strategy implements the "stay in the middle" approach highlighted in CGP Grey's video @cgpgrey2017traffic as a simple yet effective solution to phantom jams. The algorithm focuses on maintaining balanced positioning relative to neighboring vehicles by positioning each autonomous vehicle equidistantly between the car in front and the car behind. This rule-based approach dynamically computes safe zones based on current states and applies safety-critical actions when necessary. When not in emergency situations, the controller attempts to position the vehicle optimally within its neighborhood, promoting stable collective patterns and reducing the oscillatory behaviors that lead to phantom jam formation.

*Consensus-Based Control (CBC):* This advanced strategy implements distributed coordination among autonomous vehicles. Each vehicle updates its actions based on state differences with neighboring autonomous vehicles while maintaining safety constraints. The algorithm includes two main components: a consensus term that promotes state coordination among vehicles and a recovery term that drives individual vehicles toward their desired states. The mathematical formulation ensures that the autonomous vehicle collective converges to coordinated behavior while avoiding conflicts.

== Coordination Algorithm Implementation

The Spatial Rule-Based Control computes target positions by:
$p_"target" = 0.5(p_"front" + p_"back")$

where:
- $p_"target"$ is the desired target position for the autonomous vehicle
- $p_"front"$ is the current position of the vehicle directly ahead
- $p_"back"$ is the current position of the vehicle directly behind

The algorithm also enforces safety constraints ensuring that minimum separation distance $d_"min" = f(s_i, s_"max")$ is always maintained, where:
- $d_"min"$ is the minimum safe following distance
- $s_i$ is the current speed of vehicle $i$
- $s_"max"$ is the maximum speed limit

The Spatial Rule-Based Control algorithm uses dynamic braking distance calculations based on the current vehicle speed, rather than fixed minimum distance values. The algorithm computes braking distance as $d_"braking" = v^2 / (2 \cdot |a_"max"|)$ where $v$ is the current speed and $a_"max" = 5.0$ m/s² is the maximum deceleration capability.

The Consensus-Based Control algorithm operates by having each autonomous vehicle $i$ calculate its action as:

$a_i = k_c sum_(j in N_i) (s_j - s_i) + k_r (s_d - s_i)$

where:
- $a_i$ is the control action (acceleration/deceleration) for vehicle $i$
- $k_c$ is the consensus gain, controlling how strongly vehicles coordinate with neighbors
- $k_r$ is the recovery gain, controlling how strongly vehicles move toward their desired state
- $s_i$ is the current state (position and velocity) of vehicle $i$
- $s_j$ is the current state of neighboring autonomous vehicle $j$
- $s_d$ is the desired target state for the vehicle
- $N_i$ represents the set of neighboring autonomous vehicles within communication range of vehicle $i$

We choose the arbitrary values of $k_c = 0.5$ and $k_r = 0.2$ for the Consensus-Based Control algorithm.

== Vehicle Distribution Strategies

The implemented code allows for three distribution strategies determine the initial spatial organization of autonomous vehicles within the environment:

*Interleaved Distribution:* Autonomous vehicles and human-driven vehicles alternate in the initial configuration, promoting maximum interaction between different vehicle types and enabling comprehensive evaluation of coordination strategies.

*Clustered Distribution:* Autonomous vehicles are grouped together, allowing for enhanced coordination within the autonomous vehicle cluster while studying the interaction between the cluster and surrounding human-driven vehicles.

*Random Distribution:* Vehicles are distributed randomly throughout the environment, representing realistic deployment scenarios where autonomous vehicle presence occurs gradually and unpredictably.

= Results and Analysis

== Experimental Setup

Our experimental evaluation focuses on comparing the performance of different autonomous vehicle coordination strategies under varying conditions. The simulation parameters were configured to represent diverse traffic scenarios, with vehicle velocities ranging from 16 to 30 units/s and autonomous vehicle population ratios varying from 10% to 90% in increments of 10%.

Key performance metrics include:
- Traffic flow rate (vehicles per second passing a fixed measurement point)
- Average vehicle speed across all vehicles
- Speed variance (indicating capacity in maintaining a stable speed)
- Wave formation time (time for traffic waves to form after perturbations)
- Wave dissipation time (time for traffic waves to dissipate).

Controlled perturbation, in the form of timed brake events from a pre-selected vehicle, were introduced to test system resilience and evaluate how different coordination strategies respond to environmental disturbances.

We ran multiple simulations with the following parameters:

- 100 vehicles
- 10000m track
- 3600 simulated seconds (360000 steps)
- 10% to 90% AV penetration rate
- Random distribution strategy

== Results and Analysis

When comparing the performance of the different coordination strategies, we can see that the Consensus-Based Control (CBC) and the Spatial Rule-Based Control (SBC) are the best performing strategies.

When analysing the Average Vehicle Speed, we can see that, when comparing with the Random Behavior strategy, the three strategies (Greedy, CBC and SBC) are able to maintain a higher average speed until the AV penetration rate reaches around 50%.

#figure(
  image("./images/average_speed.png", width: 100%),
  caption: [
    Average vehicle speed across different AV penetration rates and control strategies.
  ]
)

After that, we see a drop in the average speed of the CBC strategy.

We can observe the same pattern for the Traffic Flow Rate.

#figure(
  image("./images/flow_rate.png", width: 100%),
  caption: [
    Traffic flow rate across different AV penetration rates and control strategies.
  ]
)

This can be explained by looking at the Speed Variance graph, where we can see that the speed variance after 50% AV penetration rate incresases for the Greedy and SBC strategies, while the CBC strategy maintains a lower speed variance.

#figure(
  image("./images/speed_variance.png", width: 100%),
  caption: [
    Speed variance across different AV penetration rates and control strategies.
  ]
)

This indicates that, while the Greedy and SBC agents brake and accelerate more often to maintain flow and speed, the CBC is more stable and smoother in its behavior, antecipating the actions of the other agents and maintaining a more consistent speed.

When analysing the Wave Formation Time, the three strategies have lower wave formation times than the Random Behavior strategy until the 50% AV penetration rate. After that, the CBC maintains its lower wave formation time, while the Greedy and SBC strategies increase a lot.

#figure(
  image("./images/wave_formation.png", width: 100%),
  caption: [
    Wave formation time across different AV penetration rates and control strategies.
  ]
)

This indicates that the SBC and Greedy strategies form bigger waves, having the AVs reaching the wave faster than the CBC strategy, consequence of the higher average speed of the SBC and Greedy strategies.

When analysing the Wave Dissipation Time, we can see that the CBC strategy has a lower wave dissipation time, than the SBC and than the Greedy strategy. This indicates that the CBC strategy is able to dissipate the wave faster than the other strategies, altough the difference is not that significant.

#figure(
  image("./images/wave_dissipation.png", width: 100%),
  caption: [
    Wave dissipation time across different AV penetration rates and control strategies.
  ]
)

The random behaviour strategy doesn't have a wave dissipation time, because it was unable to dissipate the wave. As such, we couldn't plot it.

== Autonomous Vehicle Population Ratio Analysis

When analysing the metrics evolution with the change in the Autonomous Vehicle Population Ratio, we could see an improvment in the average speed and the traffic flow rate when the AVs have defined a strategy to follow.

After 50% AV penetration rate, we can see a choice between having a more reactive, but more unstable strategy, choosing a Greedy or a SBC strategy, or having a more stable speed and flow strategy, choosing a CBC strategy.

The choice of algorithms should have in mind its application. Perhaps the users don't want to always be accelerating and braking, and would prefer a more stable speed and flow. On the other way, if the users want to sacrifice comfort for a more efficient flow, they could choose the Greedy or SBC strategy.

= Conclusion

This project demonstrates the significant potential of distributed coordination strategies to achieve superior collective behavior in traffic systems. Our simulation framework, while being a simple model, was able to show the potential of the different coordination strategies.

The results show that the Consensus-Based Control (CBC) and the Spatial Rule-Based Control (SBC) are the best performing strategies, achieving superior collective performance and system stability compared to individualistic vehicle strategies.

The Autonomous Vehicle Population Ratio Analysis shows that the choice of algorithms should have in mind its application. Perhaps the users don't want to always be accelerating and braking, and would prefer a more stable speed and flow. On the other way, if the users want to sacrifice comfort for a more efficient flow, they could choose the Greedy or SBC strategy.

The current model is a simple model, with a circular spatial domain and a fixed number of vehicles. It would be interesting to see how the different coordination strategies perform in a more complex spatial domain, with more vehicles and more complex traffic scenarios.

It would also be interesting to see how the different coordination strategies perform in a more complex spatial domain, with more vehicles and more complex traffic scenarios.

#bibliography(
  "refs.bib",
  title: "References",
  style: "ieee",
)
