'use strict';

// Node colors — aligned with search.html palette
const COLORS = {
  center:            '#00ff41',
  company:           '#aaffdd',
  institution:       '#ff99bb',
  fund:              '#ffaa55',
  investor:          '#ffaa55',
  public_fund:       '#ffaa55',
  government_agency: '#ff5555',
  bank:              '#cc3333',
  edf_project:       '#64a0ff',
  default:           '#888888',
};

function nodeColor(type) {
  return COLORS[type] || COLORS.default;
}

function truncate(str, max) {
  if (!str) return '';
  return str.length > max ? str.slice(0, max - 1) + '…' : str;
}

// Build Cytoscape elements (1-hop ego graph) from relMap
// Shapes:
//   1/2 — EDF-heavy / mixed  → edf_participant rels → project nodes
//   3   — Investors only     → target rels → investor nodes around center
//   4   — IV-investor        → investor rels → portfolio nodes
//   EDF project profile      → edf_member rels → participant nodes
export function buildElements(entityId, entityMap, relMap) {
  const center = entityMap[entityId];
  if (!center) return { elements: [], nodeCount: 0, hasEdf: false };

  const nodes = new Map();
  const edges = [];
  let hasEdf = false;

  // Center node
  nodes.set(entityId, {
    data: { id: entityId, label: truncate(center.name, 20), type: center.type },
    classes: 'center-node',
  });

  for (const { rel, role, other } of (relMap[entityId] || [])) {
    if (!other) continue;
    const oid = other.id;

    if (role === 'edf_participant') {
      hasEdf = true;
      if (!nodes.has(oid))
        nodes.set(oid, { data: { id: oid, label: truncate(other.name, 20), type: 'edf_project' }, classes: 'edf-node' });
      edges.push({ data: { id: `e${entityId}${oid}`, source: entityId, target: oid, etype: 'edf' } });

    } else if (role === 'target') {
      // other invested in center
      if (!nodes.has(oid))
        nodes.set(oid, { data: { id: oid, label: truncate(other.name, 20), type: other.type || 'investor' }, classes: 'investor-node' });
      edges.push({ data: { id: `e${oid}${entityId}`, source: oid, target: entityId, etype: 'investment' } });

    } else if (role === 'investor') {
      // center invested in other (IV profile)
      if (!nodes.has(oid))
        nodes.set(oid, { data: { id: oid, label: truncate(other.name, 20), type: other.type || 'company' }, classes: 'portfolio-node' });
      edges.push({ data: { id: `e${entityId}${oid}`, source: entityId, target: oid, etype: 'investment' } });

    } else if (role === 'edf_member') {
      // center IS an EDF project; other is a participant
      if (!nodes.has(oid))
        nodes.set(oid, { data: { id: oid, label: truncate(other.name, 20), type: other.type || 'company' }, classes: 'portfolio-node' });
      edges.push({ data: { id: `e${oid}${entityId}`, source: oid, target: entityId, etype: 'edf' } });
    }
  }

  return { elements: [...nodes.values(), ...edges], nodeCount: nodes.size, hasEdf };
}

function spacingForCount(n) {
  if (n <= 6)  return 3.5;
  if (n <= 12) return 2.5;
  if (n <= 20) return 1.8;
  if (n <= 35) return 1.3;
  return 1.0;
}

function pickLayout(hasEdf, nodeCount) {
  if (nodeCount <= 1) return { name: 'grid' };

  // Large EDF graph → spring layout
  if (hasEdf && nodeCount > 40) {
    return {
      name: 'cose',
      animate: false,
      randomize: false,
      idealEdgeLength: 60,
      nodeRepulsion: () => 3000,
      gravity: 0.25,
      numIter: 1000,
    };
  }

  // Small-medium → concentric (center in middle, neighbors in ring)
  return {
    name: 'concentric',
    concentric: n => n.hasClass('center-node') ? 10 : 1,
    levelWidth: () => 1,
    spacingFactor: spacingForCount(nodeCount),
    animate: false,
  };
}

const CY_STYLE = [
  {
    selector: 'node',
    style: {
      'background-color': ele => nodeColor(ele.data('type')),
      'label': 'data(label)',
      'color': 'rgba(255,255,255,0.75)',
      'font-size': '8px',
      'font-family': '"JetBrains Mono", monospace',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'text-margin-y': '3px',
      'text-wrap': 'wrap',
      'text-max-width': '72px',
      'width': 14,
      'height': 14,
      'border-width': 0,
    }
  },
  {
    selector: 'node.center-node',
    style: {
      'background-color': COLORS.center,
      'width': 26,
      'height': 26,
      'font-size': '9px',
      'font-weight': 'bold',
      'color': '#fff',
      'text-margin-y': '4px',
    }
  },
  {
    selector: 'node:selected',
    style: { 'border-width': 2, 'border-color': '#fff', 'border-opacity': 0.6 }
  },
  {
    selector: 'node:active',
    style: { 'overlay-opacity': 0.12 }
  },
  {
    selector: 'edge',
    style: {
      'width': 1,
      'line-color': 'rgba(255,255,255,0.10)',
      'target-arrow-shape': 'none',
      'curve-style': 'haystack',
    }
  },
  {
    selector: 'edge[etype = "edf"]',
    style: { 'line-color': 'rgba(100,160,255,0.22)' }
  },
  {
    selector: 'edge[etype = "investment"]',
    style: {
      'line-color': 'rgba(255,165,80,0.22)',
      'line-style': 'dashed',
      'line-dash-pattern': [4, 3],
    }
  },
];

let activeCy = null;

export function destroyActive() {
  if (activeCy) { activeCy.destroy(); activeCy = null; }
}

// Render ego graph into containerEl.
// onNavigate(entityId) called when user clicks a non-center node.
export function initEgoGraph(containerEl, entityId, entityMap, relMap, onNavigate) {
  destroyActive();

  if (!window.cytoscape) {
    containerEl.innerHTML = '<div class="graph-placeholder">Cytoscape.js not loaded.</div>';
    return;
  }

  const { elements, nodeCount, hasEdf } = buildElements(entityId, entityMap, relMap);

  if (nodeCount <= 1) {
    containerEl.innerHTML = '<div class="graph-placeholder">No connections to display.</div>';
    return;
  }

  // Height proportional to node count, capped
  containerEl.style.height = Math.min(520, Math.max(280, nodeCount * 14)) + 'px';

  activeCy = window.cytoscape({
    container: containerEl,
    elements,
    style: CY_STYLE,
    layout: pickLayout(hasEdf, nodeCount),
    userZoomingEnabled: true,
    userPanningEnabled: true,
    boxSelectionEnabled: false,
    minZoom: 0.2,
    maxZoom: 4,
  });

  activeCy.fit(undefined, 28);

  if (onNavigate) {
    activeCy.on('tap', 'node', evt => {
      const nid = evt.target.id();
      if (nid !== entityId) onNavigate(nid);
    });
  }
}
