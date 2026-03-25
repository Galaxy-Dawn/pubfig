const FIGURE_KEY = "pubfigFigureId";
const PANEL_KEY = "pubfigPanelId";
const PANEL_ROW_KEY = "pubfigPanelRow";
const PANEL_COLUMN_KEY = "pubfigPanelColumn";
const ROLE_KEY = "pubfigRole";
const SOURCE_KEY = "pubfigSourcePath";
const VERSION_KEY = "pubfigVersion";
const LAYOUT_PRESET_KEY = "pubfigLayoutPreset";
const PANEL_GAP_KEY = "pubfigPanelGap";
const PLUGIN_VERSION = "0.4.8";
const PANEL_BUNDLE_TYPE = "pubfig_figma_bundle";

const PANEL_PADDING = 2;
const LABEL_HEIGHT = 0;
const LABEL_OUTSET_X = 12;
const LABEL_OUTSET_Y = 12;
const DEFAULT_GAP = 12;
const DEFAULT_COLUMNS = 2;
const DEFAULT_PANEL_WIDTH = 320;
const DEFAULT_PANEL_HEIGHT = 220;
const DEFAULT_TITLE_HEIGHT = 56;
const DEFAULT_LEGEND_WIDTH = 220;
const DEFAULT_LEGEND_HEIGHT = 120;
const TEXT_INSET = 14;

const ROOT_BACKGROUND = { r: 1, g: 1, b: 1 };
const PANEL_BACKGROUND = { r: 1, g: 1, b: 1 };
const PLACEHOLDER_FILL = { r: 0.96, g: 0.97, b: 0.99 };
const PLACEHOLDER_STROKE = { r: 0.82, g: 0.86, b: 0.92 };
const TEXT_COLOR = { r: 0.09, g: 0.13, b: 0.18 };

const VALID_PRESETS = new Set(["auto", "grid", "row", "column", "two_by_two", "hero_left", "hero_top"]);
const VALID_LABEL_ALIGN_X = new Set(["panel", "column"]);
const VALID_LABEL_ALIGN_Y = new Set(["panel", "row"]);

figma.showUI(__html__, { width: 480, height: 940 });

async function ensureBoldFont() {
  try {
    await figma.loadFontAsync({ family: "Inter", style: "Bold" });
    return true;
  } catch (error) {
    console.warn("Failed to load Inter Bold:", error);
    return false;
  }
}

function clampPositive(value, fallback) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric) || numeric <= 0) {
    return fallback;
  }
  return numeric;
}

function withDefault(value, fallback) {
  return value === null || value === undefined ? fallback : value;
}

function getLayout(bundle) {
  const layout = bundle.layout || {};
  const preset = VALID_PRESETS.has(layout.preset) ? layout.preset : "auto";
  const rowPanelCounts = normalizeRowPanelCounts(layout.row_panel_counts, Array.isArray(bundle.panels) ? bundle.panels.length : 0);
  const rawColumns = Number(layout.columns);
  const columns = Number.isFinite(rawColumns) && rawColumns > 0 ? Math.max(1, Math.round(rawColumns)) : null;
  return {
    preset,
    columns,
    rowPanelCounts,
    panelGap: Math.max(0, Number(withDefault(layout.panel_gap, DEFAULT_GAP))),
    preservePositionsOnRefresh: Boolean(withDefault(layout.preserve_positions_on_refresh, true)),
  };
}

function getPanelLabelSettings(bundle) {
  const panelLabels = bundle.panel_labels || {};
  const alignX = VALID_LABEL_ALIGN_X.has(panelLabels.align_x) ? panelLabels.align_x : "column";
  const alignY = VALID_LABEL_ALIGN_Y.has(panelLabels.align_y) ? panelLabels.align_y : "row";
  const rawOffsetX = Number(withDefault(panelLabels.offset_x, 12));
  const rawOffsetY = Number(withDefault(panelLabels.offset_y, 12));
  return {
    enabled: panelLabels.enabled !== false,
    offsetX: Number.isFinite(rawOffsetX) && rawOffsetX >= 0 ? rawOffsetX : 12,
    offsetY: Number.isFinite(rawOffsetY) && rawOffsetY >= 0 ? rawOffsetY : 12,
    alignX,
    alignY,
  };
}

function isPanelBundle(bundle) {
  return bundle && bundle.bundle_type === PANEL_BUNDLE_TYPE;
}

function normalizeRowPanelCounts(values, panelCount) {
  if (!Array.isArray(values) || !values.length) {
    return null;
  }
  const normalized = [];
  let total = 0;
  for (const value of values) {
    const numeric = Math.round(Number(value));
    if (!Number.isFinite(numeric) || numeric <= 0) {
      return null;
    }
    normalized.push(numeric);
    total += numeric;
  }
  if (panelCount > 0 && total !== panelCount) {
    return null;
  }
  return normalized;
}

function chooseAutoGridColumns(panelCount) {
  if (!Number.isFinite(panelCount) || panelCount <= 1) {
    return 1;
  }
  return Math.max(1, Math.ceil(Math.sqrt(panelCount)));
}

function resolvePreset(layout, panelCount) {
  if (layout.rowPanelCounts && layout.rowPanelCounts.length) {
    return "grid";
  }
  if (layout.preset !== "auto") {
    return layout.preset;
  }
  return "grid";
}

