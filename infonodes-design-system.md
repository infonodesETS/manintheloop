# info.nodes — Design System

## Brand Identity

**info.nodes** is an Italian non-profit organization founded in 2019, combining investigative journalism and civic activism. The brand communicates urgency, transparency and social commitment through a dark, minimal aesthetic with vibrant accents.

---

## Colors

| Token | Value | Use |
|-------|-------|-----|
| `--color-bg-primary` | `#000000` | Header, footer, main section backgrounds |
| `--color-bg-page` | `#FFFFFF` | Content / body background |
| `--color-bg-surface` | `rgba(0,0,0,1)` | Cards, alternating rows |
| `--color-text-primary` | `#000000` | Headings, strong text |
| `--color-text-body` | `rgba(102,102,102,1)` | Body text |
| `--color-text-inverse` | `#FFFFFF` | Text on dark backgrounds |
| `--color-accent` | `#00ff41` | Legacy accent (teal) |
| `--color-accent-green` | from logo green | Current primary accent |
| `--color-border` | `rgb(65,67,69)` | Button borders |
| `--color-btn-hover` | `rgb(65,67,69)` | Button background on hover |

The palette is essentially **black and white** with the logo green as the only chromatic accent. The effect is editorial and direct.

---

## Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| Headings (H1/H2) | **Barlow Condensed** | 700 | 96px desktop / 50px mobile |
| Subheadings (H4) | **Barlow Condensed** | 700 | 22px |
| Body | **Barlow Condensed** | 400 | 18px desktop / 14px mobile |
| Body fallback | **Rubik** | 300 | 16px |
| System font | Rubik, Source Sans Pro | — | — |

The choice of **Barlow Condensed** as the dominant font gives a journalistic, compact and modern tone. Headings are very large (96px) for maximum impact.

---

## Buttons

| Property | Value |
|----------|-------|
| Border radius | `50px` (pill) |
| Border width | `1px` |
| Border color | `rgb(65,67,69)` |
| Background | `transparent` |
| Text color | `rgb(65,67,69)` |
| Font | Barlow Condensed, 700 |
| Font size | `15px` (all viewports) |
| Hover bg | `rgb(65,67,69)` |
| Hover text | `#FFFFFF` |
| Padding | `10px 0` |

**Ghost/outline** style with full-fill transition on hover. Pill shape for softness.

---

## Layout

| Parameter | Value |
|-----------|-------|
| Max content width | `960px` |
| Row padding | `40px` horizontal |
| Grid | 12-column flex |
| Column gap | `1.5%` |
| Row vertical padding | `15px` top/bottom |

The layout is centered with a 960px max-width. Full-bleed sections break this constraint for backgrounds. The grid uses a 12-column flex system.

---

## Key Components

### Header
- Solid black background, sticky
- Centered logo (max 126px width)
- Spacer height: 124px desktop

### Hero Section
- Background with grey gradient (`grey_gradient.jpg`) + fixed attachment
- Full-width banner image
- Centered CTA below the banner

### Navigation Grid (4 columns)
- 4 circular image-buttons with grayscale hover
- Links to sections: MARLA, Activism, Training, Investigations

### "Who We Are" Section
- Large centered H2 heading
- Justified body text
- Member list with SVG lightning bolt icons + name + role

### Footer
- Black background
- 4 columns: social, PayPal donation, contacts, documents
- Social icons: email + Instagram

---

## Iconography

- **Logo**: circular shape with ray/node pattern (inline SVG, green on black)
- **Member icons**: stylized lightning bolt (custom SVG, repeated for each member)
- **Social icons**: custom `dm-social-icons` set

---

## Effects and Interactions

| Effect | Where |
|--------|-------|
| Hover grayscale | Navigation image-buttons |
| Fixed background | Hero section (parallax) |
| Sticky header | Header with `hasStickyHeader` class |
| Entry animations | Elements with `data-anim-desktop` (hidden until triggered) |

---

## Visual Tone

The info.nodes design system communicates: **editorial seriousness**, **journalistic urgency**, **transparency**. The dominant black with white text and green accents creates a strong, recognisable identity consistent with the investigative and activist mission.
