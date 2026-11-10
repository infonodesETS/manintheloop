# Networks page — layout parameter reference

> Read this before modifying node spacing, clustering, or visual density in `networks.html`.

## Where the parameters live

File: `refactoringDB/networks.html`
Function: `buildLayout(nodeCount)` — around line 689.

The function returns a Cytoscape.js **cose** layout config object. It selects values based on `nodeCount` (total nodes in the current graph):

| Bucket | Condition | Typical countries |
|---|---|---|
| Small | `nodeCount ≤ 150` | Small EDF countries, EDF-only filter |
| Medium | `150 < nodeCount ≤ 300` | Italy, Spain, Germany, Poland (EDF + Inv) |
| Large | `nodeCount > 300` | France, all-countries view |

---

## Parameters and their effect

### `idealEdgeLength` — controls how far connected nodes sit from each other
- Higher → nodes spread further apart along their edges
- Too high → disconnected-looking graph, lots of empty space
- **Current values:** small=150, medium=120, large=90

### `nodeRepulsion` — repulsion force between every pair of nodes
- Higher → nodes push each other further apart globally
- Too high → nodes fly to the edges, no visible structure
- **Current values:** small=14000, medium=9000, large=5000

### `gravity` — force pulling all nodes toward the canvas centre
- Lower → less centre-clustering, more spread across canvas
- Too low → the graph breaks apart into disconnected islands
- **Current values:** small/medium=0.03, large=0.06

### `nodeOverlap` — minimum pixel gap between node bounding boxes
- Higher → nodes never visually overlap, but takes more space
- **Current value:** 20 (uniform across all sizes)

### `componentSpacing` — extra gap between disconnected sub-graphs
- Higher → isolated clusters don't touch each other
- **Current value:** 80 (uniform)

### `edgeElasticity` — stiffness of edges (how hard they pull connected nodes together)
- Lower → edges are looser, nodes have more freedom to spread
- Default is 100; we use 70
- **Current value:** 70 (uniform)

### `numIter` — number of simulation steps before stopping
- Higher → better final layout, but slower (blocking the main thread)
- **Current values:** small=1400, medium=1000, large=600

### `coolingFactor` — how fast the simulation "freezes"
- Closer to 1.0 → slower cooling, more iterations matter
- **Current value:** 0.95 (uniform)

---

## Current `buildLayout` code (as of 2026-05-27)

```js
function buildLayout(nodeCount) {
  if (nodeCount <= 1) return { name: 'grid' };
  return {
    name: 'cose',
    animate: false,
    randomize: false,
    idealEdgeLength:  nodeCount > 300 ? 90  : nodeCount > 150 ? 120 : 150,
    nodeRepulsion:    () => nodeCount > 300 ? 5000 : nodeCount > 150 ? 9000 : 14000,
    nodeOverlap:      20,
    gravity:          nodeCount > 300 ? 0.06 : 0.03,
    numIter:          nodeCount > 500 ? 600  : nodeCount > 200 ? 1000 : 1400,
    componentSpacing: 80,
    coolingFactor:    0.95,
    edgeElasticity:   () => 70,
  };
}
```

---

## Tuning guide

| Symptom | Fix |
|---|---|
| Nodes too close / overlapping | Raise `nodeRepulsion`, raise `idealEdgeLength`, lower `gravity` |
| Graph too spread out / islands | Lower `nodeRepulsion`, raise `gravity`, lower `idealEdgeLength` |
| Centre cluster still visible | Lower `gravity` further (try 0.01–0.02) |
| Layout too slow | Lower `numIter`, raise `coolingFactor` toward 0.99 |
| Nodes still overlapping despite repulsion | Raise `nodeOverlap` |
| Disconnected sub-graphs touching | Raise `componentSpacing` |

---

## Node size constants (lines 434–435)

```js
const CIRCLE_SIZE = 14;           // default size for entity and investor nodes
const DIAM_MIN = 10, DIAM_MAX = 36; // EDF project diamond: scaled by EU budget
```

EDF project diamonds are scaled between `DIAM_MIN` and `DIAM_MAX` proportionally to `eu_contribution`. Entity/investor circles are all `CIRCLE_SIZE` (degree-scaled only for outbound investors in `buildElements()`).

---

## Related files

| File | Role |
|---|---|
| `networks.html` | All graph logic: `buildElements()`, `buildLayout()`, `renderNetwork()`, `CY_STYLE` |
| `web/graph.js` | Ego-graph card in `search.html` — separate Cytoscape instance, different layout |
| `data/database.json` | Source data for all nodes and edges |
