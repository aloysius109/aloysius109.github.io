# Homepage theme template

The reusable palette and typography tokens for the homepage are in [`theme.css`](theme.css). The page follows the operating system's light/dark preference; light mode is the fallback when no preference is set. The palette uses a cool pale-blue light background and sage, blush and dusty-blue report accents.

## Colours

| Role | Light | Dark |
| --- | --- | --- |
| Page background | `#f4f8fb` | `#11181c` |
| Surface | `#ffffff` | `#1a2529` |
| Main text | `#26352e` | `#e8eef0` |
| Muted text | `#68756e` | `#b5c3c2` |
| Sage card | `#edf2ec` | `#202d28` |
| Sage artwork | `#496b58` | `#365644` |
| Blush card | `#f8e9ed` | `#32232b` |
| Blush artwork | `#a65370` | `#744257` |
| Dusty blue card | `#edf5f8` | `#1d2c32` |
| Dusty blue artwork | `#365d71` | `#31586b` |
| Borders | `#dce6eb` | `#38474b` |

The homepage, CV and 404 page each define matching theme tokens and switch through `prefers-color-scheme`; they use no JavaScript toggle. The dark overrides are in place before content paints, and the CV's print stylesheet explicitly restores the light palette for PDF output.

## Typography

The theme uses **Manrope** with a system sans-serif fallback. For the same web font as the homepage, add this in the document `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

Then include `theme.css` after the font link:

```html
<link rel="stylesheet" href="theme.css">
```

The stylesheet also provides optional `.theme-card--sage`, `.theme-card--blush` and `.theme-card--blue` classes, with `.theme-card-art` for each card's artwork panel.
