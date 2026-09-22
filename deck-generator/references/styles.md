# Deck Style Presets

Use one preset for the entire deck unless the user explicitly requests a style change. Preserve the same palette, typography, illustration language, spacing, and visual density on every slide.

## Presets

### `whiteboard`

- Clean white background
- Black hand-drawn ink
- Orange highlights
- Bold hand-lettered headers
- Simple figures, arrows, and icons
- No photos, gradients, or 3D effects

Prompt prefix:

> Hand-drawn whiteboard illustration style presentation slide. Black ink sketch on clean white background. Orange accent color for highlights. Bold hand-lettered headers. Simple stick figures and icons. No photos, no gradients, no 3D effects. Minimalist sketch aesthetic like a whiteboard drawing.

### `corporate`

- Navy and white palette
- Gold accents
- Modern sans-serif typography
- Flat icons and restrained geometric patterns
- Clear, professional data visualization
- No clip art

Prompt prefix:

> Clean professional corporate presentation slide. Navy blue and white color scheme with gold accents. Modern sans-serif typography. Flat design icons. Subtle geometric patterns in background. Professional data visualization style. No clip art.

### `minimalist`

- Pure white background
- Electric-blue accent
- Large bold sans-serif type
- Maximum negative space
- One idea per slide
- No decorative elements

Prompt prefix:

> Ultra-minimalist presentation slide. Pure white background. Single accent color (electric blue). Large bold sans-serif text. Maximum negative space. One idea per slide. No decorative elements. Apple Keynote aesthetic.

### `dark-tech`

- Near-black background (`#0a0a0a`)
- Neon-green accent (`#00ff88`)
- Monospace headers
- Subtle grid
- Terminal/code visual language
- High contrast and readable body text

Prompt prefix:

> Dark-themed tech presentation slide. Near-black background (#0a0a0a). Neon green (#00ff88) accent color. Monospace font for headers. Terminal/code aesthetic. Subtle grid lines. Futuristic but readable.

### `playful`

- Bright pastel palette
- Rounded shapes and soft edges
- Friendly sans-serif typography
- Hand-drawn doodle accents
- Energetic, modern startup feel
- Playful without looking childish

Prompt prefix:

> Colorful playful presentation slide. Bright pastel color palette. Rounded shapes and soft edges. Fun hand-drawn doodle elements. Friendly sans-serif font. Energetic but not childish. Modern startup aesthetic.

### `editorial`

- Black and white base
- One red spot color
- Strong typographic hierarchy
- Thin serif headers with clean sans-serif body
- Pull-quote and magazine layouts
- High contrast

Prompt prefix:

> Editorial magazine-style presentation slide. Black and white with one spot color (red). Strong typographic hierarchy. Pull-quote style layouts. Thin serif headers, clean sans-serif body. High contrast. Vogue/Economist aesthetic.

## Selection

- Use `whiteboard` for explanations, workshops, and process storytelling.
- Use `corporate` for executive, sales, and client-facing decks.
- Use `minimalist` for product narratives and keynote-style presentations.
- Use `dark-tech` for AI, developer, infrastructure, and security topics.
- Use `playful` for creator, community, consumer, and culture topics.
- Use `editorial` for thought leadership, research, and strong narrative arguments.

Default to `whiteboard` when the user gives no visual direction.

## Custom styles

When the user supplies brand guidance or a custom direction, pass a custom prompt prefix in place of a preset. Include:

- background and accent colors;
- typography category and hierarchy;
- imagery or illustration language;
- layout density and spacing;
- chart and icon style;
- explicit exclusions;
- a consistency instruction that applies to every slide.

Do not mix presets casually. A custom style should remain stable across all generated slide prompts.