function getPlaceholders(bundle) {
  const placeholders = bundle.placeholders || {};
  const title = placeholders.shared_title || {};
  const legend = placeholders.shared_legend || {};
  return {
    sharedTitle: {
      enabled: Boolean(title.enabled),
      text: String(title.text || bundle.title || "Shared Figure Title"),
    },
    sharedLegend: {
      enabled: Boolean(legend.enabled),
      text: String(legend.text || "Shared Legend"),
      position: String(legend.position || "right") === "bottom" ? "bottom" : "right",
    },
  };
}

function getPanelTitle(panel) {
  const title = String(panel.title || "").trim();
  return title;
}

function getPanelLabelText(panel, labelSettings) {
  const label = String(panel.label || panel.panel_id).trim();
  return label;
}

function getRoleNode(root, role) {
  return root.findOne((node) => typeof node.getPluginData === "function" && node.getPluginData(ROLE_KEY) === role);
}

function removeRoleNode(root, role) {
  const node = getRoleNode(root, role);
  if (node) {
    node.remove();
  }
}

function getNodeWidth(node, fallback) {
  return clampPositive(node && node.width, fallback);
}

function getNodeHeight(node, fallback) {
  return clampPositive(node && node.height, fallback);
}

function getPanelSlotWidth(frame, labelSettings) {
  return getNodeWidth(frame, DEFAULT_PANEL_WIDTH) + (labelSettings && labelSettings.enabled ? labelSettings.offsetX : 0);
}

function getPanelSlotHeight(frame, labelSettings) {
  return getNodeHeight(frame, DEFAULT_PANEL_HEIGHT) + (labelSettings && labelSettings.enabled ? labelSettings.offsetY : 0);
}

function placePanelFrameAtSlot(frame, slotX, slotY, rowIndex, columnIndex, labelSettings) {
  const insetX = labelSettings && labelSettings.enabled ? labelSettings.offsetX : 0;
  const insetY = labelSettings && labelSettings.enabled ? labelSettings.offsetY : 0;
  frame.x = slotX + insetX;
  frame.y = slotY + insetY;
  frame.setPluginData(PANEL_ROW_KEY, String(rowIndex));
  frame.setPluginData(PANEL_COLUMN_KEY, String(columnIndex));
}

function findFigureRootFromSelection(figureId) {
  for (const selected of figma.currentPage.selection) {
    let current = selected;
    while (current) {
      if (
        current.type === "FRAME" &&
        typeof current.getPluginData === "function" &&
        current.getPluginData(FIGURE_KEY) === figureId
      ) {
        return current;
      }
      current = current.parent || null;
    }
  }
  return null;
}

function findExistingRootInCurrentPage(figureId) {
  return figma.currentPage.findOne(
    (node) => node.type === "FRAME" && typeof node.getPluginData === "function" && node.getPluginData(FIGURE_KEY) === figureId,
  );
}

async function findExistingRootInDocument(figureId) {
  if (typeof figma.loadAllPagesAsync === "function") {
    await figma.loadAllPagesAsync();
  }
  for (const page of figma.root.children) {
    if (!page || page.type !== "PAGE") {
      continue;
    }
    const root = page.findOne(
      (node) => node.type === "FRAME" && typeof node.getPluginData === "function" && node.getPluginData(FIGURE_KEY) === figureId,
    );
    if (root) {
      return { page, root };
    }
  }
  return null;
}

async function resolveImportMode(bundle, requestedMode) {
  if (requestedMode && requestedMode !== "auto") {
    return requestedMode;
  }
  const figureId = String(bundle.figure_id || "pubfig-figure");
  if (findExistingRootInCurrentPage(figureId)) {
    return "refresh";
  }
  return (await findExistingRootInDocument(figureId)) ? "refresh" : "import";
}

function getBridgeSessionSnapshot(bridgeUrl) {
  return {
    client_name: "pubfig-sync",
    file_name: figma.root.name || "Untitled",
    page_name: figma.currentPage.name || "Page 1",
    plugin_version: PLUGIN_VERSION,
    bridge_url: String(bridgeUrl || ""),
    meta: {
      selection_count: figma.currentPage.selection.length,
      current_page_id: figma.currentPage.id,
    },
  };
}

async function ensureRootFrame(bundle, mode) {
  const figureId = String(bundle.figure_id || "pubfig-figure");
  if (mode !== "import") {
    const selected = findFigureRootFromSelection(figureId);
    if (selected) {
      selected.fills = [{ type: "SOLID", color: ROOT_BACKGROUND }];
      return { page: figma.currentPage, root: selected };
    }

    const fallback = figma.currentPage.findOne(
      (node) => node.type === "FRAME" && node.getPluginData(FIGURE_KEY) === figureId,
    );
    if (fallback) {
      fallback.fills = [{ type: "SOLID", color: ROOT_BACKGROUND }];
      return { page: figma.currentPage, root: fallback };
    }

    const anywhere = await findExistingRootInDocument(figureId);
    if (anywhere) {
      if (anywhere.page && anywhere.page.id !== figma.currentPage.id) {
        await figma.setCurrentPageAsync(anywhere.page);
      }
      anywhere.root.fills = [{ type: "SOLID", color: ROOT_BACKGROUND }];
      return anywhere;
    }

    throw new Error(
      `Could not find an existing figure frame for figure_id "${figureId}" anywhere in this Figma document.`,
    );
  }

  const page = figma.createPage();
  page.name = `pubfig/${figureId}`;
  await figma.setCurrentPageAsync(page);

  const root = figma.createFrame();
  root.name = `figure/${figureId}`;
  root.layoutMode = "NONE";
  root.fills = [{ type: "SOLID", color: ROOT_BACKGROUND }];
  root.clipsContent = false;
  root.setPluginData(FIGURE_KEY, figureId);
  root.setPluginData(VERSION_KEY, String(bundle.pubfig_version || ""));
  root.setRelaunchData({
    refresh: "Refresh pubfig panels",
    relayout: "Refresh and relayout pubfig figure",
  });
  page.appendChild(root);
  return { page, root };
}

