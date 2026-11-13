# Homepage theme template

The reusable palette and typography tokens for the homepage are in [`theme.css`](theme.css).

## Colours

| Role | Colour |
| --- | --- |
| Warm paper | `#fffaf8` |
| Surface | `#fffdfb` |
| Main text | `#26352e` |
| Muted text | `#68756e` |
| Sage card | `#edf2ec` |
| Sage artwork | `#496b58` |
| Blush card | `#f8e9ed` |
| Blush artwork | `#a9677d` |
| Dusty blue card | `#edf5f8` |
| Dusty blue artwork | `#365d71` |
| Fine borders | `#e9e1dd` |

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
