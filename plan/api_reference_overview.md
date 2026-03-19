# pubfig API Reference Overview

## Shared conventions

### Common plotting parameters
Most public plotting functions follow the same shared parameter vocabulary:

- `title`: figure title
- `color_palette`: palette used for series / categories
- `theme`: pubfig theme object or theme name resolved upstream
- `width`: figure width in pixels
- `height`: figure height in pixels
- `ax`: optional Matplotlib axes to draw into

### Naming conventions

- `category_names`: labels on a categorical axis
- `series_names`: labels for legend entries / multiple plotted series
- `variable_names`: labels for variables / features / dimensions
- `pair_names`: labels for paired observations
- `group_names`: labels for an outer tensor grouping dimension
- `row_category_names` / `column_category_names`: row/column labels for matrix-like plots
- `node_names`: labels for graph nodes

## Plot families

### Bar family
- `bar(data, category_names=..., series_names=...)`
- `bar_scatter(data, category_names=..., series_names=...)`
- `stacked_bar(data, group_names=...)`

### Distribution family
- `box(data, category_names=...)`
- `violin(data, category_names=...)`
- `strip(data, category_names=...)`
- `ridgeline(data, category_names=...)`
- `density(data, ...)`
- `histogram(data, ...)`

### Line family
- `line(data, series_names=...)`
- `area(data, series_names=...)`

### Evaluation family
- `roc(fpr, tpr, series_names=...)`
- `pr_curve(precision, recall, series_names=...)`

### Matrix / structure family
- `heatmap(data, category_names=...)`
- `corr_matrix(data, variable_names=...)`
- `clustermap(data, row_category_names=..., column_category_names=...)`
- `parallel_coordinates(data, variable_names=...)`
- `sankey(source, target, value, node_names=...)`

### Geometry / reduction family
- `scatter(x, y, labels=...)`
- `bubble(x, y, size, labels=...)`
- `paired(before, after, pair_names=...)`
- `radar(data, categories=..., series_names=...)`
- `dimreduce(data, labels=...)`
- `pca_biplot(data, variable_names=...)`
- `surface(x, y, z, ...)`
- `scatter3d(x, y, z, color, ...)`

## Removal policy

Old generic names such as `names`, `bar_names`, `feature_names`, `subject_names`, `model_names`, `row_names`, `col_names`, and `node_labels` are removed from the public API and should not appear in examples, docs, or tests.
