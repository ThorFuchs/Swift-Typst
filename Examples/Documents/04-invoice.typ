#set page(paper: "a4", margin: (x: 22mm, y: 20mm), fill: white)
#set text(font: "STIX Two Text", size: 10.5pt, fill: rgb("#202b36"))
#set par(leading: 0.6em)
#let navy = rgb("#173858")
#let pale = rgb("#eef4f8")
#let label(body) = text(font: "DejaVu Sans Mono", size: 8pt, fill: navy, body)
#grid(columns: (1fr, auto),
  [#text(size: 19pt, weight: "bold", fill: navy)[north / studio] #linebreak() #text(size: 9pt)[Thoughtful design for good ideas.]],
  align(right)[#text(size: 29pt, weight: "bold", fill: navy)[Invoice] #linebreak() #label[NS-2026-014]],
)
#v(14mm)
#line(length: 100%, stroke: 1.2pt + navy)
#v(8mm)
#grid(columns: (1fr, 1fr, 1fr), gutter: 5mm,
  [#label[BILL TO] #v(3mm) *Juniper & Co.* #linebreak() 42 Garden Lane #linebreak() Portland, OR 97205],
  [#label[FROM] #v(3mm) *North Studio* #linebreak() 18 Orchard Street #linebreak() Portland, OR 97205],
  [#label[DETAILS] #v(3mm) Issued: 12 May 2026 #linebreak() Due: 11 June 2026 #linebreak() Currency: USD],
)
#v(14mm)
#table(
  columns: (3fr, 1fr, 1fr, 1fr), align: (left, right, right, right), inset: (x: 3mm, y: 4mm),
  stroke: (bottom: 0.5pt + rgb("#d9e3e9")), fill: (x, y) => if y == 0 { pale } else { none },
  table.header( [*Description*], [*Qty*], [*Rate*], [*Amount*]),
  [Brand strategy workshop], [1], [\$1,200], [\$1,200],
  [Visual identity design], [1], [\$2,400], [\$2,400],
  [Implementation guide], [1], [\$600], [\$600],
)
#v(8mm)
#align(right)[
  #grid(columns: (38mm, 32mm), align: (left, right), row-gutter: 3mm,
    [Subtotal], [\$4,200], [Tax (0%)], [\$0],
    [#text(size: 14pt, weight: "bold", fill: navy)[Total due]], [#text(size: 14pt, weight: "bold", fill: navy)[\$4,200]],
  )
]
#v(12mm)
#block(width: 100%, fill: pale, radius: 2mm, inset: 6mm)[
  #label[PAYMENT DETAILS] #v(3mm)
  Please include the invoice number with your payment. Thank you for making
  thoughtful work possible.
]
#v(1fr)
#line(length: 100%, stroke: 0.5pt + rgb("#d9e3e9"))
#v(3mm)
#label[EXAMPLE INVOICE  /  ALL DETAILS ARE FICTIONAL]
