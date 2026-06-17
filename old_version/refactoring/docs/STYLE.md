# STYLE.md — Design System & CSS Architecture

Living specification for the Man in the Loop explorer UI. Update this file whenever tokens, rules, or CSS file scope change. See `CHANGELOG.md` for the dated history of changes.

---

## 1. Typography

### Root scale

```css
html { font-size: 120%; }  /* 1rem = 19.2px */
```

The 120% root is a deliberate design decision placing body text at ~19.2px — in Medium's editorial range (18px). It is not a mistake. Do not override it.

**Minimum floor: `--fs-xs` (~13.4px). Nothing in the UI goes below this.**

### Font-size tokens

| Token | rem | ~px | Usage |
|---|---|---|---|
| `--fs-xs` | `.70rem` | ~13.4 | Badges, IDs, stat labels, micro labels — **not** for interactive elements or prose |
| `--fs-sm` | `.75rem` | ~14.4 | Nav meta, table headers, chips, interactive controls |
| `--fs-base` | `.875rem` | ~16.8 | Buttons, inputs, tooltips, form labels, reading content in panels |
| `--fs-body` | `1rem` | ~19.2 | Primary reading / UI text |
| `--fs-lg` | `1.2rem` | ~23.0 | Sidebar titles, section h2 |
| `--fs-xl` | `1.65rem` | ~31.7 | Page headings, panel titles |
| `--fs-stat` | `2rem` | ~38.4 | Dashboard big numbers |

Scale ratio between adjacent steps: ~1.15–1.25× (approximates the major third / √φ band validated by Medium and Substack).

### Token assignment rules

`--fs-xs` is for purely decorative or non-interactive micro elements only: badges, pill chips, IDs, stat card labels, UPPERCASE section group labels with `letter-spacing`. **Never use `--fs-xs` for:**
- Interactive elements (buttons, links, clickable tags, controls)
- Content descriptions, history entries, source blocks
- Structural headers that organize readable content

`--fs-sm` covers secondary interactive elements and structural labels. `--fs-base` is the minimum for any element the user reads or acts on in a panel or sidebar.

### Line-height tokens

| Token | Value | Usage |
|---|---|---|
| `--lh-tight` | `1.2` | Headings, large display text |
| `--lh-snug` | `1.35` | Sub-headings, condensed UI labels, tooltips |
| `--lh-body` | `1.55` | Primary reading text, descriptions |
| `--lh-loose` | `1.65` | Captions, small text, sidebar rows, long-form prose |

Reference: Medium body lh 1.50, Substack body lh 1.60. `--lh-body: 1.55` splits the difference.

### SVG font sizes (pixel-based, bypass rem cascade)

| Token | Value | Usage |
|---|---|---|
| `--fs-svg-xs` | `9px` | Graph ★ star overlay |
| `--fs-svg-sm` | `10px` | Graph investor badge number |
| `--fs-svg-md` | `13px` | Graph node label |

SVG sizes are intentionally in `px` — D3 transforms scale the SVG viewport and rem would not behave correctly inside it.

---

## 2. Sidebar token system

### Em-cascade contract

`.sidebar { font-size: var(--scale-sidebar) }` sets `1.2rem` (~23px) as the em-cascade base for slide-in and inline panels. Child elements may use em fractions against that base:

| Em value | Resolves to | ~px | Usage |
|---|---|---|---|
| `.65em` | `0.78rem` | ~15px | ID chips, timestamps, block headers |
| `.8em` | `0.96rem` | ~18px | "Not available" placeholders |

**Do not use em fractions outside `.sidebar` context.** All other elements use `var(--fs-*)` tokens.

### Sidebar typography tokens (`--sl-*`)

All sidebar typography aliases the main scale. Change the main token, all sidebars follow.

| Token | Alias | ~px | Role |
|---|---|---|---|
| `--sl-title-fs` | `var(--fs-xl)` | ~31.7 | Panel title |
| `--sl-section-lbl-fs` | `var(--fs-base)` | ~16.8 | Section label (UPPERCASE, accent) |
| `--sl-row-lbl-fs` | `var(--fs-base)` | ~16.8 | Row key (UPPERCASE, dim) |
| `--sl-row-val-fs` | `var(--fs-body)` | ~19.2 | Row value |
| `--sl-desc-fs` | `var(--fs-body)` | ~19.2 | Description / prose text |

### Sidebar layout tokens

| Token | Value | Role |
|---|---|---|
| `--sl-w-sm` | `380px` | Narrow slide-in (participant sidebar) |
| `--sl-w-inline` | `450px` | Inline panels (matrix / graph / map) |
| `--sl-w-lg` | `800px` | Wide slide-in (entity detail sidebar) |
| `--sl-header-pad` | `.9rem 1.25rem` | Header padding |
| `--sl-body-pad` | `1.25rem` | Body padding |
| `--sl-panel-bg` | `#0d0d0d` | Slide-in background |
| `--sl-inline-bg` | `var(--surface3)` | Inline panel background |
| `--sl-header-bg` | `var(--surface2)` | Header strip |

### Panel positioning convention

All detail panels and slide-in sidebars are anchored to the **left** side of the content area. This applies to: Graph `#graph-detail`, SC Map `#map-panel`, EDF Map `#edfmap-panel`, Matrix `#mx-detail`, EU Calls participant sidebar `.ec-part-sidebar-panel`, entity slide-in `.entity-sidebar-panel`. Do not place new panels on the right.

### Sidebar primitive classes (`css/components.css`)

