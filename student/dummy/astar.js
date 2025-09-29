// js/astar.js
(function (global) {
  "use strict";

  /** ---- Utilities ---- **/

  function euclid(a, b) {
    // Safe Euclidean distance; returns 0 if coords missing
    const dx = (a?.x ?? 0) - (b?.x ?? 0);
    const dy = (a?.y ?? 0) - (b?.y ?? 0);
    return Math.hypot(dx, dy);
  }

  function reconstructPath(cameFrom, currentId) {
    const path = [currentId];
    while (Object.prototype.hasOwnProperty.call(cameFrom, currentId)) {
      currentId = cameFrom[currentId];
      path.push(currentId);
    }
    return path.reverse();
  }

  // Minimal binary heap priority queue for [id, fScore]
  class MinHeap {
    constructor(getKey) {
      this.getKey = getKey; // function(item) -> comparable value
      this.data = [];
    }
    size() { return this.data.length; }
    peek() { return this.data[0]; }
    push(x) {
      this.data.push(x);
      this._siftUp(this.data.length - 1);
    }
    pop() {
      const a = this.data;
      if (a.length === 0) return undefined;
      const top = a[0];
      const end = a.pop();
      if (a.length) {
        a[0] = end;
        this._siftDown(0);
      }
      return top;
    }
    _siftUp(i) {
      const a = this.data;
      const item = a[i], key = this.getKey(item);
      while (i > 0) {
        const p = ((i - 1) >> 1);
        if (key >= this.getKey(a[p])) break;
        a[i] = a[p];
        i = p;
      }
      a[i] = item;
    }
    _siftDown(i) {
      const a = this.data;
      const n = a.length;
      const item = a[i];
      const key = this.getKey(item);
      while (true) {
        let l = (i << 1) + 1;
        if (l >= n) break;
        let r = l + 1;
        let m = (r < n && this.getKey(a[r]) < this.getKey(a[l])) ? r : l;
        if (this.getKey(a[m]) >= key) break;
        a[i] = a[m];
        i = m;
      }
      a[i] = item;
    }
  }

  /** ---- Core A* ----
   * Params:
   *  - nodes:  [{ id, x, y, type? }]
   *  - edges:  [{ from, to, weight? }]
   *  - startId: string
   *  - goalIds: string[]  (OR pass goalTest(nodeId) instead)
   *  - heuristic(nodeA, nodeB) -> number  (defaults to euclid)
   *  - costPenalty(uNode, vNode, edge) -> number|Infinity  (optional)
   *  - undirected: boolean (default true)
   *  - goalTest: (id) => boolean (optional; used if provided)
   */
  function aStar({
    nodes,
    edges,
    startId,
    goalIds = [],
    heuristic = euclid,
    costPenalty = null,
    undirected = true,
    goalTest = null
  }) {
    // ---- Input validation
    if (!Array.isArray(nodes) || nodes.length === 0) {
      console.warn("[A*] nodes array is empty.");
      return null;
    }
    if (!Array.isArray(edges)) {
      console.warn("[A*] edges must be an array.");
      return null;
    }
    if (!startId) {
      console.warn("[A*] startId is required.");
      return null;
    }
    const useGoalTest = typeof goalTest === "function";
    if (!useGoalTest && (!Array.isArray(goalIds) || goalIds.length === 0)) {
      console.warn("[A*] Provide goalIds[] or a goalTest(id) function.");
      return null;
    }

    // ---- Index nodes
    const nodeById = new Map(nodes.map(n => [n.id, n]));
    if (!nodeById.has(startId)) {
      console.warn(`[A*] startId "${startId}" not found in nodes.`);
      return null;
    }
    const goalSet = useGoalTest ? null : new Set(goalIds.filter(id => nodeById.has(id)));
    if (!useGoalTest && goalSet.size === 0) {
      console.warn("[A*] None of the goalIds exist in nodes.");
      return null;
    }

    // ---- Build adjacency
    const adj = new Map(); // id -> [{nid, baseWeight, edge}]
    function addEdge(u, v, e) {
      if (!adj.has(u)) adj.set(u, []);
      adj.get(u).push(v);
    }
    let skippedEdges = 0;
    for (const e of edges) {
      const a = nodeById.get(e.from);
      const b = nodeById.get(e.to);
      if (!a || !b) { skippedEdges++; continue; }
      const w = (typeof e.weight === "number") ? e.weight : euclid(a, b);
      const uv = { nid: e.to, baseWeight: w, edge: e };
      addEdge(e.from, uv, e);
      if (undirected) {
        const vu = { nid: e.from, baseWeight: w, edge: e };
        addEdge(e.to, vu, e);
      }
    }
    if (skippedEdges > 0) {
      console.warn(`[A*] Skipped ${skippedEdges} edge(s) referencing missing node(s).`);
    }

    // ---- Helper to run A* to a single goalId
    function runToGoalId(goalId) {
      const startNode = nodeById.get(startId);
      const goalNode  = nodeById.get(goalId);

      if (!goalNode) return null;

      const openHeap = new MinHeap(item => item.f);
      const openSet = new Set(); // membership check
      const cameFrom = {};
      const gScore = new Map([[startId, 0]]);
      const f0 = heuristic(startNode, goalNode);
      const fScore = new Map([[startId, isFinite(f0) && f0 >= 0 ? f0 : 0]]);
      openHeap.push({ id: startId, f: fScore.get(startId) });
      openSet.add(startId);

      const visited = new Set();

      while (openHeap.size()) {
        const current = openHeap.pop();
        if (!openSet.has(current.id)) continue; // skip stale entries
        openSet.delete(current.id);

        if (current.id === goalId) {
          const path = reconstructPath(cameFrom, current.id);
          return {
            goal: goalId,
            cost: gScore.get(current.id),
            path,
            visitedCount: visited.size
          };
        }

        visited.add(current.id);
        const neighbors = adj.get(current.id) || [];
        for (const n of neighbors) {
          if (!nodeById.has(n.nid)) continue;

          let penalty = 0;
          if (typeof costPenalty === "function") {
            penalty = costPenalty(nodeById.get(current.id), nodeById.get(n.nid), n.edge);
            if (penalty === Infinity) continue; // block this edge
          }

          const gCurr = gScore.get(current.id);
          const base = (typeof n.baseWeight === "number" && isFinite(n.baseWeight)) ? n.baseWeight : euclid(nodeById.get(current.id), nodeById.get(n.nid));
          const tentative = gCurr + base + (isFinite(penalty) ? penalty : 0);

          if (tentative < (gScore.get(n.nid) ?? Infinity)) {
            cameFrom[n.nid] = current.id;
            gScore.set(n.nid, tentative);
            const h = heuristic(nodeById.get(n.nid), goalNode);
            const hSafe = (isFinite(h) && h >= 0) ? h : 0;
            const f = tentative + hSafe;
            fScore.set(n.nid, f);
            openHeap.push({ id: n.nid, f });
            openSet.add(n.nid);
          }
        }
      }
      return null; // unreachable
    }

    // ---- If using goalTest, we transform to a multi-goal search by scanning goals found during expansion.
    if (useGoalTest) {
      // We’ll do a multi-source-like loop by trying every node as a potential dynamic goal via a two-phase approach:
      // 1) Collect candidate goal ids from nodes that satisfy goalTest.
      const dynamicGoals = nodes.filter(n => goalTest(n.id)).map(n => n.id);
      if (dynamicGoals.length === 0) return null;

      let best = null;
      for (const gid of dynamicGoals) {
        const res = runToGoalId(gid);
        if (res && (!best || res.cost < best.cost)) best = res;
      }
      return best;
    } else {
      // Try each goalId; take best cost
      let best = null;
      for (const gid of goalSet) {
        const res = runToGoalId(gid);
        if (res && (!best || res.cost < best.cost)) best = res;
      }
      return best;
    }
  }

  // Expose
  global.Pathfinding = { aStar, euclid };
})(window);
