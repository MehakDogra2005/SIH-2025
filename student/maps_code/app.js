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

  // ====== DATA YOU ACTUALLY HAVE ======
  // Map building/floor -> JSON filename (root-level files)
  const DATA_FILES = {
    'cse-ground': 'cse_ground.json',
    'cse-first' : 'cse_first.json'
    // Add more ONLY when you create them:
    // 'admin-ground': 'admin_ground.json',
    // 'admin-first' : 'admin_first.json',
    // 'it-ground'   : 'it_ground.json',  etc.
  };

  // Optional: traced background SVGs in /maps (shown faintly under the graph)
  const TRACE_MAP = {
    'cse-ground'  : 'maps/cse_ground_floor_trace.svg',
    'cse-first'   : 'maps/cse_first_floor_trace.svg',
    'admin-ground': 'maps/admin_ground_floor_trace.svg',
    'admin-first' : 'maps/admin_first_floor_trace.svg'
  };

  // ====== Helpers ======
  function keyFor(b, f) { return `${b}-${f}`; }
  function hasData(key) { return Object.prototype.hasOwnProperty.call(DATA_FILES, key); }
  function hasTrace(key){ return Object.prototype.hasOwnProperty.call(TRACE_MAP, key); }

  function titleize() {
    const bMap = { cse:'CSE Block', admin:'Admin Block', it:'IT Block', hostel:'Hostel Block' };
    const fMap = { ground:'Ground Floor', first:'First Floor', second:'Second Floor', third:'Third Floor' };
    mapTitle.textContent = `${bMap[selectedBuilding]} - ${fMap[selectedFloor]} Evacuation Map`;
  }

  function refreshFloorAvailability() {
    // Disable floor buttons that don't have data for the selected building
    floorBtns.forEach(btn => {
      const floor = btn.dataset.floor;
      const has = hasData(keyFor(selectedBuilding, floor));
      btn.disabled = !has;
      btn.title = has ? '' : 'Data not available yet';
      btn.classList.toggle('active', floor === selectedFloor);
    });

    // If current selection has no data, switch to an available floor (prefer ground)
    if (!hasData(keyFor(selectedBuilding, selectedFloor))) {
      if (hasData(keyFor(selectedBuilding, 'ground'))) {
        selectedFloor = 'ground';
      } else {
        const firstAvailable = Object.keys(DATA_FILES)
          .filter(k => k.startsWith(`${selectedBuilding}-`))
          .map(k => k.split('-')[1])[0];
        if (firstAvailable) selectedFloor = firstAvailable;
      }
    }
  }

  async function loadData() {
    const key = keyFor(selectedBuilding, selectedFloor);
    refreshFloorAvailability();
    titleize();

    dataset = null; // reset

    // Try to load JSON only if available
    if (hasData(key)) {
      const file = DATA_FILES[key];
      try {
        const res = await fetch(file);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        dataset = await res.json();
      } catch (err) {
        console.error('Failed to load JSON:', file, err);
        // Show a friendly note but still draw the background trace if any
        svgContainer.innerHTML = `<div style="padding:16px;color:#dc3545;">Could not load ${file}</div>`;
      }
    }

    drawSVG(); // draw whatever we have (trace + dataset layers)
  }

  function drawSVG() {
    svgContainer.innerHTML = '';
    locationInfo.style.display = 'none';
    selectedRoomId = null;

    const key = keyFor(selectedBuilding, selectedFloor);
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 600 400');
    svg.style.width = '100%';
    svg.style.height = '100%';

    // Background (light)
    svg.appendChild(rect(0,0,600,400,'#f8f9fa'));

    // Optional: traced map as background image (if present)
    if (hasTrace(key)) {
      const img = document.createElementNS('http://www.w3.org/2000/svg', 'image');
      img.setAttributeNS('http://www.w3.org/1999/xlink','href', TRACE_MAP[key]);
      img.setAttribute('x','0'); img.setAttribute('y','0');
      img.setAttribute('width','600'); img.setAttribute('height','400');
      img.setAttribute('opacity','0.35');           // faint background
      img.setAttribute('preserveAspectRatio','xMidYMid slice');
      img.setAttribute('pointer-events','none');    // let clicks go through
      svg.appendChild(img);
    }

    // If no dataset (no JSON for this floor), stop after background
    if (!dataset) {
      svgContainer.appendChild(svg);
      currentSVG = svg;
      return;
    }

    // Corridors (visual only)
    (dataset.corridors || []).forEach(poly => {
      const p = document.createElementNS('http://www.w3.org/2000/svg','polygon');
      p.setAttribute('points', poly.points.map(pt => `${pt.x},${pt.y}`).join(' '));
      p.setAttribute('fill', '#e9ecef');
      p.setAttribute('stroke', '#dee2e6');
      p.setAttribute('stroke-width', '1');
      svg.appendChild(p);
    });

    // Danger zones (affect routing via penalty function)
    (dataset.dangerZones || []).forEach(z => {
      const d = rect(z.x, z.y, z.width, z.height, null, 'danger-zone');
      d.dataset.dangerId = z.id;
      svg.appendChild(d);
    });

    // Exits (green)
    (dataset.nodes || []).filter(n => n.type === 'exit').forEach(n => {
      const c = circle(n.x, n.y, 10, 'exit-marker');
      svg.appendChild(c);
      const label = text(n.x, n.y - 14, n.label || n.id, '#fff', 'middle', 10);
      svg.appendChild(label);
    });

    // Rooms (blue, clickable)
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

    // Graph edges (subtle)
    (dataset.edges || []).forEach(e => {
      const a = dataset.nodes.find(n => n.id === e.from);
      const b = dataset.nodes.find(n => n.id === e.to);
      if (!a || !b) return;
      const line = document.createElementNS('http://www.w3.org/2000/svg','line');
      line.setAttribute('x1', a.x); line.setAttribute('y1', a.y);
      line.setAttribute('x2', b.x); line.setAttribute('y2', b.y);
      line.setAttribute('stroke', '#cfd8e3');
      line.setAttribute('stroke-width', '1.5');
      line.setAttribute('stroke-dasharray', '3,4');
      svg.appendChild(line);
    });

    svgContainer.appendChild(svg);
    currentSVG = svg;
  }

  // ====== Small SVG helpers ======
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

  // ====== UI events ======
  buildingTabs.forEach(tab => tab.addEventListener('click', () => {
    buildingTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    selectedBuilding = tab.dataset.building;
    refreshFloorAvailability();
    loadData();
  }));

  floorBtns.forEach(btn => btn.addEventListener('click', () => {
    if (btn.disabled) return; // ignore disabled floors
    floorBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedFloor = btn.dataset.floor;
    refreshFloorAvailability();
    loadData();
  }));

  resetMapBtn.addEventListener('click', () => {
    selectedRoomId = null;
    locationInfo.style.display = 'none';
    clearRoute();
    currentSVG?.querySelectorAll('.room-marker').forEach(r => r.classList.remove('selected'));
  });

  toggleDangerBtn.addEventListener('click', () => {
    fakeDangerActive = !fakeDangerActive;
    currentSVG?.querySelectorAll('.danger-zone').forEach(d => d.style.display = fakeDangerActive ? 'block' : 'none');
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

  // ====== Geometry & penalties ======
  function lineIntersectsRect(ax,ay,bx,by, rx,ry,rw,rh){
    const minX = rx, maxX = rx + rw, minY = ry, maxY = ry + rh;
    function between(a,b,c){ return (a >= Math.min(b,c) && a <= Math.max(b,c)); }
    if (Math.max(ax,bx) < minX || Math.min(ax,bx) > maxX || Math.max(ay,by) < minY || Math.min(ay,by) > maxY){
      const insideA = ax>minX && ax<maxX && ay>minY && ay<maxY;
      const insideB = bx>minX && bx<maxX && by>minY && by<maxY;
      return insideA || insideB ? true : false;
    }
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

  function makePenaltyFn(dangerZones) {
    return (a, b) => {
      const ax=a.x, ay=a.y, bx=b.x, by=b.y;
      let penalty = 0;
      for (const z of dangerZones || []) {
        if (!fakeDangerActive) break;
        const intersects = lineIntersectsRect(ax,ay,bx,by, z.x,z.y,z.width,z.height);
        if (intersects) {
          if (z.hard) return Infinity;
          penalty += 500;               // strong avoidance
        } else {
          // soft avoidance near zone
          const cx = Math.max(z.x, Math.min((ax+bx)/2, z.x+z.width));
          const cy = Math.max(z.y, Math.min((ay+by)/2, z.y+z.height));
          const dist = Math.hypot(((ax+bx)/2)-cx, ((ay+by)/2)-cy);
          if (dist < 25) penalty += (25 - dist) * 6;
        }
      }
      return penalty;
    };
  }

  // ====== A* action ======
  showRouteBtn.addEventListener('click', () => {
    if (!dataset) {
      alert('No map data loaded for this selection.');
      return;
    }
    if (!selectedRoomId) {
      alert('Please select a room by clicking a blue marker.');
      return;
    }
    const startId = selectedRoomId;
    const goals = dataset.nodes.filter(n => n.type === 'exit').map(n => n.id);
    const penaltyFn = makePenaltyFn(dataset.dangerZones);

    const result = Pathfinding.aStar({
      nodes: dataset.nodes,
      edges: dataset.edges,
      startId,
      goalIds: goals,
      heuristic: Pathfinding.euclid,
      costPenalty: penaltyFn
    });

    if (!result) {
      alert('No safe route found.');
      return;
    }

    // draw route
    clearRoute();
    const pts = result.path.map(id => {
      const n = dataset.nodes.find(nn => nn.id === id);
      return `${n.x},${n.y}`;
    }).join(' ');
    const pl = document.createElementNS('http://www.w3.org/2000/svg','polyline');
    pl.setAttribute('points', pts);
    pl.setAttribute('class','route-line');
    currentSVG.appendChild(pl);

    // info
    const start = dataset.nodes.find(n => n.id === startId);
    const goal  = dataset.nodes.find(n => n.id === result.goal);
    locationInfo.innerHTML =
      `<strong>🟡 Evacuation Route Active</strong><br>
       <strong>From:</strong> ${start.label || start.id}<br>
       <strong>To:</strong> ${goal.label || goal.id}<br>
       <small>Cost: ${result.cost.toFixed(0)} (lower is faster/safer)</small>`;
    locationInfo.style.display = 'block';
  });

  // ====== boot ======
  titleize();
  refreshFloorAvailability();
  loadData();
});


