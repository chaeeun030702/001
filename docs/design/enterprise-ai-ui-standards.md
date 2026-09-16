# Enterprise AI Design System Specification

This document is the authoritative design specification for AI-generated user interfaces.

Use this file as the primary reference when generating product UIs, dashboards, admin tools, internal systems, guide sites, and enterprise applications.

The purpose of this specification is to ensure that all AI-generated interfaces follow the same design principles, semantic tokens, component patterns, interaction rules, and accessibility standards.

When this document is provided to an AI coding agent, the agent must prioritize the rules defined here over its own design assumptions or default UI patterns.

This specification is based on the organization's design system and should be treated as the single source of truth for UI generation.

---

## 1. Purpose

This document is an implementation-oriented UI specification, not a marketing summary.

The goal is to reduce output variance and maintain visual consistency when AI generates production-facing user interfaces.

Prioritize explicit design rules, semantic tokens, component patterns, layout principles, and accessibility standards over subjective visual interpretation.

When a design requirement is not explicitly defined in this specification, preserve the existing design language and extend it in a consistent manner.

New components, layouts, and interaction patterns may be created when necessary, but they should follow the same semantic structure, visual hierarchy, spacing system, typography rules, and accessibility principles defined in this specification.

Avoid arbitrary visual styles, inconsistent patterns, and unsupported design decisions.

---

## 2. Reading Rules For AI

Use the following confidence tags when interpreting this specification:

`[Must]`
Treat as a mandatory implementation rule. Do not override unless explicitly instructed.

`[Strong]`
Represents a recommended pattern and should be used as the default approach unless product requirements require otherwise.

`[Normalize]`
Convert source-specific, design-tool, or legacy naming into clear and maintainable implementation naming while preserving the original meaning.

`[Fallback]`
The specification does not provide sufficient detail. Apply accessible, conventional, and widely accepted UI patterns.

`[Check]`
Requires visual or product review before being treated as a permanent design standard.

---

## 3. Product Tone

### 3.1 Visual Direction

`[Must]` The system should feel calm, trustworthy, modern, and operational.

`[Must]` Use a light-first enterprise UI tone, not a campaign or editorial style.

`[Must]` Visual emphasis should come from hierarchy, spacing, borders, semantic color usage, and layout rhythm, not decorative effects.

`[Must]` Avoid oversized gradients, playful blobs, random illustrations, or novelty-heavy styling.

### 3.2 Core Characteristics

`[Must]` Primary interactive color: `Blue/50 (#0F6FFF)`.

`[Must]` Primary content text should use dark charcoal tones centered around `#1D1F24`.

`[Must]` Base surfaces should be white or cool-neutral.

`[Must]` Use Pretendard as the primary typeface.

`[Must]` Maintain a minimal shadow system.

`[Strong]` Trust should come from clarity, consistency, structure, and information hierarchy rather than visual ornamentation.

---

## 4. Brand And Logo

### 4.1 Official Logo Assets

`[Must]` Use only the official GS E&C logo assets provided in the design-system asset directory.

Asset Location:

`./assets/logo/`

Available Assets:

- `Mode=OnWhite, Language=Kor.svg`
- `Mode=OnWhite, Language=Eng.svg`
- `Mode=OnColor, Language=Kor.svg`
- `Mode=OnColor, Language=Eng.svg`
- `Mode=Symbol-GS.svg`

`[Must]` Do not recreate the logo using text, CSS, AI-generated graphics, or custom vector artwork.

`[Must]` Do not replace the logo with placeholders, initials, emojis, icons, or decorative symbols.

### 4.2 Logo Selection Rules

`[Must]` Use the OnWhite logo variants on light backgrounds.

`[Must]` Use the OnColor logo variants on dark backgrounds.

`[Must]` Select the Korean or English logo version according to the language of the interface.

`[Must]` Use `Mode=Symbol-GS.svg` for favicons, app icons, compact navigation layouts, and responsive mobile layouts where the full logotype cannot fit comfortably.

`[Must]` When implementing a browser favicon, tab icon, shortcut icon, or similar compact brand marker, use `./assets/logo/Mode=Symbol-GS.svg`.

`[Must]` In web implementations, declare favicon metadata in the document head so that the browser tab and bookmark icon actually use `./assets/logo/Mode=Symbol-GS.svg`.

`[Strong]` If the platform supports favicon metadata or app-icon declarations, point those declarations to `./assets/logo/Mode=Symbol-GS.svg` rather than improvising a new compact mark.

`[Strong]` In responsive layouts, switch from the full logotype to the GS symbol before the logo becomes visually crowded or unreadable.

### 4.3 Logo Usage

`[Must]` For co-brand lockups such as `GS건설 | 서비스명`, place the official logo on the left and the service name on the right.

`[Must]` Separate the logo and service name using a thin vertical divider.

`[Must]` Service names within header branding areas must remain on a single line and should not wrap.

`[Must]` In implementation terms, treat the service-name text in header brand lockups as a no-wrap element. Do not allow the service name to break into two lines beside the logo.

`[Strong]` If horizontal space becomes tight, reduce surrounding header congestion or switch to the approved compact logo/symbol behavior before allowing the service name to wrap.

