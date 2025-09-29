// js/astar.js
(function (global) {
  function euclid(a, b) {
    const dx = a.x - b.x, dy = a.y - b.y;
    return Math.hypot(dx, dy);
  }

  function reconstructPath(cameFrom, currentId) {
    const path = [currentId];
    while (cameFrom[currentId]) {
      currentId = cameFrom[currentId];
      path.push(currentId);
    }
    return path.reverse();
  }

  function aStar({ nodes, edges, startId, goalIds, heuristic = euclid, costPenalty = null }) {
    const nodeById = new Map(nodes.map(n => [n.id, n]));
    const adj = new Map();
    edges.forEach(e => {
      if (!adj.has(e.from)) adj.set(e.from, []);
      if (!adj.has(e.to)) adj.set(e.to, []);
      const a = nodeById.get(e.from), b = nodeById.get(e.to);
      const base = e.weight != null ? e.weight : euclid(a, b);
      adj.get(e.from).push({ nid: e.to, baseWeight: base, edge: e });
      adj.get(e.to).push({ nid: e.from, baseWeight: base, edge: e }); // undirected
    });

    // pick best goal dynamically
    let bestGoal = null;
    let bestPath = null;
    let bestCost = Infinity;

    for (const goalId of goalIds) {
      const open = new Set([startId]);
      const gScore = new Map([[startId, 0]]);
      const fScore = new Map([[startId, heuristic(nodeById.get(startId), nodeById.get(goalId))]]);
      const cameFrom = {};

      // Priority queue via array (small graphs) — OK for floors
      function lowestF() {
        let best = null, bestVal = Infinity;
        for (const id of open) {
          const v = fScore.get(id) ?? Infinity;
          if (v < bestVal) { bestVal = v; best = id; }
        }
        return best;
      }

      while (open.size) {
        const current = lowestF();
        if (current === goalId) {
          const path = reconstructPath(cameFrom, current);
          const cost = gScore.get(current);
          if (cost < bestCost) { bestCost = cost; bestGoal = goalId; bestPath = path; }
          break;
        }

        open.delete(current);
        const neighbors = adj.get(current) || [];
        for (const n of neighbors) {
          if (!nodeById.has(n.nid)) continue;

          // dynamic penalty (danger), or Infinity => block
          let penalty = 0;
          if (typeof costPenalty === 'function') {
            penalty = costPenalty(nodeById.get(current), nodeById.get(n.nid), n.edge);
            if (penalty === Infinity) continue; // edge blocked
          }
          const tentative = (gScore.get(current) ?? Infinity) + n.baseWeight + penalty;

          if (tentative < (gScore.get(n.nid) ?? Infinity)) {
            cameFrom[n.nid] = current;
            gScore.set(n.nid, tentative);
            const f = tentative + heuristic(nodeById.get(n.nid), nodeById.get(goalId));
            fScore.set(n.nid, f);
            open.add(n.nid);
          }
        }
      }
    }

    return bestPath ? { goal: bestGoal, cost: bestCost, path: bestPath } : null;
  }

  global.Pathfinding = { aStar, euclid };
})(window);