function ensureManagedFrame(root, role) {
  let frame = getRoleNode(root, role);
  if (frame && frame.type !== "FRAME") {
    frame.remove();
    frame = null;
  }
  if (!frame) {
    frame = figma.createFrame();
    frame.name = role;
    frame.layoutMode = "NONE";
    frame.clipsContent = false;
    frame.cornerRadius = 0;
    frame.strokes = [];
    frame.strokeWeight = 0;
    root.appendChild(frame);
  }
  frame.setPluginData(ROLE_KEY, role);
  return frame;
}

function clearChildren(node) {
  for (const child of [...node.children]) {
    child.remove();
  }
}

function ensurePanelFrame(root, panel, mode) {
  const panelId = String(panel.panel_id);
  const existing = root.findOne(
    (node) => node.type === "FRAME" && node.getPluginData(PANEL_KEY) === panelId,
  );
  if (existing) {
    existing.name = String(panel.figma_node_name || `panel/${panelId}`);
    existing.layoutMode = "NONE";
    existing.fills = [{ type: "SOLID", color: PANEL_BACKGROUND }];
    existing.strokes = [];
    existing.strokeWeight = 0;
    existing.cornerRadius = 0;
    existing.clipsContent = false;
    return existing;
  }
  if (mode !== "import") {
    throw new Error(`Could not find existing panel frame for panel_id "${panelId}" during refresh.`);
  }

  const frame = figma.createFrame();
  frame.name = String(panel.figma_node_name || `panel/${panelId}`);
  frame.layoutMode = "NONE";
  frame.fills = [{ type: "SOLID", color: PANEL_BACKGROUND }];
  frame.strokes = [];
  frame.strokeWeight = 0;
  frame.cornerRadius = 0;
  frame.clipsContent = false;
  frame.setPluginData(PANEL_KEY, panelId);
  frame.setPluginData(ROLE_KEY, "panel-frame");
  root.appendChild(frame);
  return frame;
}

function removePanelContent(frame) {
  const existing = frame.findOne(
    (node) => typeof node.getPluginData === "function" && node.getPluginData(ROLE_KEY) === "panel-content",
  );
  if (existing) {
    existing.remove();
  }
}

async function ensurePanelLabel(frame, panel, fontReady, labelSettings) {
  let labelNode = frame.findOne(
    (node) => node.type === "TEXT" && node.getPluginData(PANEL_KEY) === `${panel.panel_id}:label`,
  );
  if (!labelSettings.enabled) {
    if (labelNode) {
      labelNode.remove();
    }
    return null;
  }
  if (!fontReady) {
    return null;
  }

  if (!labelNode) {
    labelNode = figma.createText();
    labelNode.name = `${panel.panel_id}-label`;
    labelNode.fontName = { family: "Inter", style: "Bold" };
    labelNode.fontSize = 14;
    labelNode.fills = [{ type: "SOLID", color: TEXT_COLOR }];
    labelNode.setPluginData(PANEL_KEY, `${panel.panel_id}:label`);
    labelNode.setPluginData(ROLE_KEY, "panel-label");
    frame.appendChild(labelNode);
  } else {
    await figma.loadFontAsync(labelNode.fontName);
  }

  labelNode.characters = getPanelLabelText(panel, labelSettings);
  frame.appendChild(labelNode);
  return labelNode;
}

async function upsertPanelFrame(frame, panel, fontReady, mode, fitContent, labelSettings) {
  const previousGeometry = {
    x: frame.x,
    y: frame.y,
    width: getNodeWidth(frame, DEFAULT_PANEL_WIDTH),
    height: getNodeHeight(frame, DEFAULT_PANEL_HEIGHT),
  };

  removePanelContent(frame);

  const svgNode = figma.createNodeFromSvg(String(panel.svg || ""));
  svgNode.name = `${panel.panel_id}-content`;
  svgNode.setPluginData(ROLE_KEY, "panel-content");
  frame.appendChild(svgNode);

  const labelNode = await ensurePanelLabel(frame, panel, fontReady, labelSettings);
  const naturalWidth = Math.max(260, Math.ceil(getNodeWidth(svgNode, DEFAULT_PANEL_WIDTH)) + PANEL_PADDING * 2);
  const naturalHeight = Math.max(
    200,
    Math.ceil(getNodeHeight(svgNode, DEFAULT_PANEL_HEIGHT)) + PANEL_PADDING * 2 + (labelNode ? LABEL_HEIGHT : 0),
  );

  if (mode === "import" || fitContent) {
    frame.resizeWithoutConstraints(naturalWidth, naturalHeight);
  } else {
    frame.resizeWithoutConstraints(previousGeometry.width, previousGeometry.height);
    frame.x = previousGeometry.x;
    frame.y = previousGeometry.y;
  }

  svgNode.x = PANEL_PADDING;
  svgNode.y = PANEL_PADDING;

  frame.setPluginData(SOURCE_KEY, String(panel.source_path || ""));
  frame.setPluginData(VERSION_KEY, String(panel.pubfig_version || ""));
}