`[Must]` Preserve the original logo proportions.

`[Must]` Do not stretch, compress, recolor, outline, crop, rotate, or apply semantic colors to the logo.

`[Strong]` Service names should remain visually distinct from the logo and should be treated as a separate text element.

`[Check]` Exact clear-space and minimum-size requirements should follow the latest official brand guideline when available.

### 4.4 Asset Failure Behavior

`[Must]` If the required logo asset is unavailable, explicitly report that the official asset is missing.

`[Must]` Request the correct asset rather than generating, approximating, or substituting the logo.

---

## 5. Typography

### 5.1 Typeface

`[Must]` Primary font family:

`"Pretendard Variable", "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", "Segoe UI", Roboto, -apple-system, BlinkMacSystemFont, sans-serif`

`[Strong]` Monospace font family for data, code, IDs, and technical content:

`"SF Mono", SFMono-Regular, Menlo, Consolas, monospace`

### 5.2 Weight Discipline

`[Must]` Use primarily font weights `400`, `600`, and `700`.

`[Must]` Avoid unnecessary weight variation within the same interface.

`[Must]` Do not use font weights below `400` or custom intermediate weights unless explicitly required.

`[Strong]` Recommended usage:

- `400` for body content
- `600` for labels, subtitles, and emphasis
- `700` for headings, page titles, and key metrics

### 5.3 Typography Scale

`[Must]` Use only typography tokens defined in the official design system.

`[Must]` Do not create custom font sizes, line heights, weights, or typography styles outside the approved scale.

Approved Typography Tokens:

| Token | Size | Weight |
| --- | --- | --- |
| Display1 | 64px | 700 |
| Display2 | 56px | 700 |
| Display3 | 44px | 700 |
| Display4 | 36px | 700 |
| Title1 | 32px | 700 |
| Title2 | 28px | 700 |
| Title3 | 24px | 700 |
| Heading1 | 22px | 700 |
| Heading2 | 20px | 700 |
| Heading3 | 18px | 700 |
| Body1 | 16px | 400 |
| Body2 | 15px | 400 |
| Body3 | 14px | 400 |
| Label1 | 13px | 600 |
| Label2 | 12px | 600 |
| Caption1 | 11px | 400 |
| Caption2 | 10px | 400 |
| Caption3 | 9px | 400 |

`[Strong]` Prefer existing typography tokens before creating new text patterns.

`[Strong]` Typography hierarchy should be created through size and weight differences rather than color changes.

### 5.4 Numeric Rules

`[Must]` Use tabular numerals for tables, transaction amounts, financial data, metrics, and aligned numeric content.

`[Strong]` Proportional numerals are acceptable for display-oriented content such as summary cards, dashboards, and hero metrics.

`[Must]` Do not mix tabular and proportional numerals within the same data context.

---

## 6. Color System

### 6.1 Primary And Secondary Interaction Colors

- `[Must]` `primary/default`: Light `#0F6FFF` / Dark `#3F8CFF`
- `[Must]` `primary/hover`: Light `#0E65E8` / Dark `#0F6FFF`
- `[Must]` `primary/active`: Light `#0B4FB5` / Dark `#0E65E8`
- `[Strong]` `secondary/default`: Light `#1D1F24` / Dark `#E9EBEF`
- `[Strong]` `secondary/hover`: Light `#282B33` / Dark `#CCD0D6`
- `[Strong]` `secondary/active`: Light `#333741` / Dark `#ADB4BD`

### 6.2 Text, Surface, And Line Roles

- `[Strong]` `text/strong`: Light `#000000` / Dark `#FFFFFF`
- `[Strong]` `text/default` (raw Figma alias `Text/Defult`): Light `#1C1C1C` / Dark `#EBECED`
- `[Strong]` `text/sub`: Light `#303030` / Dark `#C4C4C4`
- `[Strong]` `text/caption`: Light `#737373` / Dark `#8A8A8A`
- `[Strong]` `text/hint`: Light `#B0B0B0` / Dark `#737373`
- `[Strong]` `text/disabled`: Light `#C4C4C4` / Dark `#5C5C5C`
- `[Strong]` `text/inverse`: Light `#EBECED` / Dark `#000000`
- `[Strong]` `bg/default` (raw Figma alias `BG/Nomal/Normal`): Light `#FFFFFF` / Dark `#1D1F24`
- `[Must]` In light mode, the global header background should use `bg/default` (`BG/Nomal/Normal`) white `#FFFFFF` unless the product explicitly defines a different shell treatment.
- `[Must]` In dark mode, both the global header and the desktop side navigation should use `bg/default` (`BG/Nomal/Normal`) `#1D1F24` as the default shell background unless the product explicitly defines a different dark shell treatment.
- `[Strong]` `bg/content-canvas`: Light `#EEF1F5` / Dark `#15171C`
- `[Must]` In shell-based dashboard layouts, visually separate the main content canvas from the header and side-navigation shell. In light mode, a subtle cool-neutral content background such as `#EEF1F5` is appropriate.
- `[Must]` In dark mode, the main content canvas should be darker than the header and desktop side navigation. A safe default is `#15171C` for the content area while the shell remains `#1D1F24`.
- `[Strong]` `bg/alternative` (raw Figma alias `BG/Nomal/Alternative`): Light `#F2F3F6` / Dark `#282B33`
- `[Strong]` `bg/elevated` (raw Figma alias `BG/Nomal/Elevated`): Light `#F2F3F6` / Dark `#333741`
- `[Strong]` `bg/disabled` (raw Figma alias `BG/Nomal/Disabbled`): Light `#E2E4E9` / Dark `#282B33`
- `[Strong]` `bg/inverse`: Light `#1D1F24` / Dark `#FFFFFF`
- `[Strong]` `surface/default`: Light `#FFFFFF` / Dark `#1D1F24`
- `[Strong]` `surface/alternative-1`: Light `#F2F3F6` / Dark `#282B33`
- `[Strong]` `surface/alternative-2`: Light `#E2E4E9` / Dark `#333741`
- `[Strong]` `surface/inverse`: Light `#282B33` / Dark `#FFFFFF`
- `[Strong]` `divider/strong`: Light `#E2E4E9` / Dark `#333741`
- `[Strong]` `divider/default`: Light `#E9EBEF` / Dark `#282B33`
- `[Strong]` `divider/subtle`: Light `#F2F3F6` / Dark `#1D1F24`
- `[Strong]` `border/strong`: Light `#CCD0D6` / Dark `#4A505F`
- `[Strong]` `border/default`: Light `#E2E4E9` / Dark `#333741`
- `[Strong]` `border/subtle`: Light `#E9EBEF` / Dark `#282B33`
- `[Strong]` `border/decorative`: Light `#F2F3F6` / Dark `#1D1F24`
- `[Strong]` `overlay/dimming`: `#1D1F24 50%` in both light and dark

