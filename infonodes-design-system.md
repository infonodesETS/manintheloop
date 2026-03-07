# info.nodes — Design System

## Brand Identity

**info.nodes** è un'organizzazione italiana no-profit fondata nel 2019 che unisce giornalismo investigativo e attivismo civico. Il brand comunica urgenza, trasparenza e impegno sociale attraverso un'estetica scura e minimale con accenti vibranti.

---

## Colori

| Token | Valore | Uso |
|-------|--------|-----|
| `--color-bg-primary` | `#000000` | Sfondo header, footer, sezioni principali |
| `--color-bg-page` | `#FFFFFF` | Sfondo contenuti / body |
| `--color-bg-surface` | `rgba(0,0,0,1)` | Card, righe alternate |
| `--color-text-primary` | `#000000` | Titoli, testo forte |
| `--color-text-body` | `rgba(102,102,102,1)` | Testo corpo |
| `--color-text-inverse` | `#FFFFFF` | Testo su sfondo scuro |
| `--color-accent` | `#68CCD1` | Accent legacy (teal) |
| `--color-accent-green` | dal logo verde | Accent principale corrente |
| `--color-border` | `rgb(65,67,69)` | Bordi bottoni |
| `--color-btn-hover` | `rgb(65,67,69)` | Sfondo bottone al hover |

La palette è essenzialmente **bianco e nero** con il verde del logo come unico accento cromatico. L'effetto è editoriale e diretto.

---

## Tipografia

| Ruolo | Font | Peso | Dimensione |
|-------|------|------|------------|
| Titoli (H1/H2) | **Barlow Condensed** | 700 | 96px desktop / 50px mobile |
| Sottotitoli (H4) | **Barlow Condensed** | 700 | 22px |
| Corpo | **Barlow Condensed** | 400 | 18px desktop / 14px mobile |
| Fallback corpo | **Rubik** | 300 | 16px |
| Font di sistema | Rubik, Source Sans Pro | — | — |

La scelta di **Barlow Condensed** come font dominante conferisce un tono giornalistico, compatto e moderno. I titoli sono molto grandi (96px) per massimo impatto.

---

## Bottoni

| Proprietà | Valore |
|-----------|--------|
| Border radius | `50px` (pill) |
| Border width | `1px` |
| Border color | `rgb(65,67,69)` |
| Background | `transparent` |
| Text color | `rgb(65,67,69)` |
| Font | Barlow Condensed, 700 |
| Font size | `15px` (tutte le viewport) |
| Hover bg | `rgb(65,67,69)` |
| Hover text | `#FFFFFF` |
| Padding | `10px 0` |

Stile **ghost/outline** con transizione a pieno al hover. Forma pill per morbidezza.

---

## Layout

| Parametro | Valore |
|-----------|--------|
| Max width contenuti | `960px` |
| Padding riga | `40px` laterale |
| Griglia | 12 colonne flex |
| Gap colonne | `1.5%` |
| Padding riga verticale | `15px` top/bottom |

Il layout è centrato con larghezza massima 960px. Le sezioni full-bleed rompono questo vincolo per gli sfondi. La griglia usa un sistema a 12 colonne con distribuzione flex.

---

## Componenti Chiave

### Header
- Sfondo nero pieno, sticky
- Logo centrato (max 126px larghezza)
- Altezza spacer: 124px desktop

### Sezione Hero
- Sfondo con gradiente grigio (`grey_gradient.jpg`) + attachment fixed
- Immagine banner a piena larghezza
- CTA centrata sotto il banner

### Griglia Navigazione (4 colonne)
- 4 immagini-bottone circolari con hover grayscale
- Link a sezioni: MARLA, Attivismo, Formazione, Inchieste

### Sezione "Chi Siamo"
- Titolo H2 grande centrato
- Testo giustificato corpo
- Lista membri con icone SVG lightning bolt + nome + ruolo

### Footer
- Sfondo nero
- 4 colonne: social, donazione PayPal, contatti, documenti
- Icone social: email + Instagram

---

## Iconografia

- **Logo**: forma circolare con pattern a raggi/nodi (SVG inline, verde su nero)
- **Icone membri**: fulmine stilizzato (SVG custom, ripetuto per ogni membro)
- **Icone social**: set custom `dm-social-icons`

---

## Effetti e Interazioni

| Effetto | Dove |
|---------|------|
| Hover grayscale | Immagini-bottone navigazione |
| Background fixed | Hero section (parallax) |
| Sticky header | Header con classe `hasStickyHeader` |
| Animazioni entrata | Elementi con `data-anim-desktop` (hidden fino a trigger) |

---

## Tono Visivo

Il design system di info.nodes trasmette: **serietà editoriale**, **urgenza giornalistica**, **trasparenza**. Il nero dominante con testo bianco e accenti verdi crea un'identità forte e riconoscibile, coerente con la missione di inchiesta e attivismo.
