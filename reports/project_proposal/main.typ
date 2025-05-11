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
    email: "email1@email.com",
    mark: super(sym.suit.diamond),
    istid: "istXXXXXX",
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

This project proposal outlines a multi-agent simulation framework to study the impact of autonomous vehicles (AVs) on traffic flow dynamics in a circular single-lane highway. By integrating human-driven vehicle models based on the Intelligent Driver Model (IDM) with various AV decision-making strategies, we aim to analyze how different AV behaviors and penetration rates influence system-level traffic dynamics. The empirical evaluation will focus on metrics such as traffic flow rate, average speed, speed variance, and wave dissipation times to quantify the thresholds at which AVs significantly mitigate phantom jams and enhance throughput. The insights gained from this work will inform optimal traffic management strategies in mixed-traffic environments.

= Introduction

== Motivation
Traffic congestion is a persistent problem in urban environments, costing billions in lost productivity and fuel wastage while increasing pollution.
The viral video "The Simple Solution to Traffic" [1] demonstrates how human driving behaviors, specifically unnecessary braking and acceleration patterns, create "phantom traffic jams" that propagate backward through a line of vehicles.

Phantom traffic jams—stop-and-go waves that arise on busy roads without obstacles—are caused by drivers' delayed reactions and uneven braking/acceleration. These jams waste time and fuel, increase pollution, and raise crash risks. While adding lanes might help, autonomous vehicles (AVs), as shown in the video @cgpgrey2017traffic, have greater potential to improve safety and efficiency. By using precise control and coordinated driving algorithms, AVs can smooth traffic flow and reduce these unnecessary costs.

== Related Work
Traffic flow dynamics have been extensively studied in transportation engineering. In the same light, although not as extensively studied, there are still a considerable number of studies related to how AVs could help traffic flow. Some of these studies, like "Traffic Flow Dynamics: Data, Models and Simulation" @Treiber2013, "Opportunities for multiagent systems and multiagent reinforcement learning in traffic control" @Bazzan2009 and "How Autonomous and Human-Driven Vehicles interact in a Roundabout" @laura2023 provide valuable insights into the potential of AVs to improve traffic efficiency and stability.

However, most of these studies focus on specific scenarios or vehicle types, leaving a gap in understanding how AVs can be integrated into existing traffic systems. The work "The impact of connected and autonomous vehicles on traffic flow stability" @sugiyama2008 provides a comprehensive overview of the potential benefits of AVs in traffic flow dynamics, but it does not explore the effects of varying penetration rates or cooperative behaviors.

== Problem definition and relevance
With this project we pretend to addresses the following problem: How do varying percentages of autonomous vehicles with different cooperative behaviors impact traffic flow stability and throughput in a circular single-lane highway?

We are looking to understand:
- The minimum penetration rate of AVs needed to significantly improve traffic flow
- From different algorithms identify optimal driving strategies for AVs to dampen traffic waves
- Quantifying emergent system-level benefits from local autonomous vehicle decision-making

== Objectives
This project aims to:
- Develop a multi-agent simulation of a circular single-lane highway with mixed vehicle populations
- Implement and compare four decision-making algorithms for autonomous vehicles where two of them we will use as baseline (greedy and random)
- Analyze the impact of varying penetration rates of autonomous vehicles on traffic stability
- Investigate whether local cooperative behaviors can produce global traffic flow optimization

= Approach

== Environment Specification
The simulation environment will consist of a circular single-lane highway where vehicles cannot change lanes or overtake, similar to the experimental setup in @sugiyama2008.

The environment will be discretized into cells, with vehicles occupying each one cell. Time will progress in discrete steps. The state of the environment at any time step includes the positions, velocities, and accelerations of all vehicles.

The simulation will be run for a fixed duration, with vehicles initialized in a random distribution to create a variety of traffic conditions. The initial state will include a mix of human-driven and autonomous vehicles, with the proportion of each type varying across experiments.