async function ensurePlaceholderText(frame, role, text, fontReady) {
  if (!fontReady) {
    return null;
  }

  let label = frame.findOne(
    (node) => node.type === "TEXT" && node.getPluginData(ROLE_KEY) === `${role}-label`,
  );
  if (!label) {
    label = figma.createText();
    label.fontName = { family: "Inter", style: "Bold" };
    label.fontSize = role === "shared-title" ? 18 : 14;
    label.fills = [{ type: "SOLID", color: TEXT_COLOR }];
    label.setPluginData(ROLE_KEY, `${role}-label`);
    frame.appendChild(label);
  } else {
    await figma.loadFontAsync(label.fontName);
  }

  label.characters = text;
  label.x = TEXT_INSET;
  label.y = TEXT_INSET;
  return label;
}

async function upsertPlaceholderFrame(root, role, text, geometry, fontReady, preserveGeometry) {
  let frame = getRoleNode(root, role);
  if (!frame) {
    frame = figma.createFrame();
    frame.name = role;
    frame.layoutMode = "NONE";
    frame.cornerRadius = 12;
    frame.strokes = [{ type: "SOLID", color: PLACEHOLDER_STROKE }];
    frame.strokeWeight = 1;
    frame.fills = [{ type: "SOLID", color: PLACEHOLDER_FILL }];
    frame.clipsContent = false;
    frame.setPluginData(ROLE_KEY, role);
    root.appendChild(frame);
  } else if (frame.type !== "FRAME") {
    frame.remove();
    return upsertPlaceholderFrame(root, role, text, geometry, fontReady, false);
  }

  const width = clampPositive(geometry.width, role === "shared-title" ? DEFAULT_PANEL_WIDTH : DEFAULT_LEGEND_WIDTH);
  const height = clampPositive(
    geometry.height,
    role === "shared-title" ? DEFAULT_TITLE_HEIGHT : DEFAULT_LEGEND_HEIGHT,
  );

  if (!preserveGeometry || getNodeWidth(frame, 0) <= 1 || getNodeHeight(frame, 0) <= 1) {
    frame.resizeWithoutConstraints(width, height);
    frame.x = Number.isFinite(geometry.x) ? geometry.x : 0;
    frame.y = Number.isFinite(geometry.y) ? geometry.y : 0;
  }

  await ensurePlaceholderText(frame, role, text, fontReady);
  return frame;
}

function getManagedPanelFrames(root, bundle) {
  const ordered = [];
  const seen = new Set();
  for (const panel of bundle.panels || []) {
    const panelId = String(panel.panel_id);
    const frame = root.findOne(
      (node) => node.type === "FRAME" && node.getPluginData(PANEL_KEY) === panelId,
    );
    if (frame) {
      ordered.push(frame);
      seen.add(panelId);
    }
  }

  for (const child of root.children) {
    if (child.type !== "FRAME") {
      continue;
    }
    const panelId = child.getPluginData(PANEL_KEY);
    if (panelId && !seen.has(panelId)) {
      ordered.push(child);
    }
  }
  return ordered;
}

function getPanelGridPosition(frame, fallbackIndex) {
  const rowValue = Number(frame.getPluginData(PANEL_ROW_KEY));
  const columnValue = Number(frame.getPluginData(PANEL_COLUMN_KEY));
  const rowIndex = Number.isFinite(rowValue) && rowValue >= 0 ? Math.round(rowValue) : fallbackIndex;
  const columnIndex = Number.isFinite(columnValue) && columnValue >= 0 ? Math.round(columnValue) : 0;
  return { rowIndex, columnIndex };
}

async function applyPanelLabels(root, bundle, panelFrames, fontReady) {
  const labelSettings = getPanelLabelSettings(bundle);
  const panelById = new Map((bundle.panels || []).map((panel) => [String(panel.panel_id), panel]));
  const labelNodes = [];
  const columnBaselineX = new Map();
  const rowBaselineY = new Map();

  for (let index = 0; index < panelFrames.length; index += 1) {
    const frame = panelFrames[index];
    const panelId = String(frame.getPluginData(PANEL_KEY) || "");
    const panel = panelById.get(panelId);
    if (!panel) {
      continue;
    }

    const labelNode = await ensurePanelLabel(frame, panel, fontReady, labelSettings);
    if (!labelNode) {
      continue;
    }

    const gridPosition = getPanelGridPosition(frame, index);
    const preferredX = frame.x - labelSettings.offsetX;
    const preferredY = frame.y - labelSettings.offsetY;
    columnBaselineX.set(
      gridPosition.columnIndex,
      columnBaselineX.has(gridPosition.columnIndex)
        ? Math.min(columnBaselineX.get(gridPosition.columnIndex), preferredX)
        : preferredX,
    );
    rowBaselineY.set(
      gridPosition.rowIndex,
      rowBaselineY.has(gridPosition.rowIndex)
        ? Math.min(rowBaselineY.get(gridPosition.rowIndex), preferredY)
        : preferredY,
    );
    labelNodes.push({ frame, labelNode, gridPosition });
  }

  for (const item of labelNodes) {
    const x = labelSettings.alignX === "column"
      ? columnBaselineX.get(item.gridPosition.columnIndex)
      : item.frame.x - labelSettings.offsetX;
    const y = labelSettings.alignY === "row"
      ? rowBaselineY.get(item.gridPosition.rowIndex)
      : item.frame.y - labelSettings.offsetY;
    item.labelNode.x = x - item.frame.x;
    item.labelNode.y = y - item.frame.y;
    item.frame.appendChild(item.labelNode);
  }
}

