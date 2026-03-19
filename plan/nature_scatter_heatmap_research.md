# Nature 风格调研：Scatter / Heatmap

更新时间：2026-03-17

## 1. 官方约束（直接来自 Nature / Nature Portfolio）

- 字体与图内文字：Nature figure guide 要求图中文字最终印刷尺寸下仍清晰可读，常用 Arial / Helvetica，字号通常需要在最终版面下保持可读。
- 颜色与可访问性：Nature formatting guide 明确要求颜色选择应考虑色觉缺陷读者，避免只靠颜色区分类别，尤其避免问题性的 red/green 组合。
- 图例与标注：官方建议 key / legend 尽量放在图外或不遮挡数据区域；不要用彩色文字直接代替图例。
- 图像类型：热图、显微图、照片类属于 continuous-tone image；投稿时需要保持足够分辨率，避免后期过度处理。

## 2. Scatter 的 Nature-like baseline

这部分不是官方硬性模板，而是结合官方规则与 Nature / Nature Methods 常见主图风格得到的实现结论：

- 点应 **小、实心、克制**，不要大面积空心 marker。
- 多组散点不要只靠颜色区分；更稳妥的是 **颜色 + marker shape** 一起编码。
- 点的描边应很细，只起分离作用，不应形成粗黑轮廓。
- 回归线、y=x 参考线应比主数据更轻、更细，避免压过点层。
- 统计文字与拟合指标通常用小号字放在角落，不与数据层竞争。

落到 `pubfig` 默认值上的实现建议：

- 单组 scatter 默认使用 filled circle。
- 多组 scatter 默认 marker cycle：`o / s / D / ^ / v`。
- 默认点径减小，alpha 下降，描边变细。
- legend 继续放 title 下方，不进 plotting area。

## 3. Heatmap 的 Nature-like baseline

同样，这部分是风格推断，不是官方逐条硬规定：

- 通用 heatmap 优先使用 **顺序型、感知单调的 colormap**；不要用 rainbow。
- 只有在数据天然围绕 0 或某个中点对称时，才优先用 diverging map。
- colorbar 应简洁、外置、细边框，不要粗黑框。
- 小矩阵可以 annotate；大矩阵不应塞满数字。
- 坐标轴与色条文字要和整库 theme 一致，spines 通常隐藏。

落到 `pubfig` 默认值上的实现建议：

- 通用 `heatmap()` 默认改为更保守的 sequential map。
- `corr_matrix()` 继续使用 diverging map，因为相关系数有自然中心 0。
- annotation 默认比 tick 再小一点。
- colorbar outline / tick / label 全部减轻。

## 4. 本轮代码改造目标

### Scatter
- 默认 marker 不再显得“海报风”或“演示风”
- 分组时自动启用 marker cycle
- 回归线 / 参考线减细

### Heatmap
- 默认色图从强调炫彩，改成投稿更稳妥的 sequential baseline
- colorbar 减重
- 示例数据从纯随机噪声改成更像论文里的结构化矩阵

## 5. 参考来源

- Nature figure guide: <https://research-figure-guide.nature.com/>
- Nature formatting guide: <https://www.nature.com/nature/for-authors/formatting-guide>
- Nature Methods colour blindness column: <https://www.nature.com/articles/nmeth.1618>
