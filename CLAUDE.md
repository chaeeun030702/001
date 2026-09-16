# Project Memory

## UI / Design System Standard (applies to ALL UI work)

Whenever you generate, modify, or review **any** user interface in this
project — product UIs, dashboards, admin tools, internal systems, guide
sites, landing pages, prototypes, or enterprise applications, in any
framework or output medium — you **must** follow the design specification at:

@docs/design/enterprise-ai-ui-standards.md

Treat that document as the single source of truth for design. Its rules take
precedence over your own default UI patterns and design assumptions.

### Key expectations (see the spec for the authoritative detail)

- Honor its confidence tags: `[Must]` (mandatory), `[Strong]` (default),
  `[Normalize]`, `[Fallback]`, `[Check]`.
- Use the semantic design tokens (colors, typography, spacing, radius,
  shadow) from the spec — never hardcode ad-hoc hex values, font sizes, or
  style constants when an equivalent token exists.
- Primary interaction color is Blue (`#0F6FFF` light / `#3F8CFF` dark).
  Keep warm accents out of primary actions.
- Use Pretendard-centered typography and the approved typography scale.
- Light-first enterprise tone: hierarchy, spacing, borders, and semantic
  color over decorative effects. Derive dark mode from the dark tokens, not
  by inverting light mode.
- Reuse existing design-system components before creating new ones; if a new
  one is needed, extend the existing design language and semantics.
- Follow the accessibility rules (keyboard, visible focus, label
  association, color-plus-text for errors).

### Brand assets

The spec references official assets under `./assets/logo/`, `./assets/icon/`,
and `./assets/avatar/`. These are **not** yet present in this repository. Per
the spec, if a required brand asset (logo, icon, avatar) is missing, do not
recreate, approximate, or substitute it — report that the official asset is
missing and request it.

### Reusing this standard in other projects

To apply this same standard to another repository, copy
`docs/design/enterprise-ai-ui-standards.md` and this `CLAUDE.md` UI section
into that project (and its brand assets under `assets/`).