function layoutRow(panelFrames, gap, labelSettings) {
  let maxHeight = 0;
  for (const frame of panelFrames) {
    maxHeight = Math.max(maxHeight, getPanelSlotHeight(frame, labelSettings));
  }
  let x = 0;
  for (let index = 0; index < panelFrames.length; index += 1) {
    const frame = panelFrames[index];
    placePanelFrameAtSlot(frame, x, 0, 0, index, labelSettings);
    x += getPanelSlotWidth(frame, labelSettings) + gap;
  }
  return { width: Math.max(0, x - gap), height: maxHeight };
}

function layoutColumn(panelFrames, gap, labelSettings) {
  let maxWidth = 0;
  for (const frame of panelFrames) {
    maxWidth = Math.max(maxWidth, getPanelSlotWidth(frame, labelSettings));
  }
  let y = 0;
  for (let index = 0; index < panelFrames.length; index += 1) {
    const frame = panelFrames[index];
    placePanelFrameAtSlot(frame, 0, y, index, 0, labelSettings);
    y += getPanelSlotHeight(frame, labelSettings) + gap;
  }
  return { width: maxWidth, height: Math.max(0, y - gap) };
}

function layoutGrid(panelFrames, columns, gap, labelSettings) {
  const resolvedColumns = Math.max(1, Math.round(clampPositive(columns, chooseAutoGridColumns(panelFrames.length))));
  const rows = [];
  const columnWidths = new Array(resolvedColumns).fill(0);
  let totalHeight = 0;

  for (let index = 0; index < panelFrames.length; index += resolvedColumns) {
    const row = panelFrames.slice(index, index + resolvedColumns);
    let rowHeight = 0;
    for (let columnIndex = 0; columnIndex < row.length; columnIndex += 1) {
      const frame = row[columnIndex];
      rowHeight = Math.max(rowHeight, getPanelSlotHeight(frame, labelSettings));
      columnWidths[columnIndex] = Math.max(columnWidths[columnIndex], getPanelSlotWidth(frame, labelSettings));
    }
    rows.push({ frames: row, height: rowHeight });
    totalHeight += rowHeight + gap;
  }

  const maxRowWidth = columnWidths.reduce((accumulator, width) => accumulator + width, 0) + Math.max(0, resolvedColumns - 1) * gap;
  let rowY = 0;
  for (let rowIndex = 0; rowIndex < rows.length; rowIndex += 1) {
    const row = rows[rowIndex];
    let x = 0;
    for (let columnIndex = 0; columnIndex < row.frames.length; columnIndex += 1) {
      const frame = row.frames[columnIndex];
      placePanelFrameAtSlot(frame, x, rowY, rowIndex, columnIndex, labelSettings);
      x += columnWidths[columnIndex] + gap;
    }
    rowY += row.height + gap;
  }

  return { width: Math.max(0, maxRowWidth), height: Math.max(0, totalHeight - gap) };
}

function layoutRowsByCounts(panelFrames, rowPanelCounts, gap, labelSettings) {
  if (!rowPanelCounts || !rowPanelCounts.length) {
    return layoutGrid(panelFrames, chooseAutoGridColumns(panelFrames.length), gap, labelSettings);
  }

  const rows = [];
  const maxColumns = Math.max(...rowPanelCounts);
  const columnWidths = new Array(maxColumns).fill(0);
  let cursor = 0;
  let totalHeight = 0;

  for (const count of rowPanelCounts) {
    const rowFrames = panelFrames.slice(cursor, cursor + count);
    cursor += count;
    let rowHeight = 0;
    for (let columnIndex = 0; columnIndex < rowFrames.length; columnIndex += 1) {
      const frame = rowFrames[columnIndex];
      rowHeight = Math.max(rowHeight, getPanelSlotHeight(frame, labelSettings));
      columnWidths[columnIndex] = Math.max(columnWidths[columnIndex], getPanelSlotWidth(frame, labelSettings));
    }
    rows.push({ frames: rowFrames, height: rowHeight });
    totalHeight += rowHeight + gap;
  }

  const maxRowWidth = columnWidths.reduce((accumulator, width) => accumulator + width, 0) + Math.max(0, maxColumns - 1) * gap;
  let rowY = 0;
  for (let rowIndex = 0; rowIndex < rows.length; rowIndex += 1) {
    const row = rows[rowIndex];
    let x = 0;
    for (let columnIndex = 0; columnIndex < row.frames.length; columnIndex += 1) {
      const frame = row.frames[columnIndex];
      placePanelFrameAtSlot(frame, x, rowY, rowIndex, columnIndex, labelSettings);
      x += columnWidths[columnIndex] + gap;
    }
    rowY += row.height + gap;
  }

  return { width: Math.max(0, maxRowWidth), height: Math.max(0, totalHeight - gap) };
}

