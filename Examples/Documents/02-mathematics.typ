#set page(paper: "a4", margin: (x: 22mm, y: 20mm), fill: rgb("#f7f8fa"))
#set text(font: "STIX Two Text", size: 11pt, fill: rgb("#172641"))
#set par(leading: 0.72em)
#let blue = rgb("#3155a4")
#let muted = rgb("#697991")
#text(font: "DejaVu Sans Mono", size: 8pt, fill: blue, tracking: 0.08em)[MATHEMATICAL NOTES  /  02]
#v(10mm)
#text(size: 34pt, weight: "bold")[A little calculus]
#v(3mm)
#text(size: 14pt, style: "italic", fill: muted)[Three ideas that make change visible.]
#v(9mm)
#line(length: 100%, stroke: 0.8pt + rgb("#cbd6e7"))
#v(7mm)
#text(size: 15pt, weight: "bold")[01  The derivative]

The derivative measures the instantaneous rate at which a function changes.
For a smooth function $f$, it is defined by the limit

#block(width: 100%, fill: rgb("#e7eefb"), inset: 7mm, radius: 3mm)[
  #align(center)[$ f'(x) = lim_(h -> 0) (f(x + h) - f(x)) / h $]
]
#v(5mm)
#text(size: 15pt, weight: "bold")[02  The integral]

Accumulation is the other side of the same story. The fundamental theorem of
calculus connects a function with the area traced by its rate of change:

$ integral_a^b f'(x) dif x = f(b) - f(a) $

#v(4mm)
#text(size: 15pt, weight: "bold")[03  A familiar example]

If $f(x) = x^2$, then $f'(x) = 2x$. Over the interval from $0$ to $3$,

$ integral_0^3 2x dif x = [x^2]_0^3 = 9. $

#v(5mm)
#text(size: 10pt, style: "italic", fill: muted)[A compact page of equations, prose, and mathematical typography.]
#v(1fr)
#line(length: 100%, stroke: 0.5pt + rgb("#cbd6e7"))
#v(3mm)
#grid(columns: (1fr, auto), text(font: "DejaVu Sans Mono", size: 8pt, fill: muted)[SWIFT-TYPST  /  STUDY SERIES], text(font: "DejaVu Sans Mono", size: 8pt, fill: muted)[02])
