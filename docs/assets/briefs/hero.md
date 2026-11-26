# Brief: README hero and social preview

Date: 2026-11-26. Output: `docs/assets/hero-art.png` (AI illustration, no text), composed with real type into `docs/assets/hero.png` (README banner) and `docs/assets/social-preview.png` (1280x640, upload in GitHub Settings, Social preview). The exact prompt, model and time are in `docs/assets/hero-art.png.json`. References are inspiration only; none was used as an image input or copied.

## What a newcomer must see
Many online stores go in; a short list of niches comes out. It is research, not a product list.

## References
| Reference | What works | Taken / avoided |
|---|---|---|
| [Mermaid README](https://github.com/mermaid-js/mermaid) (opened) | One-line tagline, diagram placed below the description, not as the banner | Mermaid flow below the intro; art stays a plain metaphor |
| Funnel READMEs | None found in this search | A gap, so the funnel is original here |
| [Flujo pipeline cookbook](https://aandresalvarez.github.io/flujo/cookbook/visualizing_pipelines) (search snippet only) | Parallel branches converge on a join node | Stage-to-shortlist layout idea for the flow |

Research note: the QA step caught that the first render of the funnel read right to left. I mirrored the image and moved the title to the right so it reads many, then few.

## Design
- **Subject:** a wide field of hundreds of tiny dim points narrowing through two thin translucent filter rings into three bright points (teal, green, amber).
- **Palette and style (shared across the owner's repos):** deep navy ink (#0B1020), teal/green highlight, amber for the exception, soft glow, faint perspective grid, minimal and not photoreal. Subject in the right two-thirds, calm empty left third for the title.
- **Must not contain:** text, letters, numbers, logos, watermarks, borders, people, robots, brains.
- **QA:** schema check by vision model against this brief, plus a manual look. Result noted in the commit.
