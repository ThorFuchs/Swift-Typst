#set page(paper: "a4", margin: (x: 21mm, y: 19mm), fill: white)
#set text(font: "Libertinus Serif", size: 10.5pt, fill: rgb("#24332f"))
#set par(leading: 0.68em)
#let green = rgb("#356b5b")
#let soft = rgb("#edf4ef")
#let mono(body) = text(font: "DejaVu Sans Mono", size: 8pt, fill: green, body)
#grid(columns: (1fr, auto), [#mono[STUDIO NORTH  /  RESEARCH]], [#mono[2026  •  NO. 03]])
#v(11mm)
#text(size: 33pt, weight: "bold")[A better working day]
#v(3mm)
#text(size: 14pt, style: "italic", fill: rgb("#6b7e75"))[A small study of focus, energy, and thoughtful routines.]
#v(8mm)
#grid(columns: (1fr, 1fr, 1fr), gutter: 4mm,
  block(width: 100%, fill: soft, radius: 2mm, inset: 4mm)[#mono[PARTICIPANTS] #v(2mm) #text(size: 22pt, weight: "bold")[128] #linebreak() #text(size: 9pt)[across 8 teams]],
  block(width: 100%, fill: soft, radius: 2mm, inset: 4mm)[#mono[FOCUS TIME] #v(2mm) #text(size: 22pt, weight: "bold")[+24%] #linebreak() #text(size: 9pt)[after six weeks]],
  block(width: 100%, fill: soft, radius: 2mm, inset: 4mm)[#mono[WELLBEING] #v(2mm) #text(size: 22pt, weight: "bold")[4.6 / 5] #linebreak() #text(size: 9pt)[average rating]],
)
#v(8mm)
#text(size: 16pt, weight: "bold")[The opportunity]

Good work needs both space and structure. In this fictional study, teams tried
simple changes: fewer interruptions, clear priorities, and protected time to
think. The results suggest that small rituals can make the workday feel calmer
and more intentional.
#v(4mm)
#text(size: 16pt, weight: "bold")[What changed]
#v(3mm)
#table(
  columns: (1.2fr, 1fr, 1fr), inset: 3mm,
  stroke: (bottom: 0.5pt + rgb("#d9e5dc")),
  table.header([*Practice*], [*Before*], [*After*]),
  [Uninterrupted focus], [2.1 h / day], [2.6 h / day],
  [Meeting-free mornings], [1 day / week], [3 days / week],
  [Weekly planning], [Occasional], [Consistent],
)
#v(6mm)
#block(width: 100%, fill: soft, radius: 2mm, inset: 5mm)[
  #text(size: 13pt, style: "italic")[“A little more breathing room changed how we work together.”]
  #v(2mm)
  #mono[PARTICIPANT FEEDBACK]
]
#v(1fr)
#line(length: 100%, stroke: 0.5pt + rgb("#d9e5dc"))
#v(3mm)
#grid(columns: (1fr, auto), [#mono[FICTIONAL DATA  /  EXAMPLE REPORT]], [#mono[03]])
