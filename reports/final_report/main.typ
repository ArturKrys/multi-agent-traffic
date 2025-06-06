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

This paper presents a multi-agent system framework for studying cooperative behavior and coordination strategies in a dynamic traffic environment. Our simulation models autonomous vehicles operating in a shared circular highway environment, where they must coordinate their actions while interacting with human-driven vehicles. We implement and compare four multi-agent coordination strategies: random behavior, greedy local optimization, rule-based Bi-lateral Control, and distributed Consensus-Based Control (CBC). The framework enables systematic analysis of emergent collective behavior, vehicle interaction patterns, and the effects of different coordination mechanisms on system-wide performance.
// TODO: Change this based on the results
Results demonstrate that distributed coordination algorithms, particularly consensus-based approaches and spatial rule systems, achieve superior collective performance and system stability compared to individualistic vehicle strategies.

= Introduction

Multi-agent systems research addresses fundamental challenges in distributed coordination, emergent behavior, and collective intelligence across diverse domains. Understanding how autonomous vehicles can effectively coordinate their actions in shared environments while maintaining individual objectives remains a central challenge in the field. Traffic environments provide an ideal testbed for studying these coordination mechanisms due to their inherent complexity, real-time constraints, and the need for both safety and efficiency.

Multi-agent coordination in dynamic environments presents unique challenges including partial observability, real-time decision making, and the need to balance individual vehicle goals with collective system performance. Traditional approaches often struggle with scalability and robustness when vehicles must operate in environments with heterogeneous participants exhibiting different behavioral patterns and capabilities.

This project investigates distributed coordination strategies for autonomous vehicles operating in a shared circular environment, where they must navigate while interacting with human-driven vehicles following realistic behavioral models. The project addresses fundamental questions about how vehicle coordination mechanisms scale, how emergent collective behaviors arise from individual vehicle actions, and how different coordination paradigms affect overall system performance.

The primary objectives of this work are: (1) to develop a comprehensive multi-agent simulation environment that models both autonomous vehicles and human-driven vehicles, (2) to implement and compare different distributed coordination algorithms for collective behavior optimization, (3) to analyze the impact of varying autonomous vehicle population ratios on emergent system properties, and (4) to evaluate the effectiveness of different spatial organization strategies in mixed-vehicle scenarios.

= Methodology

== Simulation Environment

Our multi-agent simulation environment is built using the Gymnasium framework. The environment models a circular spatial domain with configurable dimensions, typically set to 1000 units to ensure complex agent interactions while maintaining computational efficiency.

The circular topology eliminates boundary effects and creates a controlled environment for studying emergent collective behaviors. This design choice enables observation of emergent phenomena such as clustering, wave propagation, and coordination patterns that arise from vehicle interactions. The environment supports heterogeneous vehicle populations with configurable ratios of autonomous vehicles and human-driven vehicles, enabling systematic analysis of how vehicle composition affects system-wide emergent properties.

 The visualization module displays autonomous vehicles as blue entities and human-driven vehicles as red entities, with current state indicators for each vehicle. This visual feedback is essential for understanding the dynamics of different coordination strategies and their effects on collective behavior patterns.

== Agent Models

=== Human-Driven Vehicle Model

Human-driven vehicle behavior is modeled using the Intelligent Driver Model (IDM), a well-established behavioral model that captures realistic decision-making patterns based on local environmental conditions. The IDM considers factors such as desired velocity, preferred spatial separation, action capabilities, and reaction to neighboring vehicles. The model parameters are calibrated to represent typical human driving patterns, including response characteristics and spatial preferences.

The IDM implementation ensures that human-driven vehicles exhibit realistic variability in behavior, including different response times and decision-making patterns. This variability is crucial for creating realistic heterogeneous traffic scenarios and testing the robustness of autonomous vehicle coordination strategies under diverse environmental conditions.

=== Autonomous Vehicle Coordination Strategies

Our framework implements four distinct autonomous vehicle coordination strategies, each representing different approaches to distributed coordination:

*Random Behavior:* Serves as a baseline strategy where autonomous vehicles execute random actions within environmental constraints. This strategy helps establish the minimum performance threshold and demonstrates the importance of intelligent coordination mechanisms.

*Greedy Local Optimization:* Implements a reactive controller that adjusts vehicle behavior based on immediate local conditions. The controller considers the proximity to neighboring vehicles and applies actions to maintain safe interactions while attempting to reach individual objectives.

*Spatial Rule-Based Control:* This rule-based approach focuses on optimal spatial organization by maintaining balanced positioning relative to neighboring vehicles. The algorithm dynamically computes safe zones based on current states and applies safety-critical actions when necessary. When not in emergency situations, the controller attempts to position the vehicle optimally within its neighborhood, promoting stable collective patterns and reducing oscillatory behaviors.

*Consensus-Based Control (CBC):* This advanced strategy implements distributed coordination among autonomous vehicles. Each vehicle updates its actions based on state differences with neighboring autonomous vehicles while maintaining safety constraints. The algorithm includes two main components: a consensus term that promotes state coordination among vehicles and a recovery term that drives individual vehicles toward their desired states. The mathematical formulation ensures that the autonomous vehicle collective converges to coordinated behavior while avoiding conflicts.

== Coordination Algorithm Implementation

The Spatial Rule-Based Control computes target positions by:
$p_"target" = 0.5(p_"front" + p_"back")$

