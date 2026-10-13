# HyperX Lab website — working rules

Jekyll site published with GitHub Pages: https://hyperx-web.github.io/hyperx/
(repo `hyperx-web/hyperx`, branch `main`; `baseurl: "/hyperx"`).
Always answer the user in Korean.

## Workflow
- Content lives in `_data/*.yml`; pages only render it. Edit data, not templates, for content changes.
- Local preview: no Ruby on this PC. Build with the Python Liquid preview script (scratchpad `preview.py`
  → `_site`, served on http://localhost:8765). Re-create it if missing.
- After every change: rebuild preview, `git commit` (with the Co-Authored-By line), `git push origin main`.
  Push uses the `hyperx-web` account via remote `https://hyperx-web@github.com/hyperx-web/hyperx.git`
  (do not switch the global credential; `dhjung-debug` has no access).
- Pages build takes ~1 min. CSS/JS are cache-busted with `?v={{ site.time }}`.
- Always use `relative_url` for internal links/assets (baseurl!).
- Shell heredocs/sed can drop backslashes: write regexes as JS regex literals and verify LaTeX `\\` after edits.

## Publications (`_data/publications.yml`)
- Groups: `Submitted / In Preparation`, `Published`, `Domestic Journals`, `International Conferences`,
  `Domestic Conferences`, `US Granted Patents`, `US Filed Patents`. Newest first inside each group.
- Venue text: submitted → `submitted to <Journal>, <Mon. YYYY>`; accepted → `accepted to …`; in prep → `in preparation`.
- Author lists: 3+ authors → serial comma before the last `and` (`A, B, and C`); 2 authors → `A and B`.
  Correct spacing (`, ` after commas, no `andD.-H.`), initials like `C.-G. Kang`, `DSSS- and CSS-based`.
  `*` = corresponding author, `†` = equal contribution.
- Title case: sentence case like the existing entries.
- Optional `research: 6g|satellite|ai` pins a paper to a Research area (else keyword matching).
- Lab-member names to mark are listed in `_data/members.yml` → `pub_names` (global list) and per member
  `pub_names` (spelling exactly as in papers). Add new students there.
  `J. Park†` is used for Junhyung Park because another "J. Park" exists.

## Display rules
- Publications page: lab members underlined (same colour as other authors; underline the name only,
  not commas/`*`/`†`); journal/conference name bold in accent blue (detected automatically).
- Home news: journal names wrapped in `<em>` → bold accent blue. News types: paper | award | lab | member.
  Add a "joined HyperX … Welcome aboard! 🎉" news item (type member) when someone joins.
- Members page (student achievements):
  - Submitted + Published are merged under **International Journals**; venue prefix shown as `Submitted to …` / `Accepted to …`.
  - Domestic conference papers are NOT shown.
  - Underline only that student's own name; keep `*` only on the student's own name;
    keep `†` only if the student is an equal-contribution author (then show † on all co-first authors).
  - Venue name bold but no accent colour.
  - Professor row shows profile + link, no publication list.

## Research page (`_data/research.yml`)
- Order: 6G → Satellite & Space → AI. Heading "Related Works" (max 5, auto by keywords; 6G excludes satellite papers).
- Figures: white background, caption outside the figure, figure column 460px, click to enlarge.
- Paper figures are vector SVGs animated with `tools/animate_figure.py <figure.pdf> <out.svg>`
  (signals flow along wires, continuous pulses every 0.9 s, merges arrive together, merged colours blend,
  stacked inputs of the same kind share one colour). New block diagrams: draw in TikZ with the RSMA palette
  (`tools/figures/fig_afdm.tex` is the template), compile with pdflatex, then animate.
- Satellite area: Walker-delta constellation canvas (no ISLs, 15° grid) + Earth–Moon CR3BP Arenstorf orbit
  (`assets/js/threebody.json`, precomputed with scipy). Both on white.

## Style
- Fonts: Inter (English) + KoPub World Dotum (Korean, self-hosted woff2).
- Eyebrow labels: 1.05rem, letter-spacing .06em. No rounded border on the home stats bar.
- Avoid flashy hover effects on images; don't crop photos (members 7:10, research square, gallery natural ratio).
