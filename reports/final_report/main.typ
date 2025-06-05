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

#bibliography(
  "refs.bib",
  title: "References",
  style: "ieee",
)