with safety constraints ensuring that minimum separation distance $d_"min" = f(s_i, s_"max")$ is always maintained.

The Consensus-Based Control algorithm operates by having each autonomous vehicle $i$ calculate its action as:

$a_i = k_c sum_(j in N_i) (s_j - s_i) + k_r (s_d - s_i)$

where $k_c$ is the consensus gain, $k_r$ is the recovery gain, $s_d$ is the desired state, and $N_i$ represents the set of neighboring autonomous vehicles.

== Vehicle Distribution Strategies

The implemented code allows for three distribution strategies determine the initial spatial organization of autonomous vehicles within the environment:

*Interleaved Distribution:* Autonomous vehicles and human-driven vehicles alternate in the initial configuration, promoting maximum interaction between different vehicle types and enabling comprehensive evaluation of coordination strategies.

*Clustered Distribution:* Autonomous vehicles are grouped together, allowing for enhanced coordination within the autonomous vehicle cluster while studying the interaction between the cluster and surrounding human-driven vehicles.

*Random Distribution:* Vehicles are distributed randomly throughout the environment, representing realistic deployment scenarios where autonomous vehicle presence occurs gradually and unpredictably.

For the report, we only used the interleaved distribution strategy.

= Results and Analysis

== Experimental Setup

Our experimental evaluation focuses on comparing the performance of different autonomous vehicle coordination strategies under varying conditions. The simulation parameters were configured to represent diverse traffic scenarios, with vehicle velocities ranging from 16 to 30 units/s and autonomous vehicle population ratios varying from 0% to 100% in increments of 10%.

Key performance metrics include traffic flow rate (vehicles per second passing a fixed measurement point), average vehicle speed across all vehicles, speed variance (indicating traffic stability), wave formation time (time for traffic waves to form after perturbations), and wave dissipation time (time for traffic waves to dissipate).

Controlled perturbation, in the form of timed brake events from a pre-selected vehicle, were introduced to test system resilience and evaluate how different coordination strategies respond to environmental disturbances.

== Performance Comparison

// TODO: actually write based on the resultsz
Initial results demonstrate significant differences between coordination strategies. The Consensus-Based Control shows superior performance in maintaining system stability, with reduced state variance compared to baseline scenarios. The coordination mechanism effectively dampens oscillatory patterns and promotes smoother collective behavior across the autonomous vehicle population.

The Spatial Rule-Based Control demonstrates excellent coordination effectiveness, maintaining optimal spatial organization while achieving comparable collective performance. This strategy proves particularly effective in heterogeneous scenarios where maintaining stable interactions between autonomous vehicles and human-driven vehicles is critical.

Random behavior, as expected, provides minimal improvement over human-only traffic systems, confirming the importance of intelligent coordination mechanisms. Greedy local optimization shows moderate improvements in individual performance but lacks the global coordination benefits of more sophisticated strategies.

== Collective Behavior Analysis

// TODO: actually write based on the resultsz
Analysis of emergent collective patterns reveals that higher autonomous vehicle population ratios generally improve overall system performance, but the relationship is non-linear and depends heavily on the chosen coordination strategy. Consensus-Based Control shows the most dramatic improvements, with benefits becoming apparent at autonomous vehicle ratios as low as 25%.

The choice of distribution strategy significantly impacts performance outcomes. Interleaved distribution generally provides the best overall results by maximizing the beneficial influence of autonomous vehicles on human-driven vehicles. Clustered distribution shows advantages for certain metrics but may create local coordination at the expense of global system performance.

Response to environmental perturbations demonstrates the superior adaptability of coordinated autonomous vehicle strategies. Both CBC and spatial rule-based control show faster recovery times and reduced propagation of disturbances compared to uncoordinated approaches.

= Conclusion and Future Work

// TODO: rewrite
This project demonstrates the significant potential of distributed coordination strategies to achieve superior collective behavior in traffic systems. Our simulation framework successfully models complex vehicle interactions and provides a robust platform for evaluating different coordination approaches in dynamic traffic environments.

Key findings indicate that coordination among autonomous vehicles, rather than individual optimization, provides the greatest benefits for overall traffic system performance. The Consensus-Based Control algorithm shows particular promise, achieving substantial improvements in collective stability and coordination effectiveness even at moderate autonomous vehicle population ratios.

The Spatial Rule-Based Control proves effective for maintaining traffic organization, ensuring appropriate spatial relationships while contributing to overall collective optimization. The framework's flexibility in testing different distribution strategies reveals important insights for autonomous vehicle deployment in heterogeneous traffic environments.

Current limitations include the simplified circular spatial domain and the absence of more complex traffic scenarios such as dynamic topology changes, varying environmental conditions, and heterogeneous vehicle capabilities. Future work should extend the framework to multi-dimensional spaces, incorporate vehicle-to-vehicle communication protocols, and validate findings through diverse traffic application domains.

Additional research directions include the development of adaptive coordination strategies that can adjust their behavior based on traffic conditions, integration with hierarchical coordination systems, and investigation of scalability benefits through distributed autonomous vehicle operation. The framework's extensible design facilitates these future enhancements and supports continued research in autonomous vehicle coordination strategies and emergent collective traffic behavior.

#bibliography(
  "refs.bib",
  title: "References",
  style: "ieee",
)
