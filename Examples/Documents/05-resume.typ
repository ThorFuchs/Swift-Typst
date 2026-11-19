#set page(paper: "a4", margin: (x: 21mm, y: 19mm), fill: rgb("#fbfaf7"))
#set text(font: "Libertinus Serif", size: 10.5pt, fill: rgb("#2d3235"))
#set par(leading: 0.65em)
#let blue = rgb("#345f6d")
#let muted = rgb("#718084")
#let label(body) = text(font: "DejaVu Sans Mono", size: 8pt, fill: blue, tracking: 0.04em, body)
#text(size: 35pt, weight: "bold")[Alex Morgan]
#v(2mm)
#text(size: 14pt, fill: blue)[Product designer  /  Systems thinker]
#v(4mm)
#text(size: 9pt, fill: muted)[Portland, OR   ·   alex\@example.com   ·   example.com/alex]
#v(8mm)
#line(length: 100%, stroke: 1pt + blue)
#v(8mm)
#grid(columns: (1.9fr, 1fr), gutter: 11mm,
  [
    #label[PROFILE] #v(3mm)
    Designer drawn to useful, quietly delightful products. I bring research,
    systems thinking, and careful craft to complex problems.
    #v(7mm)
    #label[EXPERIENCE] #v(4mm)
    #text(size: 13pt, weight: "bold")[Senior Product Designer] #linebreak()
    #text(fill: blue)[Northstar Studio] #h(1fr) #text(size: 9pt, fill: muted)[2022 — Present]
    #v(2mm)
    Led end-to-end design for a collaboration platform, from discovery and
    prototyping to a shared design system used by four teams.
    #v(5mm)
    #text(size: 13pt, weight: "bold")[Product Designer] #linebreak()
    #text(fill: blue)[Fieldwork Labs] #h(1fr) #text(size: 9pt, fill: muted)[2019 — 2022]
    #v(2mm)
    Designed research tools and translated complex workflows into clear,
    accessible experiences for a diverse community.
    #v(7mm)
    #label[SELECTED WORK] #v(3mm)
    *Common Ground* — A flexible workspace that helps teams turn ideas into
    meaningful action.
  ],
  [
    #label[EXPERTISE] #v(3mm)
    Product strategy #linebreak() User research #linebreak() Interaction design #linebreak() Design systems #linebreak() Prototyping
    #v(8mm)
    #label[EDUCATION] #v(3mm)
    *BFA, Design* #linebreak() Pacific Arts College #linebreak() #text(size: 9pt, fill: muted)[2015 — 2019]
    #v(8mm)
    #label[APPROACH] #v(3mm)
    Listen closely. #linebreak() Make it simple. #linebreak() Keep learning.
  ],
)
#v(1fr)
#line(length: 100%, stroke: 0.5pt + rgb("#cbd7d6"))
#v(3mm)
#label[EXAMPLE RÉSUMÉ  /  FICTIONAL PROFILE]