### 6.3 Semantic Status Colors

- `[Must]` `status/success`: Light `#15B874` / Dark `#44C690`
- `[Must]` `status/warning`: Light `#FFA833` / Dark `#FFB95C`
- `[Must]` `status/error`: Light `#E63B3B` / Dark `#EB5E5E`

### 6.4 Accent Colors

- `[Strong]` `accent/orange`: Light `#FE6F3F` / Dark `#FE8C65`
- `[Strong]` `accent/purple`: Light `#B357FF` / Dark `#C279FF`
- `[Strong]` `accent/pink`: Light `#F553DA` / Dark `#F775E1`
- `[Strong]` `accent/skyblue`: Light `#00BDDE` / Dark `#33CAE5`

### 6.5 Usage Rules

- `[Must]` Blue is the main interactive hue.
- `[Must]` Do not use warm accents like orange or pink as the primary action color.
- `[Must]` Semantic colors communicate state, not primary action hierarchy.
- `[Strong]` Accent colors such as orange, purple, pink, and sky blue can exist in the system, but keep them out of core interaction unless explicitly required.
- `[Must]` When dark mode is supported, use the recovered dark tokens directly rather than approximating them through automatic inversion.

### 6.6 Raw Token Naming

- `[Normalize]` If source Figma tokens contain misspellings such as `Nomal`, `Defult`, or `Disabbled`, keep them only in import/codegen/alias layers.
- `[Normalize]` Public CSS variables, exported token keys, component props, and engineering docs must use normalized names.

---

## 7. Layout And Responsive Model

### 7.1 Default Direction

`[Must]` For enterprise dashboards and operational products, use a desktop-first structure.

`[Strong]` For simpler service or product flows, maintain mobile-first clarity and scale the layout up carefully.

`[Must]` The UI should support both operational desktop shells and smaller responsive breakpoints.

### 7.2 Breakpoints

`[Strong]` XS: single-flow mobile screen.

`[Strong]` S: compact tablet.

`[Strong]` M: spacious tablet.

`[Strong]` L-XL: full desktop shell.

### 7.3 Mobile Baseline

`[Strong]` Mobile baseline can safely begin from 375px.

`[Strong]` Default horizontal padding around 20px is appropriate for compact screens.

`[Must]` Touch targets should typically remain between 40px and 56px.

### 7.4 Desktop Shell

`[Must]` On desktop and wide layouts, the system may use sticky global headers, fixed or persistent side navigation, multi-column dashboard sections, cards, filters, action bars, and tables.