function layoutHeroLeft(panelFrames, gap, labelSettings) {
  if (panelFrames.length === 0) {
    return { width: DEFAULT_PANEL_WIDTH, height: DEFAULT_PANEL_HEIGHT };
  }
  if (panelFrames.length === 1) {
    placePanelFrameAtSlot(panelFrames[0], 0, 0, 0, 0, labelSettings);
    return { width: getPanelSlotWidth(panelFrames[0], labelSettings), height: getPanelSlotHeight(panelFrames[0], labelSettings) };
  }

  const hero = panelFrames[0];
  placePanelFrameAtSlot(hero, 0, 0, 0, 0, labelSettings);

  const rightX = getPanelSlotWidth(hero, labelSettings) + gap;
  let rightWidth = 0;
  for (let index = 1; index < panelFrames.length; index += 1) {
    rightWidth = Math.max(rightWidth, getPanelSlotWidth(panelFrames[index], labelSettings));
  }
  let y = 0;
  for (let index = 1; index < panelFrames.length; index += 1) {
    const frame = panelFrames[index];
    placePanelFrameAtSlot(frame, rightX, y, index - 1, 1, labelSettings);
    y += getPanelSlotHeight(frame, labelSettings) + gap;
  }
  return {
    width: getPanelSlotWidth(hero, labelSettings) + gap + rightWidth,
    height: Math.max(getPanelSlotHeight(hero, labelSettings), Math.max(0, y - gap)),
  };
}

function layoutHeroTop(panelFrames, gap, labelSettings) {
  if (panelFrames.length === 0) {
    return { width: DEFAULT_PANEL_WIDTH, height: DEFAULT_PANEL_HEIGHT };
  }
  if (panelFrames.length === 1) {
    placePanelFrameAtSlot(panelFrames[0], 0, 0, 0, 0, labelSettings);
    return { width: getPanelSlotWidth(panelFrames[0], labelSettings), height: getPanelSlotHeight(panelFrames[0], labelSettings) };
  }

  const hero = panelFrames[0];
  placePanelFrameAtSlot(hero, 0, 0, 0, 0, labelSettings);

  let bottomRowHeight = 0;
  let bottomRowWidth = 0;
  for (let index = 1; index < panelFrames.length; index += 1) {
    const frame = panelFrames[index];
    bottomRowHeight = Math.max(bottomRowHeight, getPanelSlotHeight(frame, labelSettings));
    bottomRowWidth += getPanelSlotWidth(frame, labelSettings);
  }
  if (panelFrames.length > 1) {
    bottomRowWidth += gap * (panelFrames.length - 2);
  }
  let x = Math.max(0, (Math.max(getPanelSlotWidth(hero, labelSettings), bottomRowWidth) - bottomRowWidth) / 2);
  const rowY = getPanelSlotHeight(hero, labelSettings) + gap;
  for (let index = 1; index < panelFrames.length; index += 1) {
    const frame = panelFrames[index];
    placePanelFrameAtSlot(frame, x, rowY, 1, index - 1, labelSettings);
    x += getPanelSlotWidth(frame, labelSettings) + gap;
  }

  return {
    width: Math.max(getPanelSlotWidth(hero, labelSettings), bottomRowWidth),
    height: getPanelSlotHeight(hero, labelSettings) + gap + bottomRowHeight,
  };
}

function offsetPanelFrames(panelFrames, offsetX, offsetY) {
  for (const frame of panelFrames) {
    frame.x += offsetX;
    frame.y += offsetY;
  }
}

function computeBounds(nodes) {
  if (!nodes.length) {
    return { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0 };
  }
  const minX = Math.min(...nodes.map((node) => Number(node.x) || 0));
  const minY = Math.min(...nodes.map((node) => Number(node.y) || 0));
  const maxX = Math.max(...nodes.map((node) => (Number(node.x) || 0) + getNodeWidth(node, 0)));
  const maxY = Math.max(...nodes.map((node) => (Number(node.y) || 0) + getNodeHeight(node, 0)));
  return { minX, minY, maxX, maxY, width: Math.max(0, maxX - minX), height: Math.max(0, maxY - minY) };
}

function collectRelativeBounds(node, originX, originY, collector) {
  if (!node || node.visible === false) {
    return;
  }
  const x = originX + (Number(node.x) || 0);
  const y = originY + (Number(node.y) || 0);
  collector.push({
    minX: x,
    minY: y,
    maxX: x + getNodeWidth(node, 0),
    maxY: y + getNodeHeight(node, 0),
  });
  if ("children" in node) {
    for (const child of node.children) {
      collectRelativeBounds(child, x, y, collector);
    }
  }
}

function computeRelativeBounds(root) {
  const entries = [];
  for (const child of root.children) {
    collectRelativeBounds(child, 0, 0, entries);
  }
  if (!entries.length) {
    return { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0 };
  }
  const minX = Math.min(...entries.map((entry) => entry.minX));
  const minY = Math.min(...entries.map((entry) => entry.minY));
  const maxX = Math.max(...entries.map((entry) => entry.maxX));
  const maxY = Math.max(...entries.map((entry) => entry.maxY));
  return { minX, minY, maxX, maxY, width: Math.max(0, maxX - minX), height: Math.max(0, maxY - minY) };
}

