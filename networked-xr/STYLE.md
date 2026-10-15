# Writing guide for the Networked XR review

This review condenses the Networked XR Atlas (5,408 screened papers, 2016–2026) into a ~30-page
journal-style survey. Every section must read as if one careful author wrote it.

## Voice
- Simple, straight, sophisticated. Short declarative sentences; precise technical terms; no hype.
- Open every paragraph with its claim. The rest of the paragraph supports it with evidence.
- Prefer verbs to nominalisations ("users tolerated 200 ms", not "a tolerance of 200 ms was observed").
- British spelling (optimise, synchronisation, behaviour), serial comma not required.
- Banned words and tics: delve, landscape (except Section 3 title), realm, crucial, pivotal, paramount,
  seamless, cutting-edge, novel (unless contrasting with prior work), plethora, myriad, "it is worth
  noting", "plays a vital role", "in recent years", "paves the way", "game-changer", "holistic",
  rhetorical questions, exclamation marks, em-dash chains. Use "---" sparingly (at most one per paragraph).
- Do not write "papers show" when one paper shows. Attribute a result to the study that produced it,
  and state its conditions (testbed, number of users, link) when they limit it.
- Separate three registers explicitly: what is **established** (replicated or measured on real systems),
  what is **contested** (conflicting results), and what is **assumed** (stated without evidence).
- Numbers carry the argument. Give the number, its unit and its source: "post-render warping removed up
  to 80% of the aiming penalty of 80 ms added latency \cite{W3089399051}".

## LaTeX conventions
- One file per section, beginning `\section{...}\label{sec:...}`. Use `\subsection` for strands
  (3–4 per section). No `\subsubsection`. Use `\paragraph{...}` only when really needed.
- Cite with `\cite{Wxxxxxxx}` (OpenAlex ids). Cite ONLY ids that appear in the atlas material you were
  given (synthesis files, short cell texts, gap files, paper summaries). Never invent an id.
  Several ids: `\cite{W1,W2}`.
- Size macros from `data/numbers.tex` and `data/synthesis_numbers.tex` may be used (e.g.
  `\nxrNProbLatency{}`, `\nxrShProbLatency{}`, `\nxrRealLatency{}`). Do NOT use any macro ending in
  `Refs` (they point at labels of an older document). Do not use `\S\ref{sec:problem-...}` labels.
  Cross-reference other sections of THIS review only with the labels listed below.
- Counts quoted from the synthesis fact sheets refer to an older 5,721-paper multi-label cell
  membership and disagree with the macros. Prefer the macros for cell size and shares; for regex
  sub-counts, prefer a macro from synthesis_numbers.tex if one exists, otherwise express the result as
  a proportion or an order of magnitude ("fewer than one in twenty latency papers report tail latency").
- Typography: `~ms`, `~Mbps`, `$\times$`, `5G`, `6G`, `Wi-Fi~6`, `360-degree video`, `6DoF`, `3DoF`,
  "motion-to-photon (MTP)" at first use in a section, then MTP. En-dash for ranges `5--100~ms`.
  Percent as `\%`. No bold in running text except the lead-in of an open-problem item.
- Open problems: end every core section with exactly one box:
  ```
  \begin{openproblems}
  \item \textbf{Short statement of the gap.} One or two sentences of evidence, then what study or
        system would close it.
  ...
  \end{openproblems}
  ```
  4–6 items, each ≤ 60 words. Choose the gaps with high confidence in the atlas gap files.
- Optional: at most one compact table per section (`table` float, `\small`, `tabularx`, booktabs,
  ≤ 9 rows) of key quantitative results, caption ending in a full stop, label `tab:<section>-...`.
  Only include it if it adds information the prose does not.

## Section labels in this review
sec:intro, sec:method, sec:landscape, sec:framework,
sec:encode (What is sent: representing and encoding immersive content),
sec:anticipate (Delivering ahead of the user: adaptation, prediction, caching),
sec:compute (Where computation happens: offloading, remote rendering, latency),
sec:provision (Provisioning the network: radio, resources, transport, architecture),
sec:connect (Connecting people and things: synchronisation, avatars, haptics, holoportation, twins),
sec:assure (Assuring experience and trust: QoE, security, privacy),
sec:synthesis, sec:agenda, sec:conclusion.

## Revision 2 (applies to every function section)
- Prose budget is now **1,150–1,300 words** (excluding the open-problems box, table and figure). The
  whole review must fit in 30 pages.
- Every function section MUST contain one **architecture or mechanism diagram** in TikZ: a system
  view (components, tiers device/access/edge/cloud, data and control flows, where the section's
  decisions are made), not a data chart. Width \linewidth or 0.9\linewidth, height ≤ 0.33 page,
  `\sffamily\scriptsize`/`\footnotesize` labels, black text, thin strokes (0.5–0.7pt), rounded
  boxes filled with the section colour at 6–12% (e.g. `fill=compute!8,draw=compute!70!black`),
  arrows `-{Stealth[length=1.8mm]}`, a small legend if line styles carry meaning. Use the section
  colour as accent only. No overlapping labels: render the page to PNG
  (`pdftoppm -png -r 110 -f N -l N test_x.pdf out`) and look at it before finishing.
- At most one compact table in addition to the diagram, and only if it carries numbers the prose
  does not.
- Figures use `[t]` placement, caption first sentence = what it shows, second = the point.
