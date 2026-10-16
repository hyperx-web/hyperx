# HyperX Lab website — working rules

Jekyll site published with GitHub Pages: https://hyperx-web.github.io/hyperx/
(repo `hyperx-web/hyperx`, branch `main`; `baseurl: "/hyperx"`).
Always answer the user in Korean.

## Workflow
- Content lives in `_data/*.yml`; pages only render it. Edit data, not templates, for content changes.
- Local preview: no Ruby on this PC. `python -I tools/preview.py . <out>/_site` (python-liquid + pyyaml),
  then serve `<out>/_site` with `python -m http.server 8765`.
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
  Add a "<strong>Name</strong> joined HyperX … Welcome aboard! 🎉" news item (type member, name in bold) when someone joins.
- Members page (student achievements):
  - Submitted + Published are merged under **International Journals**; venue prefix shown as `Submitted to …` / `Accepted to …`.
  - Domestic conference papers are NOT shown.
  - Underline only that student's own name; keep `*` only on the student's own name;
    keep `†` only if the student is an equal-contribution author (then show † on all co-first authors).
  - Venue name bold but no accent colour.
  - Professor row shows profile + link, no publication list.

## Research page (`_data/research.yml`)
- Order: 6G → Satellite & Space → AI. Heading "Related Works" (max 5, auto by keywords; 6G excludes satellite papers).
- Figures: white background, caption outside the figure (bold, centred), figure column 460px, click to enlarge.
- Paper figures are vector SVGs animated with `tools/animate_figure.py <figure.pdf> <out.svg>`
  (signals flow along wires, continuous pulses every 0.9 s, merges arrive together, merged colours blend,
  stacked inputs of the same kind share one colour; dashed strokes = group boxes/control arrows, not signals). New block diagrams: draw in TikZ with the RSMA palette
  (`tools/figures/fig_afdm.tex`, `fig_rsma.tex` are the sources; both show multi-antenna Tx/Rx, panels
  labelled Transmitter / Receiver), compile with pdflatex, then animate. Edit .tex with the Edit tool (shell drops `\`).
- Satellite area: Walker-delta constellation canvas (no ISLs, 15° grid; Earth-fixed UE near the equator, starts at the left limb and
  rotates with the Earth; animation restarts when the UE goes behind the Earth; no rim on the globe): nearest visible satellite red + red link, 2nd–5th nearest grey dashed links) + Earth–Moon CR3BP Arenstorf orbit
  (`assets/js/threebody.json`, precomputed with scipy). Both on white.

## Style
- Fonts: Inter (English) + KoPub World Dotum (Korean, self-hosted woff2).
- Eyebrow labels: 1.05rem, letter-spacing .06em. Members achievement headings and block titles (Education, Experience, …): letter-spacing 0. No rounded border on the home stats bar.
- Gallery photos live in one folder per event `assets/img/gallery/<YYYY-MM-event>/01.jpg, 02.jpg…`;
  `_data/gallery.yml` image = `YYYY-MM-event/01.jpg`.
- Avoid flashy hover effects on images; don't crop photos (members 7:10, research square, gallery natural ratio).

## School domain (pending)
- Requested domain: `hyperx.ssu.ac.kr` (forms in `../domain/`), DNS: CNAME → `hyperx-web.github.io`.
- When it is issued: add `CNAME` file (`hyperx.ssu.ac.kr`), set `baseurl: ""` and `url: "https://hyperx.ssu.ac.kr"`,
  set the custom domain in repo Settings → Pages, and turn ON **Enforce HTTPS** once the certificate is issued (user decided).
