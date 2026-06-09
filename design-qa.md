# Design QA

Reference: `/Users/ivanproskurakov/Downloads/ChatGPT Image 9 июн. 2026 г., 00_53_21.png`

Prototype: `messenger.html`

Viewport: `1536x1024`

## Checks

- Main `file://` screen keeps the existing Macaroni style: monospace typography, black borders, white background, dense chat layout.
- Feature detection does not change the main chat layout when the browser is supported.
- Unsupported browser screen uses the same visual language: centered bordered panel, monospace text, no decorative assets, no localhost fallback.
- First-run setup screen uses the same visual language: centered bordered panel, mono labels, plain controls, no extra decoration.
- Settings screen uses the same visual language and keeps reset/save/back controls clear.
- Required unsupported text is present: "Your browser is not funny enough to run Macaroni Messenger."
- No external CSS, JS, images, or assets are required.

## Issues

- P0: none.
- P1: none.
- P2: none.

Final result: passed.
