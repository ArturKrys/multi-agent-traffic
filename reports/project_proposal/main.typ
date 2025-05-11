#import "@preview/clean-acmart:0.0.1": acmart, acmart-ccs, acmart-keywords, acmart-ref, to-string

#let cuhk = super(sym.suit.spade)

#let title = [
  Multi-Agent System for Phantom Traffic Jam Mitigation
]
#let authors = (
  (
    name: "Artur Krystopchuk",
    email: "email2@email.com",
    mark: super(sym.suit.diamond),
  ),
  (
    name: "Tiago Caixinha",
    email: "email1@email.com",
    mark: super(sym.suit.diamond),
  ),
  (
    name: "Tiago Vieira da Silva",
    email: "tiagovsilva@tecnico.ulisboa.pt",
    mark: super(sym.suit.diamond),
  ),
)
#let affiliations = (
  (
    name: "Instituto Superior Técnico",
    mark: cuhk,
    department: "Departmento de Engenharia Informática",
    course: "Agentes Autónomos e Sistemas Multi-Agentes"
  ),
)

#show: acmart.with(
  title: title,
  authors: authors,
  affiliations: affiliations,
  conference: "AASMA",
  review: none,
  copyright: none
)

= Abstract

= Introduction

== Motivation

== Related Work

== Problem Definition and Relevance

== Objectives

= Approach

== Environment Specification
The simulation environment will consist of a circular single-lane highway where vehicles cannot change lanes or overtake, similar to the experimental setup in  @sugiyama2008.

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

= Conclusion

#bibliography(
  "refs.bib",
  title: "References",
  style: "ieee",
)