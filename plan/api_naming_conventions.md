# pubfig API Naming Conventions

## Goal

Keep plotting APIs generic across scientific domains. Parameter names must describe **plot semantics**, not any one field's jargon.

## Canonical naming rules

### 1. `category_names`
Use for labels on a **categorical axis**.

Typical cases:
- bar chart category labels
- box / violin / strip group labels
- confusion-matrix shared class labels
- ridgeline category labels

Do **not** use it for legend entries or variable/dimension names.

### 2. `series_names`
Use for labels of **multiple plotted series** that usually appear in the legend.

Typical cases:
- grouped bar legend labels
- multiple lines / areas
- ROC / PR curves
- radar series
- repeated inner series in higher-dimensional grouped plots

Do **not** use it for axis tick labels.

### 3. `variable_names`
Use for labels of **variables / features / dimensions / columns**.

Typical cases:
- correlation matrix axes
- PCA loading arrow labels
- parallel coordinates dimension labels

Use this when the label names the measured variable itself rather than a category instance.

### 4. `pair_names`
Use for identifiers of **paired observations**.

Typical cases:
- paired before/after plots

This is distinct from `category_names`, because pairs are observation identities, not axis categories.

### 5. `group_names`
Use only when the plotted structure has an **outer grouping dimension** distinct from categories and series.

Typical cases:
- stacked bar: `(groups, rows, segments)`

This is acceptable because it refers to tensor structure, not domain-specific semantics.

### 6. Matrix-specific axis labels
Use explicit row/column variants when two matrix axes need different names:
- `row_category_names`
- `column_category_names`

Do not overload a single `names` parameter when row/column meaning is different.

### 7. Graph-specific node labels
Use:
- `node_names`

This is preferred over generic `names`, because graph nodes are a first-class plot concept.

## Removed legacy names

The following names are no longer accepted by the public plotting API:

- `names`
- `bar_names`
- `group_names` in places where it really meant category-axis labels
- `feature_names`
- `subject_names`
- `model_names`
- `row_names`
- `col_names`
- `node_labels`
- `subject_gap`
- `model_spacing_offset`

## Historical mapping reference

| Legacy name | Preferred name | Meaning |
|---|---|---|
| `names` | context-dependent | Old catch-all; replace with a semantic name |
| `bar_names` | `series_names` | grouped bar legend labels |
| `group_names` | `category_names` | grouped category labels in regular bar/bar_scatter |
| `feature_names` | `variable_names` | feature / variable labels |
| `subject_names` | `group_names` | outer tensor group labels |
| `model_names` | `series_names` | repeated inner series labels |
| `row_names` | `row_category_names` | matrix row labels |
| `col_names` | `column_category_names` | matrix column labels |
| `node_labels` | `node_names` | Sankey / graph node labels |
| `subject_gap` | `group_gap` | spacing between outer groups |
| `model_spacing_offset` | `series_spacing_offset` | spacing control for repeated series |

## Design rules for future APIs

1. Never introduce a new bare `names` parameter.
2. Never use domain-specific words like `subject`, `trial`, `gene`, `neuron`, `patient` in generic plotting APIs unless the plot is domain-specific by design.
3. Prefer **semantic precision** over brevity.
4. If one parameter names axis ticks and another names legend entries, they must not share the same name.
5. Do not reintroduce removed aliases for convenience.

## Examples

### Good

```python
bar(data, category_names=["A", "B"], series_names=["Ctrl", "Treatment"])
line(data, series_names=["Method 1", "Method 2"])
corr_matrix(data, variable_names=["Gene1", "Gene2", "Gene3"])
parallel_coordinates(data, variable_names=["Speed", "Accuracy", "Latency"])
clustermap(data, row_category_names=row_labels, column_category_names=col_labels)
sankey(source, target, value, node_names=["Input", "Process", "Output"])
```

### Removed / invalid

```python
bar(data, names=[...])
roc(fpr, tpr, names=[...])
parallel_coordinates(data, names=[...])
clustermap(data, row_names=[...], col_names=[...])
```

## Deprecation policy

- Old naming aliases have been removed from the public API.
- New code, docs, examples, and tests must use only canonical names.
- If future naming migration is needed, use a short deprecation window and then remove the alias fully.