| Class | Role |
|---|---|
| `.sl-title` | Panel title — every sidebar header title element |
| `.sl-close` | Panel close button — every sidebar close button |
| `.sl-section-lbl` | Section label (UPPERCASE, accent color) |
| `.sl-row` / `.sl-row-lbl` / `.sl-row-val` | Key–value row (inline panels) |
| `.es-block` / `.es-row` / `.es-lbl` / `.es-val` | Key–value rows (slide-in entity sidebar) |
| `.es-desc` | Description text |
| `.es-list` / `.es-tag` | List and tag cloud |
| `.dp-inv-meta` / `.dp-co-meta` / `.dp-funding` / `.dp-desc` / `.dp-links` / `.dp-link` / `.dp-co-count` | Detail panel body content (matrix + graph) |
| `.ec-part-row` / `.ec-part-label` / `.ec-part-val` | EU Calls participant sidebar rows |
| `.ctrl-group-lbl` | Toolbar group label — xs, uppercase, bold, `--text-faint`. Use before a group of related controls (e.g. "View", "Sector"). |
| `.ov-stats-hint` | Small "(click to filter / explore)" hint label below section headings in Overview. |

---

## 3. CSS file scope

One file per concern. Do not add selectors outside a file's declared scope.

| File | Scope |
|---|---|
| `css/base.css` | `:root` design tokens + app shell — nav (`#topnav`, `#tabnav`, `#subnav`), layout (`#content`, `.tab-pane`), intro tab, known-issues tab, loading overlay, legend dots. Also the `[data-theme="light"]` block with all token overrides and per-shell light fixes. |
| `css/components.css` | Shared UI primitives: stat cards, tables, badges, legend, tooltip, sidebar structural shells, all `.sl-*`, `.es-*`, `.dp-*` classes. |
| `css/graph.css` | Graph tab only — `#graph-*` IDs and `.gv-*` classes. |
| `css/map.css` | Supply Chain Map and EDF Map — `#map-*`, `.map-*`, `#edfmap-*`, `.edfmap-*`. |
| `css/wikidata.css` | Wikidata Inspector — `#wd-*`, `.wd-*`, `.live-*`. |
| `css/eucalls.css` | EU Calls tab — `#ec-*`, `.ec-*`. |
| `css/edfbrowse.css` | EDF Browse and EDF Overview — `#eb-*`, `.eb-*`, `#eo-*`, `.eo-*`. |
| `css/about.css` | About tab — `#tab-about` scoped only. |
| `css/companysearch.css` | Company Search tab — `#tab-companysearch`, `#cs-*`, `.cs-*`. |

---

## 4. Rules

1. **No inline `style="…"` in HTML.** All visual properties go in CSS files.
2. **No inline styles in JS-generated HTML** except for data-driven values (dynamic width/color from runtime variables). Use CSS classes or `var(--token)` in inline styles when the value is truly dynamic.
3. **No hardcoded color/size literals** in CSS or JS — always `var(--token)`.
4. **`em` units are banned outside `.sidebar` context.** Use `rem` via `--fs-*` tokens so font sizes are independent of ancestry.
5. **The `.sidebar` class** (`font-size: var(--scale-sidebar)`) is reserved for panels that explicitly use em-based sub-classes per the cascade contract above. New panels must not use it unless they follow that contract.
6. **One canonical class per role** — no parallel equivalents. Removed: `.dp-close` (= `.sl-close`), `.dp-title` (= `.sl-title`), `.dp-label` (= `.sl-section-lbl`), `.entity-sidebar-title` (= `.sl-title`), `.ec-part-title` (= `.sl-title`).

---

## 5. Light mode — "Declassified Document" theme

Dark mode is the default. Light mode uses a warm paper palette with a dark military-green accent.

### Mechanism

- **Attribute**: `data-theme="light"` on `<html>`. Dark mode = attribute absent.
- **Persistence**: `localStorage['mitl-theme']`. Applied synchronously by an inline `<script>` in `<head>` before CSS renders (no flash).
- **Toggle**: `#theme-toggle` button in `#topnav`, wired by `js/theme.js`.

### Token overrides

All semantic tokens override inside `[data-theme="light"] { … }` in `css/base.css`. Every other CSS file only needs per-component overrides for values that cannot use tokens (hardcoded `rgba()` tints referencing the dark-mode accent `#00ff41`).

Key overrides:

| Token | Dark | Light | Notes |
|---|---|---|---|
| `--bg` | `#000000` | `#f8f7f4` | warm paper |
| `--accent` | `#00ff41` | `#006622` | neon → military green |
| `--on-accent` | `#000000` | `#ffffff` | |
| `--surface` / `--surface2` / `--surface3` | dark greys | warm off-whites | |
| `--text-faint` | `#757575` | `#6c6966` | WCAG AA on respective backgrounds |
| `--dim` | `rgba(255,255,255,0.53)` | `rgba(0,0,0,0.60)` | nav inactive buttons — passes AA |
| `--warn` | `#ffaa44` | `#8a5c00` | |
| `--warn-border` | `rgba(255,170,68,0.35)` | `rgba(122,68,0,0.35)` | |
| `--node-fill` | `#000000` | `#f8f7f4` | |
| `--map-bg` | `#000000` | `#d4d0ca` | |
| `--map-land` | `#1a1a1a` | `#bfbbb3` | |
| `--map-data` | `#0a2a0a` | `#8ab88a` | countries with data — higher contrast in light |
| `--map-selected` | `#003300` | `#4a7a4a` | |
| `--map-arc-color` | `#40e8f0` | `#0d6aaa` | read by SC Map JS at draw time via `getComputedStyle` |

### rgba() tint problem

Hardcoded `rgba(0,255,65,X)` accent tints (used in `.snav-btn.active`, `.intro-*`, etc.) do not update via token override. Each is handled by an explicit `[data-theme="light"]` component rule using the dark-green equivalent `rgba(0,102,34,X)`. When adding new accent tints, always add a paired light override.