`[Must]` In light mode, the sticky global header should use BG/Normal/Normal (#FFFFFF) by default.

`[Must]` In dark mode, the sticky global header and attached desktop side navigation should use BG/Normal/Normal (#1D1F24) by default.

`[Must]` When the product uses a desktop shell with header, side navigation, and main content area, visually separate the main content canvas from the shell background.

`[Strong]` A safe shell split is header/navigation = #FFFFFF and content = #EEF1F5 in light mode, and header/navigation = #1D1F24 with content = #15171C in dark mode.

### 7.5 Side Navigation

`[Must]` Use side navigation mainly for dashboards, admin tools, detail IA, and operational products. Do not use it for every shallow page.

`[Must]` When side navigation is part of the main IA on desktop, keep it fixed or persistent under the global header.

`[Must]` Treat desktop side navigation as part of the app shell attached to the left side of the layout. It should not look like a floating card.

`[Must]` The desktop side navigation should not scroll away with the main content area. The content pane should scroll independently.

`[Must]` If the side navigation is taller than the viewport, only the side-navigation region should scroll internally.

`[Must]` On XS screens, convert persistent side navigation into a drawer, sheet, or similar collapsible pattern.

`[Must]` Do not implement side navigation as a flat unstructured link list. It should behave like a sectioned information-architecture tree.

`[Must]` Do not render desktop side navigation as a rounded, detached, card-like panel with independent shadow. Prefer a continuous vertical surface with a clear right border or shell boundary.

`[Strong]` Use a SideNav -> SideNavSection -> SideNavItem structure.

`[Must]` The default desktop form is a fixed, persistent, expanded side navigation with visible labels.

`[Must]` Unless explicitly requested, do not add collapsed, icon-only, or fold/unfold behavior to the desktop side navigation.

`[Strong]` Expanded desktop side navigation should show icon, readable label, optional dropdown caret, optional badge, and visible section grouping.

`[Strong]` Compact navigation should behave like an icon-recognition rail, not a squeezed text menu.

`[Strong]` Expanded shell width should be around 300px. Compact shell width should be around 80px.

`[Strong]` In expanded mode, group large menu clusters with dividers and consistent vertical breathing space.

`[Strong]` Preserve semantic grouping even in compact mode.

`[Strong]` Support structural row types beyond clickable menu rows, including lightweight title rows and section header rows.

`[Strong]` Side navigation items should support independent concerns: icon, label, badge, dropdown, depth, open state, and disabled state.

`[Must]` Square or boxed marks shown in references should be interpreted as icon slots, not decorative placeholder shapes.

`[Strong]` Choose icons that match the meaning of each menu item, such as dashboard, home, document, folder, chart, settings, user, bell, or layer.

`[Must]` Use a consistent icon family, stroke weight, and optical size across the entire side navigation.

`[Strong]` Support at least depth=1 and depth=2.

`[Strong]` Use about 48px row height for depth=1 items and about 44px for depth=2 child items.

`[Strong]` Compact rail items should be close to square icon targets, around 56px by 56px.

`[Strong]` Expandable parents should show open and closed state through caret direction, not only through child visibility.

`[Must]` Let the container own section dividers and group spacing. Do not push that responsibility into each individual item.

`[Strong]` A safe engineering model is:
`SideNavItem({ mode: 'expanded' | 'compact', depth: 1 | 2, icon?, label?, badgeCount?, expandable?, open?, state })`

`[Strong]` Recommended visible states include default, hovered, focused, selected, and disabled when needed.

### 7.6 Header Search

`[Must]` If the global header includes search, render only the input control itself.

`[Must]` Do not place visible adjacent labels such as Search or 통합 검색 next to the header search field.

`[Strong]` Use placeholder text and accessible labeling instead.

### 7.7 Header Utilities, Icons, And Profile

`[Must]` Header utility actions such as theme toggle, notifications, help, or shortcuts should render as icon-only buttons.

`[Must]` Use a consistent icon family across the interface.

`[Must]` Do not mix filled, outlined, rounded, and decorative icon styles within the same product.

`[Strong]` Use simple enterprise-style icons with consistent stroke weight and visual balance.

`[Strong]` Prefer the official WSG icon assets when available.

`[Must]` Use a 24px x 24px icon canvas as the default base size for header utility icons and compact profile icons.

`[Strong]` For standard header utilities, use regular icon variants with about 1.5px stroke weight as the safe default.

`[Must]` Do not style default header utility icon buttons with outlined boxes or heavy button chrome.

`[Strong]` Use a quiet circular or rounded hover background when needed. The resting state should remain clean and borderless.

`[Must]` The header profile trigger must be a single-row layout consisting only of avatar and user name.

`[Must]` Do not display department, role, title, email, or other account metadata directly in the header profile trigger.

`[Must]` Detailed account information such as department, role, account settings, and logout should appear only inside an anchored profile menu, popover, or dropdown.

`[Strong]` The profile trigger should visually match the avatar component used in the official design system.

`[Must]` Do not generate custom profile illustrations, decorative avatar artwork, or unrelated profile glyphs.

`[Must]` The header profile trigger should show only the profile photo or avatar plus the user name in the default closed state.

`[Must]` If a real user photo is unavailable or unnecessary, default to the WSG avatar system rather than an outline profile icon or improvised illustration.

`[Must]` For this project's default compact profile representation, use the local avatar asset at `./assets/avatar/default-profile-avatar.svg` before falling back to text initials.

`[Strong]` If that local default avatar asset is unavailable, using a single surname character such as `김` inside the avatar is a safe compact-header fallback in Korean enterprise products.

`[Strong]` Keep the profile trigger visually aligned with the WSG avatar component family.

`[Fallback]` If detailed profile behavior is not fully specified, use a conventional accessible profile menu pattern: click to open, outside click or Escape to close, visible focus handling, and menu items large enough for pointer use.

`[Strong]` When theme, notification, and profile affordances appear together in the header, keep the utility icons in the same icon family and weight, and keep the profile trigger visually aligned with the WSG avatar component family.

`[Must]` Do not keep department, role, or long descriptive account text permanently exposed inline in the header bar.

---

## 8. Component Direction

`[Must]` Before creating new UI, check whether an equivalent component pattern already exists in the official design system or product kit.

`[Must]` Reuse established components whenever possible instead of creating visually similar duplicates.

`[Strong]` If no suitable component exists, create a new component that preserves this specification's token system, spacing logic, typography hierarchy, interaction behavior, and accessibility rules.

`[Strong]` When extending the system, document why the existing component set was insufficient rather than silently introducing a parallel component family.

### 8.1 Buttons

`[Must]` Primary buttons should use the Primary semantic color defined in the Color System.

Reference values:
Light = #0F6FFF
Dark = #3F8CFF

`[Must]` Primary buttons should use white text.

`[Strong]` Primary button labels should typically use Body1 (16px / 600) or Label1 (13px / 600) depending on component size.

`[Strong]` Border radius should generally remain within the 8px to 12px range.

`[Strong]` Support primary, secondary, dark, and danger actions.

`[Strong]` A stable model is:

`size × style × state × icon mode`

`[Strong]` Treat loading as a state, not a whole new visual family.

`[Must]` Icon-only buttons require accessible labels.

### 8.2 Cards

- `[Must]` Default card surface is white.
- `[Must]` Use borders and spacing before relying on shadow.
- `[Strong]` Standard radii:
  - `8px` compact
  - `12px` comfortable
  - `16px` featured
- `[Strong]` Financial cards should give strong emphasis to amount hierarchy.

### 8.3 Inputs

- `[Strong]` Inputs may use a low-noise, clean field shell or underline-style treatment depending on product context.
- `[Must]` Focus state must be clear and accessible.
- `[Must]` Placeholder and helper text should remain readable and subdued.
- `[Must]` Placeholder text must not be treated as a replacement for a real label.
- `[Must]` Inputs should be explicitly associated with labels and, when relevant, helper text or error text.
- `[Must]` Validation and error messaging should remain programmatically associated with the relevant field.

### 8.4 Selection Controls

- `[Must]` Use `Checkbox` for independent multi-select decisions.
- `[Must]` Use `Radio` for small sets of mutually exclusive options.
- `[Strong]` When options become long, dense, or category-grouped, prefer `Select` instead of overextending radio groups.
- `[Must]` Use `Switch` only for immediate on/off state changes that take effect directly.
- `[Strong]` If confirmation or later submission is required, prefer `Checkbox` over `Switch`.
- `[Must]` Selection controls must remain clearly associated with visible labels.
- `[Strong]` Groups of related options should preserve clear group semantics and accessible labeling.

### 8.5 Tables And Lists

- `[Must]` Tables and list rows should prioritize aligned numbers, strong label hierarchy, and clean row scanning.
- `[Strong]` Transaction or operational rows often need at least `52px` row height.
- `[Must]` Use tabular numerals for aligned financial values.
- `[Strong]` Long datasets should support explicit pagination, filtering, or search rather than forcing excessively long continuous lists.

### 8.6 Overlays

- `[Must]` Dialog is a true blocking modal in this system, not a tooltip-like lightweight overlay.
- `[Must]` Dialogs must use a backdrop/scrim and block background interaction.
- `[Strong]` Dialog content should be slot-based:
  - title area
  - contents area
  - function area if needed
  - button area
- `[Strong]` Bottom sheets should read as upward-emerging surfaces with rounded top corners only.

### 8.7 Avatars

`[Must]` Treat avatar as a formal system component, not an ad-hoc image style.

`[Must]` The recovered WSG avatar component is circular and built from:

- size
- type
- status
- color

`[Must]` Supported avatar sizes are:

- `lg = 40px`
- `md = 32px`
- `sm = 24px`

`[Must]` Supported avatar types are:

- `Initial`
- `Avatar`
- `Check`

`[Normalize]` Some recovered source variants use the misspelled raw label `Avata`. Keep that only in import/codegen mappings and expose the normalized public name `Avatar`.

`[Must]` Supported status variants are:

- `Online`
- `Busy`
- `Offline`
- `None`

`[Must]` Supported color families are:

- `Default`
- `Primary`
- `Neutral`

`[Must]` When an avatar is referenced without an explicit variant override, use the default avatar style defined in the official design system.

`[Strong]` Use the default avatar asset and visual proportions defined in the official design system.

`[Strong]` In this project, the default compact profile/avatar asset may be:

`./assets/avatar/default-profile-avatar.svg`

especially for header account affordances and small anchored profile summaries.

`[Strong]` Initial is for text-based user/account identification, Avatar is for person/profile representation, and Check is for selection/completion-style identity markers.

`[Strong]` For compact account affordances such as the header profile trigger, `Initial` may be preferred over the generic avatar glyph when the product wants faster personal recognition.

`[Strong]` When the compact header-profile variant uses `Initial`, the safe default is Color=Secondary with white text.

`[Strong]` Status indicators should read as small anchored presence dots attached to the avatar edge rather than separate badges floating away from the component.

`[Strong]` A safe semantic mapping is:

- `Online -> status/success`
- `Busy -> status/error`
- `Offline -> neutral`
- `None -> no status indicator`

`[Must]` If a real profile photo is unavailable, unnecessary, or visually inconsistent, use the system avatar types or Initial variants rather than unrelated illustration styles.

`[Must]` Do not generate custom profile illustrations, decorative avatar artwork, or unrelated profile glyphs.

`[Must]` Use a neutral avatar style consistent with enterprise product interfaces.

`[Strong]` For header profile triggers, sm or a compact 24px avatar footprint is the safe default.

`[Strong]` Use larger avatar sizes mainly inside menus, profile summaries, lists, member tables, or detail views.

`[Must]` Keep avatar silhouettes circular unless the product explicitly defines a different identity shape system.

### 8.8 Sliders

- `[Strong]` Treat continuous, discrete, centered, and range sliders as separate families rather than one monolithic API.
- `[Must]` Support keyboard control, focus visibility, and accessible value text for all slider patterns.

### 8.9 Feedback And Helper Components

- `[Must]` Use persistent `Alert` patterns for important page-level or section-level messages that must remain visible until acknowledged or no longer relevant.
- `[Strong]` Use `Toast` for transient action feedback such as save success, deletion, retry result, or lightweight warnings.
- `[Must]` Do not rely on toast alone for critical blocking errors, irreversible warnings, or information that must remain visible for decision-making.
- `[Strong]` `Badge` should be used for short status, category, or label signals, not as a replacement for full descriptive text.
- `[Strong]` Numeric notification counts should use a dedicated count-badge treatment rather than a generic status badge.
- `[Must]` Icon-only controls should provide accessible labeling, and `Tooltip` is the preferred supplementary helper surface when the visual UI shows only the icon.
- `[Strong]` Do not add tooltips to controls that already have clear persistent text labels unless additional clarification is genuinely needed.
- `[Strong]` Tooltip copy should remain brief and should usually fit within a single short line.

### 8.10 Loading States

- `[Must]` Treat loading as a contextual state pattern, not as one generic visual pasted everywhere.
- `[Strong]` Use `Skeleton` placeholders when the final layout structure is already known, such as cards, lists, tables, and content blocks.
- `[Strong]` Use compact inline `Spinner` patterns for button actions, compact data refresh, or localized loading feedback.
- `[Strong]` Use a larger centered loading treatment only for initial page loads, route transitions, or full-screen blocking states.
- `[Must]` While a control is actively processing and repeat interaction should be prevented, disable the relevant interactive control.
- `[Strong]` Loading containers should communicate busy state accessibly when appropriate.

---

## 9. Interaction And Accessibility

### 9.1 General

- `[Must]` Keyboard activation must work on interactive controls.
- `[Must]` Focus-visible styling must be clearly visible.
- `[Must]` State changes should not depend on color alone when accessibility requires extra affordance.

### 9.2 Dialog

- `[Must]` Use focus trap and focus return for modal dialogs.
- `[Must]` `Escape` should dismiss dismissible modal surfaces.
- `[Must]` Backdrop interaction should follow the intended modal pattern rather than feeling like a lightweight popover.

### 9.3 Icon State

- `[Must]` Express icon state changes through semantic color, opacity, or parent-surface treatment.
- `[Must]` Do not redraw the icon shape just to represent hover, pressed, or disabled states.

### 9.4 Fallback Behavior

- `[Fallback]` If the guide does not specify exact behavior, use accessible defaults similar to well-understood systems like Material or shadcn.
- `[Fallback]` Use those systems as behavioral references only, not visual templates.
- `[Must]` Final visuals must still resolve through this document's tokens, density, spacing, and component semantics.
- `[Must]` Disabled components must not be interactive and should be visually distinguishable from enabled components.
- `[Must]` Validation errors should be communicated through both color and text, not color alone.

---

## 10. Icon Rules

`[Must]` Default icon box: 24px.

`[Strong]` Compact variants may use 20px or 16px when space is limited.

`[Must]` Do not distort icon aspect ratios.

`[Strong]` Line icons should remain within a consistent stroke family, typically around 1.5px to 2px.

`[Must]` Use one icon library consistently throughout a product.

`[Must]` Do not mix unrelated icon libraries within the same interface without a deliberate system reason.

`[Strong]` Refer to the official icon assets located in:

`./assets/icon/`

for preferred icon style, stroke weight, proportions, and visual language.

`[Strong]` When selecting or creating new icons, maintain consistency with the provided icon assets.

`[Must]` Do not introduce a different icon family when equivalent icons exist in the provided asset set.

`[Must]` Do not use decorative, illustrative, emoji-style, filled mascot-style, or 3D icons in product UI.

`[Strong]` Choose icons that accurately reflect the destination or action, such as search, settings, folder, notification, mail, edit, camera, or communication functions.

`[Must]` Use inline SVG icons rather than raster images for product UI.

---

## 11. Shadow, Radius, And Depth

### 11.1 Radius

`[Must]` Typical radius range: 8px to 16px.

`[Strong]` Use:

- 4px for compact badges or tiny elements.
- 8px for inputs and compact cards.
- 12px for standard cards.
- 16px for larger sheets and featured surfaces.
- 9999px for pills, chips, and toggles.

### 11.2 Shadow

`[Must]` Keep shadows minimal, neutral, and functional.

`[Must]` Do not use heavy, blurred, colorful, trendy, or decorative shadow effects.

`[Strong]` Recommended shadow levels:

- level 0: none
- level 1: 0 1px 3px rgba(0,0,0,0.06)
- level 2: 0 2px 8px rgba(0,0,0,0.08)
- level 3: 0 4px 12px rgba(0,0,0,0.12)

`[Strong]` Prefer borders, spacing, and surface contrast before increasing shadow depth.

### 11.3 Depth Usage

`[Strong]` Cards should feel low, quiet, and close to the surface.

`[Strong]` Dropdowns, popovers, and floating panels may use elevated shadow levels.

`[Must]` Blocking dialogs and modal surfaces should use the highest approved elevation level.

`[Must]` Do not use shadow as the primary method of visual hierarchy. Prefer typography, spacing, layout structure, and semantic color first.

---

## 12. Dark Theme Guidance

`[Strong]` The system is light-first, but dark mode can be supported.

`[Must]` In dark mode, use dedicated dark surfaces and border logic rather than applying simple opacity adjustments from light mode.

`[Must]` Use the following semantic tokens as the default dark-mode baseline:

`bg/default`: `#1D1F24`
`bg/content-canvas`: `#15171C`
`bg/alternative`: `#282B33`
`bg/elevated`: `#333741`

`text/default`: `#EBECED`
`text/sub`: `#C4C4C4`
`text/caption`: `#8A8A8A`

`border/default`: `#333741`
`border/strong`: `#4A505F`

`primary/default`: `#3F8CFF`

`status/success`: `#44C690`
`status/warning`: `#FFB95C`
`status/error`: `#EB5E5E`

`[Must]` In dark-mode shell areas, use `#1D1F24` as the default background for both the global header and desktop side navigation.

`[Must]` In dark-mode dashboard shells, keep the main content canvas darker than the shell. A safe default is `#15171C` for the content background under the fixed header and side navigation.

`[Strong]` Keep dimming at `#1D1F24 50%` in both light and dark modes unless an overlay-specific contract overrides it.

`[Check]` Before freezing a dark-theme contract, visually review at least:

- page canvas
- card
- input
- table
- dialog

`[Check]` Verify contrast, readability, and visual hierarchy before finalizing dark-theme implementation.

---

## 13. Do And Do Not

### Do

`[Must]` Use Pretendard-centered typography.

`[Must]` Keep blue as the primary interaction color.

`[Must]` Use tabular numerals for aligned financial data.

`[Must]` Use the official logo assets provided in `./assets/logo/` for brand representation.

`[Must]` Keep side navigation fixed or persistent on desktop when it is part of the main dashboard IA.

`[Must]` Keep header search as an input-only pattern.

`[Must]` Keep the default header profile compact: avatar/photo plus user name only, with detailed identity and logout actions inside a profile dropdown.

`[Strong]` Reuse the avatar system consistently across profile triggers, member lists, owner cells, and user/account surfaces.

`[Strong]` Prefer the default neutral no-status avatar family first, and add other status/color variants only when the workflow meaning is explicit.

`[Strong]` Prefer the official icon assets located in `./assets/icon/` and maintain their visual style when introducing new icons.

`[Strong]` Use subtle informational backgrounds such as blue-tinted surfaces for quiet emphasis.

### Do Not

`[Must]` Do not replace the logo with text or fake graphics when the official asset is available.

`[Must]` Do not treat warm accent colors as the main action hue.

`[Must]` Do not build this like a marketing landing page full of decorative effects.

`[Must]` Do not style desktop side navigation like a floating card, utility widget, or detached promo panel.

`[Must]` Do not keep header utility icons inside always-visible outlined boxes unless the product explicitly requires a more button-like treatment.

`[Must]` Do not keep team name, department, and role permanently expanded inline in the header profile area.

`[Must]` Do not invent custom avatar shapes, random illustration portraits, or mixed avatar styles when the WSG avatar system is available.

`[Must]` Do not replace the default avatar family with an unrelated outline profile icon when the product is otherwise using the WSG avatar component system.

`[Must]` Do not overuse font weights.

`[Must]` Do not use oversized border radius beyond pills and toggles unless there is a deliberate system reason.

`[Must]` Do not collapse all overlay patterns into one generic modal or all slider patterns into one giant slider API.

---

## 14. Design Token Reference

`[Must]` These tokens represent the implementation reference of the design system.

`[Must]` Use these tokens when generating code, themes, design-token files, CSS variables, or framework-specific adapters.

`[Must]` Do not redefine token values independently when equivalent semantic tokens already exist.

`[Must]` Light and dark themes should be derived from these semantic token definitions.

`[Must]` Do not hardcode raw hex values, arbitrary spacing values, or ad-hoc style constants when equivalent semantic tokens or approved system values already exist.

```css
:root {
  --color-bg-page: #ffffff;
  --color-bg-content: #eef1f5;
  --color-bg-surface: #ffffff;
  --color-bg-surface-alt-1: #f2f3f6;
  --color-bg-surface-alt-2: #e2e4e9;
  --color-bg-inverse: #1d1f24;
  --color-text-strong: #000000;
  --color-text-primary: #1c1c1c;
  --color-text-secondary: #303030;
  --color-text-muted: #737373;
  --color-text-hint: #b0b0b0;
  --color-text-disabled: #c4c4c4;
  --color-text-inverse: #ebeced;
  --color-action-primary: #0f6fff;
  --color-action-primary-hover: #0e65e8;
  --color-action-primary-active: #0b4fb5;
  --color-action-secondary: #1d1f24;
  --color-action-secondary-hover: #282b33;
  --color-action-secondary-active: #333741;
  --color-border-default: #e2e4e9;
  --color-border-strong: #ccd0d6;
  --color-divider-default: #e9ebef;
  --color-status-success: #15b874;
  --color-status-warning: #ffa833;
  --color-status-danger: #e63b3b;
  --color-accent-orange: #fe6f3f;
  --color-accent-purple: #b357ff;
  --color-accent-pink: #f553da;
  --color-accent-skyblue: #00bdde;
  --color-overlay-scrim: rgba(29, 31, 36, 0.5);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-pill: 9999px;
  --shadow-level-0: none;
  --shadow-level-1: 0px 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-level-2: 0px 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-level-3: 0px 4px 12px rgba(0, 0, 0, 0.12);
  --shadow-level-4: 0px 8px 24px rgba(0, 0, 0, 0.16);
}

[data-theme="dark"] {
  --color-bg-page: #1d1f24;
  --color-bg-content: #15171c;
  --color-bg-surface: #1d1f24;
  --color-bg-surface-alt-1: #282b33;
  --color-bg-surface-alt-2: #333741;
  --color-bg-inverse: #ffffff;
  --color-text-strong: #ffffff;
  --color-text-primary: #ebeced;
  --color-text-secondary: #c4c4c4;
  --color-text-muted: #8a8a8a;
  --color-text-hint: #737373;
  --color-text-disabled: #5c5c5c;
  --color-text-inverse: #000000;
  --color-action-primary: #3f8cff;
  --color-action-primary-hover: #0f6fff;
  --color-action-primary-active: #0e65e8;
  --color-action-secondary: #e9ebef;
  --color-action-secondary-hover: #ccd0d6;
  --color-action-secondary-active: #adb4bd;
  --color-border-default: #333741;
  --color-border-strong: #4a505f;
  --color-divider-default: #282b33;
  --color-status-success: #44c690;
  --color-status-warning: #ffb95c;
  --color-status-danger: #eb5e5e;
  --color-accent-orange: #fe8c65;
  --color-accent-purple: #c279ff;
  --color-accent-pink: #f775e1;
  --color-accent-skyblue: #33cae5;
}
```

- `[Must]` These are framework-agnostic tokens.
- `[Must]` If your framework needs its own adapter, derive that adapter from these semantic tokens rather than treating a framework-specific theme object as source truth.

---

## 15. Known Ambiguities

`[Check]` Exact logo clear-space and minimum-size requirements are not fully defined in this specification and should follow official brand guidance when available.

`[Check]` Dark mode should be visually validated before being treated as a fully locked design contract.

`[Check]` Product-specific workflows may require additional components, layouts, or interaction patterns that are not explicitly covered in this specification.

`[Check]` When extending the system, preserve the existing design language, semantic token structure, typography hierarchy, spacing principles, and accessibility standards.

---

## 16. Short Prompt For Coding Agents

Use this when you want a condensed directive:

Build a calm, trustworthy, light-first enterprise UI using the design rules defined in this specification.

Use Pretendard typography, semantic color tokens, white and cool-neutral surfaces, and the Primary interaction color (#0F6FFF / #3F8CFF in dark mode).

Follow the official logo, icon, typography, color, layout, component, accessibility, and dark-theme rules defined in this document.

Use the official logo assets from ./assets/logo/ and the official icon assets from ./assets/icon/ when available.

For favicon, tab icon, or compact browser/app branding, use ./assets/logo/Mode=Symbol-GS.svg.

Use the approved typography scale, semantic color system, spacing principles, radius system, and shadow system. Do not invent new visual styles, colors, spacing values, component families, or interaction patterns unless explicitly required.

Reuse existing design-system components before creating new ones. If a new component is necessary, extend the existing design language instead of creating a parallel visual family.

For enterprise and dashboard products, use a desktop-first shell consisting of a sticky header, persistent side navigation, and independent content area scrolling. Convert persistent navigation into drawer or sheet patterns on small screens.

Keep header utilities compact and icon-based. Keep the default profile area compact as avatar plus user name, and place account details inside a profile menu. Use `./assets/avatar/default-profile-avatar.svg` as the default compact profile/avatar asset when available.

Keep the header brand lockup on one line: official logo on the left, divider, and service name on the right. Do not let the service name wrap into two lines.

Use accessible interaction patterns, visible focus states, keyboard support, semantic status colors, and appropriate loading patterns such as skeletons for known layouts, inline spinners for local actions, and toasts for transient feedback.

When requirements are not explicitly defined, extend the existing design language while maintaining consistency with this specification.

---

## 17. Recommendation

[Must] Use `01-enterprise-ai-ui-standards.md` as the primary implementation specification for AI-generated interfaces.

[Strong] When official GS E&C logo assets, icon assets, or approved visual resources are provided, always use them as the primary source. Do not substitute or recreate brand assets.

[Strong] Do not introduce new design patterns, colors, or components unless explicitly requested.