# Isometric grid view

## Context

The Polytopia map is isometric (rotated 45 degrees). Our tool uses a standard rectangular grid, making it hard to visually map between the game and the tool.

## Approach

Pure CSS transform: rotate the `#grid` element 45 degrees, counter-rotate tile contents so text stays upright. No changes to the data model, JS logic, or solver. The browser handles coordinate mapping for mouse events automatically.

## Changes

**`static/style.css` only:**

1. `#grid` — add `transform: rotate(45deg)` with margin for the larger diagonal bounding box
2. `.tile` — add `transform: rotate(-45deg)` so emojis and text stay upright
3. `#grid-container` — adjust padding/centering if needed for the rotated grid

## Files to modify

- `static/style.css`
