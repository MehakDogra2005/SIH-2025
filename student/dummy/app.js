// js/app.js
document.addEventListener('DOMContentLoaded', () => {
  const buildingTabs = document.getElementById('buildingTabs').querySelectorAll('.building-tab');
  const floorBtns = document.getElementById('floorSelector').querySelectorAll('.floor-btn');
  const showRouteBtn = document.getElementById('showRoute');
  const resetMapBtn = document.getElementById('resetMap');
  const toggleDangerBtn = document.getElementById('toggleDanger');
  const mapTitle = document.getElementById('mapTitle');
  const svgContainer = document.getElementById('svg-container');
  const locationInfo = document.getElementById('locationInfo');

  let selectedBuilding = 'cse';
  let selectedFloor = 'ground';
  let dataset = null;
  let currentSVG = null;
  let selectedRoomId = null;
  let fakeDangerActive = true; // toggle demo

  function titleize() {
    const bMap = { cse:'CSE Block', admin:'Admin Block', it:'IT Block', hostel:'Hostel Block' };
    const fMap = { ground:'Ground Floor', first:'First Floor', second:'Second Floor', third:'Third Floor' };
    mapTitle.textContent = `${bMap[selectedBuilding]} - ${fMap[selectedFloor]} Evacuation Map`;
  }

  async function loadData() {
    const key = `${selectedBuilding}-${selectedFloor}`;
    // For demo we only ship cse-ground.json; fallback to it for other floors
    const url = `data/${selectedBuilding}-${selectedFloor}.json`.replace('-', '-');
    const safeUrl = (selectedBuilding === 'cse' && selectedFloor === 'ground')
      ? 'data/cse-ground.json'
      : 'data/cse-ground.json';
    try {
      const res = await fetch(url);
      dataset = await res.json();
    } catch {
      const res = await fetch(safeUrl);
      dataset = await res.json();
    }
    drawSVG();
  }

  function drawSVG() {
    svgContainer.innerHTML = '';
    locationInfo.style.display = 'none';
    selectedRoomId = null;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 600 400');
    svg.style.width = '100%';
    svg.style.height = '100%';

    // background
    const bg = rect(0,0,600,400,'#f8f9fa');
    svg.appendChild(bg);

    // corridors (light grey polygons)
    (dataset.corridors || []).forEach(poly => {
      const p = document.createElementNS('http://www.w3.org/2000/svg','polygon');
      p.setAttribute('points', poly.points.map(pt => `${pt.x},${pt.y}`).join(' '));
      p.setAttribute('fill', '#e9ecef');
      p.setAttribute('stroke', '#dee2e6');
      p.setAttribute('stroke-width', '1');
      svg.appendChild(p);
    });

    // danger zones (red rectangles)
    (dataset.dangerZones || []).forEach(z => {
      const d = rect(z.x, z.y, z.width, z.height, null, 'danger-zone');
      d.dataset.dangerId = z.id;
      svg.appendChild(d);
    });

    // exits (green circles)
    (dataset.nodes || []).filter(n => n.type === 'exit').forEach(n => {
      const c = circle(n.x, n.y, 10, 'exit-marker');
      svg.appendChild(c);
      const label = text(n.x, n.y - 14, n.label || n.id, '#fff', 'middle', 10);
      svg.appendChild(label);
    });

    // rooms (blue circles, clickable start points)
    (dataset.nodes || []).filter(n => n.type === 'room').forEach(n => {
      const c = circle(n.x, n.y, 8, 'room-marker');
      c.dataset.roomId = n.id;
      c.addEventListener('click', () => {
        svg.querySelectorAll('.room-marker').forEach(r => r.classList.remove('selected'));
        c.classList.add('selected');
        selectedRoomId = n.id;
        showInfo(`${n.label || n.id} Selected<br><small>Click "Show Evacuation Route" to see the path</small>`, n.x, n.y);
        clearRoute();
      });
      svg.appendChild(c);
      const label = text(n.x, n.y - 14, n.label || n.id, '#333', 'middle', 10);
      svg.appendChild(label);
    });

    // edges (optional, subtle)
    (dataset.edges || []).forEach(e => {
      const a = dataset.nodes.find(n => n.id === e.from);
      const b = dataset.nodes.find(n => n.id === e.to);
      if (!a || !b) return;
      const line = document.createElementNS('http://www.w3.org/2000/svg','line');
      line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
      line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
      line.setAttribute('stroke', '#cfd8e3'); line.setAttribute('stroke-width', '1.5');
      line.setAttribute('stroke-dasharray', '3,4');
      svg.appendChild(line);
    });

    svgContainer.appendChild(svg);
    currentSVG = svg;
  }

  function rect(x,y,w,h,fill,className){
    const r = document.createElementNS('http://www.w3.org/2000/svg','rect');
    r.setAttribute('x',x); r.setAttribute('y',y);
    r.setAttribute('width',w); r.setAttribute('height',h);
    if (fill) r.setAttribute('fill',fill);
    if (className) r.setAttribute('class',className);
    return r;
  }
  function circle(x,y,r,className){
    const c = document.createElementNS('http://www.w3.org/2000/svg','circle');
    c.setAttribute('cx',x); c.setAttribute('cy',y); c.setAttribute('r',r);
    if (className) c.setAttribute('class',className);
    return c;
  }
  function text(x,y,content,fill='#333',anchor='start',size=10){
    const t = document.createElementNS('http://www.w3.org/2000/svg','text');
    t.setAttribute('x',x); t.setAttribute('y',y);
    t.setAttribute('text-anchor',anchor);
    t.setAttribute('font-size',size);
    t.setAttribute('fill',fill);
    t.textContent = content;
    return t;
  }

  // UI events
  buildingTabs.forEach(tab => tab.addEventListener('click', () => {
    buildingTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    selectedBuilding = tab.dataset.building;
    titleize(); loadData();
  }));

  floorBtns.forEach(btn => btn.addEventListener('click', () => {
    floorBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedFloor = btn.dataset.floor;
    titleize(); loadData();
  }));

  resetMapBtn.addEventListener('click', () => {
    selectedRoomId = null;
    locationInfo.style.display = 'none';
    clearRoute();
    currentSVG?.querySelectorAll('.room-marker').forEach(r => r.classList.remove('selected'));
  });

  toggleDangerBtn.addEventListener('click', () => {
    // demo: toggle visibility of danger zones (still affects routing because penalty function reads dataset)
    fakeDangerActive = !fakeDangerActive;
    currentSVG.querySelectorAll('.danger-zone').forEach(d => d.style.display = fakeDangerActive ? 'block' : 'none');
  });

  function showInfo(html, x, y) {
    locationInfo.innerHTML = `<strong>${html}</strong>`;
    locationInfo.style.left = `${Math.min(560, Math.max(20, x + 10))}px`;
    locationInfo.style.top  = `${Math.min(360, Math.max(20, y + 10))}px`;
    locationInfo.style.display = 'block';
  }

  function clearRoute(){
    currentSVG?.querySelectorAll('.route-line').forEach(e => e.remove());
  }

  // geometry: line segment AB vs rectangle (axis-aligned)
  function lineIntersectsRect(ax,ay,bx,by, rx,ry,rw,rh){
    const minX = rx, maxX = rx + rw, minY = ry, maxY = ry + rh;

    function between(a,b,c){ return (a >= Math.min(b,c) && a <= Math.max(b,c)); }
    // quick reject
    if (Math.max(ax,bx) < minX || Math.min(ax,bx) > maxX || Math.max(ay,by) < minY || Math.min(ay,by) > maxY){
      // could still be inside rect entirely:
      const insideA = ax>minX && ax<maxX && ay>minY && ay<maxY;
      const insideB = bx>minX && bx<maxX && by>minY && by<maxY;
      return insideA || insideB ? true : false;
    }
    // check intersection with each side
    const edges = [
      {x1:minX,y1:minY,x2:maxX,y2:minY},
      {x1:maxX,y1:minY,x2:maxX,y2:maxY},
      {x1:maxX,y1:maxY,x2:minX,y2:maxY},
      {x1:minX,y1:maxY,x2:minX,y2:minY}
    ];
    function segIntersect(x1,y1,x2,y2,x3,y3,x4,y4){
      const d=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4);
      if (d===0) return false;
      const xi=((x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4))/d;
      const yi=((x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4))/d;
      return between(xi,x1,x2) && between(xi,x3,x4) && between(yi,y1,y2) && between(yi,y3,y4);
    }
    return edges.some(e => segIntersect(ax,ay,bx,by,e.x1,e.y1,e.x2,e.y2));
  }

  // Cost penalty based on danger zones (Infinity blocks, else adds cost)
  function makePenaltyFn(dangerZones) {
    return (a, b, edge) => {
      const ax=a.x, ay=a.y, bx=b.x, by=b.y;
      let penalty = 0;
      for (const z of dangerZones) {
        if (!fakeDangerActive) break;
        const intersects = lineIntersectsRect(ax,ay,bx,by, z.x,z.y,z.width,z.height);
        if (intersects) {
          // If an edge crosses a danger zone we heavily penalize it.
          // If the zone is marked "hard", block entirely.
          if (z.hard) return Infinity;
          penalty += 500; // big penalty so A* prefers other routes
        } else {
          // near miss: if either endpoint is very close to a zone, add soft penalty
          const cx = Math.max(z.x, Math.min((ax+bx)/2, z.x+z.width));
          const cy = Math.max(z.y, Math.min((ay+by)/2, z.y+z.height));
          const dist = Math.hypot(((ax+bx)/2)-cx, ((ay+by)/2)-cy);
          if (dist < 25) penalty += (25 - dist) * 6; // gentle gradient
        }
      }
      return penalty;
    };
  }

  // Draw the A* result as a yellow dashed polyline
  function drawRoute(ids) {
    clearRoute();
    const pts = ids.map(id => {
      const n = dataset.nodes.find(nn => nn.id === id);
      return `${n.x},${n.y}`;
    }).join(' ');
    const pl = document.createElementNS('http://www.w3.org/2000/svg','polyline');
    pl.setAttribute('points', pts);
    pl.setAttribute('class','route-line');
    currentSVG.appendChild(pl);
  }

  // Find path button
  showRouteBtn.addEventListener('click', () => {
    if (!selectedRoomId) {
      alert('Please select a room by clicking a blue marker.');
      return;
    }
    const startId = selectedRoomId;
    const goals = dataset.nodes.filter(n => n.type === 'exit').map(n => n.id);
    const penaltyFn = makePenaltyFn(dataset.dangerZones || []);
    const result = Pathfinding.aStar({
      nodes: dataset.nodes,
      edges: dataset.edges,
      startId: startId,
      goalIds: goals,
      heuristic: Pathfinding.euclid,
      costPenalty: penaltyFn
    });

    if (!result) {
      alert('No safe route found.');
      return;
    }

    drawRoute(result.path);

    const start = dataset.nodes.find(n => n.id === startId);
    const goal  = dataset.nodes.find(n => n.id === result.goal);
    locationInfo.innerHTML =
      `<strong>🟡 Evacuation Route Active</strong><br>
       <strong>From:</strong> ${start.label || start.id}<br>
       <strong>To:</strong> ${goal.label || goal.id}<br>
       <small>Cost: ${result.cost.toFixed(0)} (lower is faster/safer)</small>`;
    locationInfo.style.display = 'block';
  });

  // kick off
  titleize();
  loadData();
});
