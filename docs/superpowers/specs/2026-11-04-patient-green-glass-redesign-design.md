# Patient Green Glass Redesign

## Intent

Redesign the working patient frontend around the supplied dark glass dashboard reference and the exact green palette `#051F20`, `#0B2B26`, `#163832`, `#235347`, `#8EB69B`, and `#DAF1DE`. The result should feel calm, private, premium, and unmistakably healthcare-focused rather than copying ChatGPT branding or content.

## Goals

- Apply one cohesive visual system to every patient route through the shared shell and global primitives.
- Use a desktop sidebar, compact workspace header, luminous glass panels, and layered green depth.
- Preserve all current authentication, profile, history, documents, guidance, intake, safety, PWA, and accessibility behavior.
- Keep the interface responsive, keyboard-usable, high-contrast, and readable with reduced motion or forced colors.

## Non-goals

- No backend, API, data-model, workflow, or dependency changes.
- No literal ChatGPT clone, purple palette, external imagery, remote fonts, or decorative medical claims.
- No new product features or navigation destinations.

## Approaches considered

1. **Page-by-page restyle:** maximum per-page control, but duplicates styling and risks inconsistent behavior.
2. **Shared shell and design-token redesign (chosen):** remodel the global shell, navigation, and primitives, then let every route inherit the system. This is the smallest coherent change and preserves existing feature code.
3. **New component-library migration:** strongest long-term isolation, but unnecessary for a visual redesign and adds migration risk.

## Design

On wide screens, the app uses a persistent rounded sidebar for brand, patient navigation, privacy reassurance, urgent help, and account access. The main workspace sits in a separate translucent panel with a lightweight top bar and centered content. On narrow screens, the shell collapses into a compact top area with horizontally scrollable navigation and stacked content.

The darkest two greens form the page and sidebar. Mid greens create layered panels and borders. `#8EB69B` is the accent and focus color, while `#DAF1DE` is the main text and bright action surface. Glows are subtle and green-only. Existing red urgent/error semantics remain because replacing them with green would hide safety meaning.

Forms, panels, banners, buttons, lists, and cards inherit the same glass treatment. Inputs remain visually distinct and opaque enough for legibility. Motion is limited to hover/focus elevation and is disabled for reduced-motion users.

## Acceptance

- The shared shell exposes a semantic patient workspace sidebar and retains banner, navigation, main, footer, skip-link, and urgent-help landmarks.
- All six supplied palette colors are used as the design foundation.
- Main text, muted text, actions, focus states, and disabled controls retain WCAG contrast targets.
- Existing patient tests, type checking, linting, formatting, and production build pass.
- Desktop and mobile screenshots show no clipping, unreadable content, or broken forms.