The simulation will also include a mechanism for introducing perturbations (e.g., random braking events) to trigger phantom jams. These perturbations will be introduced at random intervals and locations to simulate real-world conditions.

== Multi-Agent System Design

The system will consist of two types of agents:

1. *Human-driven vehicle agents*:
These agents will follow realistic human driving behaviors including delayed reaction times, unnecessary braking, and suboptimal following distances. Their Implementation will follow a car-following model based on the Intelligent Driver Model (IDM) @treiber2000, which captures realistic human driving behavior including:
- Finite reaction times
- Imperfect perception
- Tendency to maintain safe distances that grow with speed
- Some degree of randomness in behavior

2. *Autonomous/connected vehicle agents*:

These agents will implement optimal driving strategies with perfect sensing of nearby vehicles and minimal reaction times. Multiple decision-making approaches will be implemented for these agents such as:
- Rule-based: Simple rules for maintaining safe distances and speeds such as bilateral control (maintaining equal distance to front and rear vehicles) and wave-dampening (actively counteracting detected traffic waves)
- Collaborative sensing: Sharing information about traffic conditions ahead
- Reinforcement Learning: Learning optimal policies through trial and error in simulated environments

This approaches might change the further we go into the project and course.

== System Architecture

The system will be implemented with the following components:

1. *Environment Module*: Manages the physical aspects of the circular highway, enforces physical constraints, and updates vehicle positions based on their actions.
2. *Agent Module*: Implements the decision-making algorithms for both HDVs and AVs, with distinct submodules for different AV strategies.
3. *Observation Module*: Collects and processes data about the simulation state for analysis.

The system will be implemented in Python, utilizing libraries such as NumPy for numerical computations and Matplotlib for visualization. For the multi-agent framework, either Mesa or a custom implementation will be used depending on computational efficiency requirements.

== Design Choices Rationale

The circular single-lane design is chosen to isolate the phantom traffic jam phenomenon from other complexities like intersections and lane changes. This allows for a clearer analysis of the effects of different vehicle types and coordination strategies. This environment has been validated in real-world experiments @sugiyama2008 and provides a controlled setting to analyze the impact of AVs on traffic dynamics.

The IDM model is selected for human-driven vehicles due to its balance between realism and computational efficiency. It captures essential human driving behaviors while being simple enough to implement in a multi-agent framework.

The multi-agent approach is particularly suitable for this problem because:

1. Traffic is inherently a distributed system with no central controller
2. Vehicle behaviors and interactions are complex and heterogeneous
3. Coordination strategies can be implemented and tested incrementally
4. The approach scales well to realistic traffic scenarios

= Empirical Evaluation

== Metrics
The following metrics will be used to evaluate the system's performance:

  - *Traffic Flow Rate*: The number of vehicles passing a fixed point per unit time
  - *Average Vehicle Speed*: The mean speed across all vehicles
  - *Speed Variance*: The variance in speeds across vehicles (indicating stability)
  - *Wave Formation Time*: How quickly traffic waves form after an initial perturbation
  - *Wave Dissipation Time*: How quickly traffic waves dissipate after formation

= Conclusion
In this project, we present multi-agent framework to study the impact of autonomous vehicles in a circular single-lane highway. By combining human-driven vehicle models based on the Intelligent Driver Model (IDM) with various autonomous driving strategies, we aim to dissect how different AV behaviors and penetration rates influence system-level traffic dynamics. Our empirical evaluation, guided by metrics such as traffic flow rate, average speed, speed variance, and wave dissipation times, will quantify the thresholds at which AVs significantly mitigate phantom jams and enhance throughput. The insights gained from this work will inform what is the best traffic management strategies in mixed-traffic environments. Ultimately, our findings will most likely show how AVs contribute to safer and more effiecient road networks.

#bibliography(
  "refs.bib",
  title: "References",
  style: "ieee",
)
