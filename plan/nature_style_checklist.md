# Nature-like Figure Checklist (pubfig)

Use this as a quick "pre-submission" checklist after exporting with `save_publication_figure`.

## A. Global
- [ ] Figure uses a standard sans-serif font (Arial/Helvetica) and is consistent across all panels.
- [ ] At final size, all text is readable (no smaller than ~5 pt).
- [ ] Panel labels are upright, bold, and consistent (e.g., a, b, c...).
- [ ] No shadows, 3D effects, gradients, or decorative elements.
- [ ] No colored text (labels/annotations are black; color is encoded by marks/legend keys).

## B. Axes and strokes
- [ ] Standard 2D plots show only left/bottom spines (top/right hidden).
- [ ] Tick direction is outward; tick length/width look light (not heavy).
- [ ] No (or minimal) background grid lines.
- [ ] Line widths look appropriate at final size:
  - axes/ticks/spines ~0.6–0.9 pt
  - data lines ~1.0–1.3 pt
  - reference/baseline lines are lighter (often grey dashed)

## C. Legends and labels
- [ ] Legend does not cover data; prefer above the axes or in unused whitespace.
- [ ] Legend has no frame; spacing is compact.
- [ ] Axis labels include units where relevant; labels are short (avoid long sentences).

## D. Colors and accessibility
- [ ] Palette is color-blind safe.
- [ ] No rainbow colormap.
- [ ] Heatmap/corr matrix uses a sensible colormap (uniform/diverging centered at 0).
- [ ] Text contrast is sufficient; background is white.

## E. Data integrity visualization
- [ ] Bar plots show raw data points (jitter + alpha) when appropriate.
- [ ] Error bars clearly indicate what they are (SD/SEM/CI), and the choice is explained in caption.
- [ ] Confidence intervals are shown as light alpha bands (for time series).
- [ ] Statistical annotations are minimal; avoid crowding the figure.

## F. Export / production readiness
- [ ] Vector outputs (PDF/SVG) keep text editable/selectable (not outlined).
- [ ] Fonts are embedded (or otherwise acceptable per journal).
- [ ] Raster outputs meet resolution requirements (e.g., >=300 dpi for photos; higher for line art if rasterized).
- [ ] No cropping issues: labels and colorbars are not clipped.