function computeManagedRootBounds(root, labelSettings) {
  const nodes = root.children.filter((node) => node.visible !== false);
  if (!nodes.length) {
    return { minX: 0, minY: 0, maxX: 0, maxY: 0, width: 0, height: 0 };
  }

  const entries = nodes.map((node) => {
    const isPanelFrame = node.type === "FRAME" && typeof node.getPluginData === "function" && Boolean(node.getPluginData(PANEL_KEY));
    const insetX = isPanelFrame && labelSettings && labelSettings.enabled ? labelSettings.offsetX : 0;
    const insetY = isPanelFrame && labelSettings && labelSettings.enabled ? labelSettings.offsetY : 0;
    const x = Number(node.x) || 0;
    const y = Number(node.y) || 0;
    return {
      minX: x - insetX,
      minY: y - insetY,
      maxX: x + getNodeWidth(node, 0),
      maxY: y + getNodeHeight(node, 0),
    };
  });

  const minX = Math.min(...entries.map((entry) => entry.minX));
  const minY = Math.min(...entries.map((entry) => entry.minY));
  const maxX = Math.max(...entries.map((entry) => entry.maxX));
  const maxY = Math.max(...entries.map((entry) => entry.maxY));
  return { minX, minY, maxX, maxY, width: Math.max(0, maxX - minX), height: Math.max(0, maxY - minY) };
}

function resizeRootToFit(root, labelSettings) {
  const bounds = computeManagedRootBounds(root, labelSettings);
  root.resizeWithoutConstraints(
    Math.max(1, Math.ceil(bounds.width)),
    Math.max(1, Math.ceil(bounds.height)),
  );
}

function normalizeRootChildrenOrigin(root, labelSettings) {
  const nodes = root.children.filter((node) => node.visible !== false);
  const bounds = computeManagedRootBounds(root, labelSettings);
  const shiftX = Number.isFinite(bounds.minX) ? -bounds.minX : 0;
  const shiftY = Number.isFinite(bounds.minY) ? -bounds.minY : 0;
  if (Math.abs(shiftX) < 0.5 && Math.abs(shiftY) < 0.5) {
    return;
  }
  for (const node of nodes) {
    node.x += shiftX;
    node.y += shiftY;
  }
}

async function applyPlaceholdersAndLayout(root, bundle, mode, requestedRelayout, fontReady) {
  const layout = getLayout(bundle);
  const labelSettings = getPanelLabelSettings(bundle);
  const placeholders = getPlaceholders(bundle);
  const panelFrames = getManagedPanelFrames(root, bundle);
  const resolvedPreset = resolvePreset(layout, panelFrames.length);
  const shouldRelayout = requestedRelayout || mode === "import" || !layout.preservePositionsOnRefresh;

  if (shouldRelayout) {
    let panelBounds;
    if (layout.rowPanelCounts && layout.rowPanelCounts.length) {
      panelBounds = layoutRowsByCounts(panelFrames, layout.rowPanelCounts, layout.panelGap, labelSettings);
    } else if (resolvedPreset === "row") {
      panelBounds = layoutRow(panelFrames, layout.panelGap, labelSettings);
    } else if (resolvedPreset === "column") {
      panelBounds = layoutColumn(panelFrames, layout.panelGap, labelSettings);
    } else if (resolvedPreset === "two_by_two") {
      panelBounds = layoutGrid(panelFrames, 2, layout.panelGap, labelSettings);
    } else if (resolvedPreset === "hero_left") {
      panelBounds = layoutHeroLeft(panelFrames, layout.panelGap, labelSettings);
    } else if (resolvedPreset === "hero_top") {
      panelBounds = layoutHeroTop(panelFrames, layout.panelGap, labelSettings);
    } else {
      panelBounds = layoutGrid(panelFrames, layout.columns, layout.panelGap, labelSettings);
    }

    let titleHeight = 0;
    if (placeholders.sharedTitle.enabled) {
      const titleFrame = await upsertPlaceholderFrame(
        root,
        "shared-title",
        placeholders.sharedTitle.text,
        {
          x: 0,
          y: 0,
          width: Math.max(panelBounds.width, DEFAULT_PANEL_WIDTH),
          height: DEFAULT_TITLE_HEIGHT,
        },
        fontReady,
        false,
      );
      titleHeight = titleFrame ? titleFrame.height + layout.panelGap : 0;
    } else {
      removeRoleNode(root, "shared-title");
    }

    offsetPanelFrames(panelFrames, 0, titleHeight);
    let rootWidth = panelBounds.width;
    let rootHeight = panelBounds.height + titleHeight;

    if (placeholders.sharedLegend.enabled) {
      if (placeholders.sharedLegend.position === "bottom") {
        const legend = await upsertPlaceholderFrame(
          root,
          "shared-legend",
          placeholders.sharedLegend.text,
          {
            x: 0,
            y: rootHeight + layout.panelGap,
            width: Math.max(panelBounds.width, DEFAULT_PANEL_WIDTH),
            height: DEFAULT_LEGEND_HEIGHT,
          },
          fontReady,
          false,
        );
        if (legend) {
          rootWidth = Math.max(rootWidth, legend.width);
          rootHeight = legend.y + legend.height;
        }
      } else {
        const legend = await upsertPlaceholderFrame(
          root,
          "shared-legend",
          placeholders.sharedLegend.text,
          {
            x: rootWidth + layout.panelGap,
            y: titleHeight,
            width: DEFAULT_LEGEND_WIDTH,
            height: Math.max(DEFAULT_LEGEND_HEIGHT, panelBounds.height),
          },
          fontReady,
          false,
        );
        if (legend) {
          rootWidth = legend.x + legend.width;
          rootHeight = Math.max(rootHeight, legend.y + legend.height);
        }
      }
    } else {
      removeRoleNode(root, "shared-legend");
    }

    root.resizeWithoutConstraints(Math.max(320, Math.ceil(rootWidth)), Math.max(240, Math.ceil(rootHeight)));
  } else {
    const currentPanelBounds = computeBounds(panelFrames);

    if (placeholders.sharedTitle.enabled) {
      await upsertPlaceholderFrame(
        root,
        "shared-title",
        placeholders.sharedTitle.text,
        {
          x: 0,
          y: 0,
          width: Math.max(currentPanelBounds.width, DEFAULT_PANEL_WIDTH),
          height: DEFAULT_TITLE_HEIGHT,
        },
        fontReady,
        true,
      );
    } else {
      removeRoleNode(root, "shared-title");
    }

    if (placeholders.sharedLegend.enabled) {
      const defaultLegendGeometry = placeholders.sharedLegend.position === "bottom"
        ? {
            x: currentPanelBounds.minX,
            y: currentPanelBounds.maxY + layout.panelGap,
            width: Math.max(currentPanelBounds.width, DEFAULT_PANEL_WIDTH),
            height: DEFAULT_LEGEND_HEIGHT,
          }
        : {
            x: currentPanelBounds.maxX + layout.panelGap,
            y: currentPanelBounds.minY,
            width: DEFAULT_LEGEND_WIDTH,
            height: Math.max(DEFAULT_LEGEND_HEIGHT, currentPanelBounds.height),
          };

      await upsertPlaceholderFrame(
        root,
        "shared-legend",
        placeholders.sharedLegend.text,
        defaultLegendGeometry,
        fontReady,
        true,
      );
    } else {
      removeRoleNode(root, "shared-legend");
    }

    resizeRootToFit(root, labelSettings);
  }

  root.setPluginData(LAYOUT_PRESET_KEY, resolvedPreset);
  root.setPluginData(PANEL_GAP_KEY, String(layout.panelGap));
  await applyPanelLabels(root, bundle, panelFrames, fontReady);
  normalizeRootChildrenOrigin(root, labelSettings);
  resizeRootToFit(root, labelSettings);
}

