{
  "nodes": [
    { "id": "lab101",   "label": "Lab 101",      "x": 120, "y": 120, "type": "room" },
    { "id": "faculty",  "label": "Faculty",      "x": 220, "y": 120, "type": "room" },
    { "id": "classA",   "label": "Class A",      "x": 120, "y": 220, "type": "room" },
    { "id": "server",   "label": "Server",       "x": 320, "y": 120, "type": "room" },
    { "id": "common",   "label": "Common Area",  "x": 320, "y": 220, "type": "room" },

    { "id": "c1", "x": 160, "y": 160, "type": "junction" },
    { "id": "c2", "x": 240, "y": 160, "type": "junction" },
    { "id": "c3", "x": 320, "y": 160, "type": "junction" },
    { "id": "c4", "x": 400, "y": 160, "type": "junction" },
    { "id": "c5", "x": 160, "y": 240, "type": "junction" },
    { "id": "c6", "x": 240, "y": 240, "type": "junction" },
    { "id": "c7", "x": 320, "y": 240, "type": "junction" },
    { "id": "c8", "x": 400, "y": 240, "type": "junction" },

    { "id": "exitW", "label": "Exit W", "x": 60,  "y": 200, "type": "exit" },
    { "id": "exitN", "label": "Exit N", "x": 300, "y": 60,  "type": "exit" },
    { "id": "exitE", "label": "Exit E", "x": 540, "y": 200, "type": "exit" }
  ],

  "edges": [
    { "from": "lab101", "to": "c1" },
    { "from": "faculty","to": "c2" },
    { "from": "server", "to": "c3" },
    { "from": "classA", "to": "c5" },
    { "from": "common", "to": "c7" },

    { "from": "c1", "to": "c2" },
    { "from": "c2", "to": "c3" },
    { "from": "c3", "to": "c4" },
    { "from": "c5", "to": "c6" },
    { "from": "c6", "to": "c7" },
    { "from": "c7", "to": "c8" },
    { "from": "c1", "to": "c5" },
    { "from": "c2", "to": "c6" },
    { "from": "c3", "to": "c7" },
    { "from": "c4", "to": "c8" },

    { "from": "exitW", "to": "c5" },
    { "from": "exitN", "to": "c2" },
    { "from": "exitE", "to": "c8" }
  ],

  "corridors": [
    { "id": "north", "points": [ { "x":120,"y":150 }, { "x":420,"y":150 }, { "x":420,"y":170 }, { "x":120,"y":170 } ] },
    { "id": "south", "points": [ { "x":120,"y":230 }, { "x":420,"y":230 }, { "x":420,"y":250 }, { "x":120,"y":250 } ] },
    { "id": "west",  "points": [ { "x":150,"y":150 }, { "x":170,"y":150 }, { "x":170,"y":250 }, { "x":150,"y":250 } ] },
    { "id": "east",  "points": [ { "x":310,"y":150 }, { "x":330,"y":150 }, { "x":330,"y":250 }, { "x":310,"y":250 } ] }
  ],

  "dangerZones": [
    { "id": "fire1", "x": 210, "y": 135, "width": 40, "height": 40, "hard": false },
    { "id": "collapseA", "x": 345, "y": 175, "width": 50, "height": 40, "hard": true }
  ]
}
