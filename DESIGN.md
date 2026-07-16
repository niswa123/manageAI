# DESIGN.md - МенеджAI

## Typography
- Main font: Geist or system-ui sans-serif
- Editorial emphasis: crisp weight variations, tightly tracked headings (`tracking-tight`)

## Spacing & Spacial Rhythm
- Generous padding scales (e.g. py-24, py-32, py-48, py-64)
- Section gaps: minimal but spacious (gap-12, gap-16)

## Color System
- Theme: Sophisticated Deep Charcoal & Warm Bronze
- Neutrals:
  - Charcoal background: `oklch(0.14 0.008 65)` (deep warm grey)
  - Surface containers: `oklch(0.17 0.008 65)`
  - Active/border details: `oklch(0.24 0.01 65)`
  - Text Primary: `oklch(0.96 0.006 65)` (cream white)
  - Text Secondary: `oklch(0.72 0.01 65)` (warm sand grey)
- Accents:
  - Elegant Bronze: `oklch(0.76 0.08 75)`
  - Accent Red (warning/errors): `oklch(0.65 0.14 20)`
  - Accent Emerald (success/metrics): `oklch(0.78 0.12 140)`

## Design Tokens & Visual Rules
- Avoid standard neon glow shapes and backlights.
- Use sharp/clean corners and razor-thin borders (`border border-neutral-800`).
- No side-stripe borders or gradient texts.
