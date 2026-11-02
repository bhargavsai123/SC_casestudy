#set document(title: "GAAPO: replication audit and adaptive operator selection")
#set page(paper: "a4", margin: (x: 2.2cm, y: 2.4cm), numbering: "1")
#set text(size: 10.5pt)
#set par(justify: true, leading: 0.70em)
#set heading(numbering: none)
#show heading.where(level: 1): it => {
  v(0.9em)
  set text(size: 15pt, weight: "bold")
  it
  v(0.5em)
}
#show table.cell: set par(justify: false)
#show table: it => {
  set par(justify: false)
  set text(size: 9pt)
  it
}
#show outline: it => {
  set text(size: 9.6pt)
  it
}

#align(center)[
  #v(2.2cm)
  #text(size: 21pt, weight: "bold")[GAAPO: a replication audit \
    and an adaptive operator-selection extension]
  #v(1.2em)
  #text(size: 12pt)[Reproducing, correcting and stress-testing \
    a genetic algorithm for automatic prompt optimisation]
  #v(2.2em)
  #text(size: 10.5pt)[Soft Computing — case study]
  #v(0.4em)
  #text(size: 10.5pt)[Target model: qwen2.5:3b · Optimiser model: qwen2.5:7b · Dataset: 433 questions, 50/50/200 split]
  #v(0.4em)
  #text(size: 10.5pt)[27 October 2026]
  #v(3cm)
]

#outline(title: "Contents", depth: 2, indent: 1.2em)

#pagebreak()

#include "case_study.typ"
