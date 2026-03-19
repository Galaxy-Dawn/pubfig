# Nature Portfolio Figure Style Guide (pubfig)

Date: 2026-03-09  
Target journals: Nature / Nature Portfolio (incl. many sub-journals and npj series)

This is a practical, implementation-oriented guide to match a "Nature-like" house style in `pubfig`.
Different journals/sections may add extra constraints, but the rules below are broadly safe.

References (official):
- Nature Research figure guide: https://research-figure-guide.nature.com/
- Preparing figures / specifications: https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/
- Building and exporting figure panels: https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/
- Nature final submission: https://www.nature.com/nature/for-authors/final-submission

---

## 0. One-line principle
Design **at final print size**, keep everything **readable and editable**, avoid decoration, and ensure **accessibility** (color-blind safe, good contrast).

---

## 1. Sizing (drives font/linewidth)
Common (approx.) column widths used in production:
- Single column: **89 mm**
- Double column: **183 mm**
- Often-used "1.5 column": **~120–136 mm** (when needed)

Heuristic:
- Start designing in the smallest target size you will publish at (often single-column).
- Check legibility at that final size (especially tick labels, legend, and annotations).

---

## 2. Typography
### Fonts
- Prefer standard sans-serif: **Arial / Helvetica**.
- Use **one font family** consistently across all figures.
- Keep text as **text** in vector outputs (do not outline/flatten).

### Font sizes (final size)
- Typical figure text: **5–7 pt** (avoid smaller than 5 pt).
- Panel labels (a, b, c...): **8 pt, bold, upright**.

Notes:
- Avoid colored text; use color keys (patch/line/marker) with black labels.
- Avoid excessive text inside the plot; move details to caption when possible.

---

## 3. Line widths and strokes
At final size:
- Axis/tick/spine strokes: **~0.6–0.9 pt** (avoid very thick axes).
- Data lines: **~1.0–1.3 pt** depending on complexity.
- Reference/baseline lines: thin and light (often grey dashed).
- Error bars: black; stroke similar to axes.

Avoid:
- Shadows, 3D effects, heavy borders, gradients.

---

## 4. Axes, ticks, grids
- Keep axes and ticks present (do not remove them unless a heatmap/diagram requires it).
- Default spines: **left + bottom only** (hide top/right for standard 2D plots).
- Tick direction: **out**.
- Avoid background grid lines in most cases.

---

## 5. Color and accessibility
- Use **color-blind safe** palettes.
- Avoid red/green reliance; avoid rainbow colormaps.
- Ensure contrast; keep backgrounds white.
- Prefer a small number of hues; use alpha instead of many distinct colors when data are dense.

---

## 6. Export formats
Preferred:
- Vector (editable): **PDF / SVG / EPS / AI** (depending on journal instructions).

Raster:
- Photographic images: usually **>=300 dpi** (check journal page).
- Line art / text-heavy graphics should remain vector whenever possible.

---

# 7. Plot-type summaries (one paragraph each)

## 7.1 Bar / Grouped Bar / Bar+Scatter
Keep bars simple (flat fill, minimal border). Error bars should be black and thin. Prefer showing raw points (jitter + alpha) over only mean bars. Avoid 3D bars, gradients, shadows. Statistics brackets should be minimal; avoid over-annotating inside the plot.

## 7.2 Line / Time Series / Multi-line + CI band
Use clean lines with moderate thickness and small markers only at sampling points. Confidence intervals should be shown as light alpha bands. Put legends above or outside data to avoid occlusion. Avoid heavy grids and large markers.

## 7.3 Scatter / Bubble / Paired (connected dots)
Manage overplotting with alpha and small marker sizes. A subtle white edge can help point contrast. Paired plots should use light grey connecting lines so points remain dominant. Regression/reference lines should be thin and unobtrusive.

## 7.4 Box / Violin / Strip / Histogram / Density / Ridgeline
Distribution plots should avoid heavy outlines. Box/violin edges are thin; fills are light (alpha). Prefer overlaying raw points (strip) when appropriate. Histogram borders should not be thick; KDE lines should be moderate.

## 7.5 Heatmap / Corr matrix / Clustermap
Avoid rainbow. Use perceptually uniform colormaps (e.g., viridis) for continuous scales; use diverging colormaps centered at 0 (e.g., RdBu_r) for correlations. Colorbars must be clearly labeled. If annotated, text color should auto-contrast with cell intensity.

## 7.6 ROC / PR curve
Axes typically span 0–1. Use a light grey dashed baseline. Curves should be clear but not too thick. Put AUC/AP in legend without blocking the curve.

## 7.7 Radar
Radar is not a typical Nature-first choice; if used, keep grid light and sparse, reduce dimensions, and keep legend unobtrusive. Prefer alternative plots when possible.

## 7.8 Sankey / Parallel coordinates
These are non-traditional for many Nature articles; focus on clarity: fewer nodes/links, minimal color usage, black labels, no decoration. Consider splitting into panels when dense.

## 7.9 3D plots (surface/3D scatter/3D dimreduce)
3D is often discouraged due to occlusion and print readability. If used, fix a clear view, include colorbar, and consider adding 2D projections/slices as additional panels.

---

# 8. pubfig mapping (defaults)
In `pubfig` we implement the Nature-like style via:
- `Theme(name="nature")`: fonts, spines, tick sizes, linewidths.
- Shared helpers in `src/pubfig/_style.py`: legend placement + linewidth/marker defaults.
- Export sizing in `save_publication_figure`: single/double column widths and consistent trim/layout.

