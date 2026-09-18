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

### Override: ignore the logo / brand rules

**Ignore all logo and brand-mark rules in the spec** (Section 4 "Brand And
Logo", the favicon/app-icon requirements in 4.2, and the header brand-lockup
rules). Specifically:

- Do **not** require, request, or report missing official logo assets
  (`./assets/logo/`). Missing-logo behavior in Section 4.4 does not apply —
  never block on a logo asset.
- Do **not** add the GS symbol favicon/app-icon declarations required by the
  spec. Use a plain or omitted favicon as appropriate.
- The header brand-lockup rules (logo + divider + service name) do not
  apply; use a plain text service/product name where a brand lockup would go.

All other rules of the spec (color, typography, layout, components,
accessibility, dark theme, icons, spacing, radius, shadow) still apply.

### Other brand assets

The spec also references `./assets/icon/` and `./assets/avatar/`. These are
not present in this repository. Per the spec, if a required icon or avatar
asset is missing, do not recreate or substitute it — report that it is
missing and request it. (This does not apply to logos, which are ignored per
the override above.)
