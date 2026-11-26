# Brief: README hero and social preview

Date: 2026-11-26. Output: `docs/assets/hero-art.png` (AI illustration, no text), composed with real type into `docs/assets/hero.jpg` (README banner) and `docs/assets/social-preview.jpg` (1280x640, upload in GitHub Settings, Social preview). The exact prompt, model and time are in `docs/assets/hero-art.png.json`. References are inspiration only; none was used as an image input or copied.

## What a newcomer must see
Many online stores go in; a short list of niches comes out. It is research, not a product list.

## References
| Reference | What works | Taken / avoided |
|---|---|---|
| [Mermaid README](https://github.com/mermaid-js/mermaid) (opened) | One-line tagline, diagram placed below the description, not as the banner | Mermaid flow below the intro; art stays a plain metaphor |
| Funnel READMEs | None found in this search | A gap, so the funnel is original here |
| [Flujo pipeline cookbook](https://aandresalvarez.github.io/flujo/cookbook/visualizing_pipelines) (search snippet only) | Parallel branches converge on a join node | Stage-to-shortlist layout idea for the flow |

Research note: the QA step caught that the first render of the funnel read right to left. I mirrored the image and moved the title to the right so it reads many, then few.

## Design (revised 2026-11-26)

- **Style:** Engraved woodcut on parchment, almanac style.
- **Why this picture:** The repo narrows a huge field of stores to a few niches, and a prospector panning for gold is the oldest picture of that.
- **Subject:** a river crowded with hundreds of tiny floating shop stalls and a large gold-panning pan in the foreground, tipped, with three glowing nuggets left. Sepia cross-hatching with gold and muted teal as the only colours.
- **Layout:** the left third stays quiet for the title; colours and font of the title are set per image in `compose_banner.py`.
- **Must not contain:** text, letters, numbers, logos, watermarks, borders, real people, robots.
- **QA:** schema check by a vision model against this brief, plus a manual look.

## Revision note

The first version of this banner used the same dark navy, teal and grid look as the owner's other repos. It was consistent but samey, so it was replaced with a distinct art direction per repo, each built on a metaphor for what the repo does.