async function importBundle(bundle, mode, relayout) {
  const fontReady = await ensureBoldFont();
  const finalMode = await resolveImportMode(bundle, mode || "auto");
  const { root } = await ensureRootFrame(bundle, finalMode);
  const fitContent = finalMode === "import" || Boolean(relayout);
  const labelSettings = getPanelLabelSettings(bundle);

  for (const panel of bundle.panels || []) {
    const frame = ensurePanelFrame(root, panel, finalMode);
    await upsertPanelFrame(frame, panel, fontReady, finalMode, fitContent, labelSettings);
  }

  await applyPlaceholdersAndLayout(root, bundle, finalMode, relayout, fontReady);
  figma.viewport.scrollAndZoomIntoView([root]);
  figma.currentPage.selection = [root];
  return { root, mode: finalMode };
}

figma.ui.onmessage = async (message) => {
  if (!message || !message.type) {
    return;
  }

  if (message.type === "ping") {
    figma.ui.postMessage({
      type: "pong",
      pluginVersion: PLUGIN_VERSION,
      pageName: figma.currentPage ? figma.currentPage.name : "",
    });
    return;
  }

  if (message.type === "close") {
    figma.closePlugin();
    return;
  }

  if (message.type === "bridge-session-snapshot") {
    figma.ui.postMessage({
      type: "bridge-session-snapshot",
      snapshot: getBridgeSessionSnapshot(message.bridgeUrl),
    });
    return;
  }

  if (message.type === "import-bundle") {
    try {
      const bundle = message.bundle;
      if (!bundle || !isPanelBundle(bundle)) {
        throw new Error("Invalid pubfig Figma bundle JSON.");
      }
      const mode = message.mode || "auto";
      const relayout = Boolean(message.relayout);
      const importResult = await importBundle(bundle, mode, relayout);
      const actionLabel = importResult.mode === "import"
        ? "imported"
        : relayout
          ? "refreshed + relayout applied"
          : "refreshed";
      figma.notify(`pubfig bundle ${actionLabel}: ${importResult.root.name}`);
      figma.ui.postMessage({
        type: "import-result",
        ok: true,
        figureId: bundle.figure_id,
        rootName: importResult.root.name,
        pageName: figma.currentPage.name,
        panelCount: Array.isArray(bundle.panels) ? bundle.panels.length : 0,
        sourcePanelDir: String(bundle.source_panel_dir || ""),
        workflowPath: String((bundle.workflow && bundle.workflow.path) || "panel-first"),
        bundleProvenance: message.bundleProvenance || null,
        mode: importResult.mode,
        relayout,
      });
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      figma.ui.postMessage({ type: "import-result", ok: false, error: detail });
      figma.notify(`pubfig-sync failed: ${detail}`, { error: true });
    }
  }
};
