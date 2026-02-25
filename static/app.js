const TERRAIN_EMOJI = {
  'field':          '\u{1F33E}',
  'field+crop':     '\u{1F33D}',
  'forest':         '\u{1F332}',
  'mountain':       '\u{26F0}\uFE0F',
  'mountain+metal': '\u{26CF}\uFE0F',
  'water':          '\u{1F30A}',
  'ocean':          '\u{1F310}',
  'empty':          '',
};

const TERRAIN_CLASS = {
  'field':          'terrain-field',
  'field+crop':     'terrain-field-crop',
  'forest':         'terrain-forest',
  'mountain':       'terrain-mountain',
  'mountain+metal': 'terrain-metal',
  'water':          'terrain-water',
  'ocean':          'terrain-ocean',
  'empty':          '',
};

const BUILDING_ABBR = {
  sawmill:     'SAW',
  windmill:    'WIN',
  forge:       'FRG',
  market:      'MKT',
  lumber_hut:  'LH',
  farm:        'FM',
  mine:        'MN',
};

let state = {
  rows: 10,
  cols: 10,
  tiles: {},     // "r,c" -> terrain string
  cities: [],    // {id, row, col, expanded}
  pinned: {},    // "r,c" -> building name
  excluded: [],  // building names excluded from solver
};

let activeTool = null;
let isMouseDown = false;
let resultPlacements = {};  // "r,c" -> building string
let resultMarkets = [];     // [{row, col, city_id, income}]
let resultBurns = {};       // "r,c" -> true
let nextCityId = 1;

// --- Grid rendering ---

function renderGrid() {
  const grid = document.getElementById('grid');
  grid.style.gridTemplateColumns = `repeat(${state.cols}, 36px)`;
  grid.innerHTML = '';

  // Margin to accommodate 45° rotation overhang: (√2 - 1)/2 ≈ 0.21 of grid size
  const tileSize = 37; // 36px tile + 1px gap
  const overhangV = Math.ceil(state.cols * tileSize * 0.21);
  const overhangH = Math.ceil(state.rows * tileSize * 0.21);
  grid.style.margin = `${overhangV}px ${overhangH}px`;

  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const key = `${r},${c}`;
      const terrain = state.tiles[key] || 'empty';
      const div = document.createElement('div');
      div.className = `tile ${TERRAIN_CLASS[terrain] || ''}`;
      div.dataset.r = r;
      div.dataset.c = c;

      // Content wrapper (counter-rotated so text stays upright)
      const content = document.createElement('div');
      content.className = 'tile-content';

      // Terrain emoji (skip for colour-only terrains)
      const DEAD_TERRAIN = new Set(['field', 'mountain', 'water', 'ocean']);
      if (terrain !== 'empty' && !DEAD_TERRAIN.has(terrain)) {
        content.textContent = TERRAIN_EMOJI[terrain] || '';
      }

      // City marker
      const city = state.cities.find(ct => ct.row === r && ct.col === c);
      if (city) {
        const marker = document.createElement('span');
        marker.className = 'city-marker';
        marker.textContent = `C${city.id}${city.expanded ? '+' : ''}`;
        marker.title = 'Right-click to toggle expansion';
        content.appendChild(marker);
      }

      // Pinned building icon
      const pinnedBldg = state.pinned[key];
      if (pinnedBldg) {
        const pin = document.createElement('span');
        pin.className = 'pinned-icon';
        pin.textContent = BUILDING_ABBR[pinnedBldg] || pinnedBldg;
        content.appendChild(pin);
      }

      // Result icon
      const bldg = resultPlacements[key];
      if (bldg) {
        const icon = document.createElement('span');
        icon.className = 'result-icon';
        icon.textContent = BUILDING_ABBR[bldg] || bldg;
        content.appendChild(icon);
      }

      // Burn indicator
      if (resultBurns[key]) {
        const burn = document.createElement('span');
        burn.className = 'burn-icon';
        burn.textContent = 'BURN';
        content.appendChild(burn);
      }

      div.appendChild(content);

      div.addEventListener('mousedown', onTileMouseDown);
      div.addEventListener('mouseenter', onTileMouseEnter);
      div.addEventListener('contextmenu', onTileRightClick);
      grid.appendChild(div);
    }
  }
}

// --- Tile interaction ---

function applyTool(r, c) {
  const key = `${r},${c}`;
  if (activeTool === 'city') {
    const existingIdx = state.cities.findIndex(ct => ct.row === r && ct.col === c);
    if (existingIdx >= 0) {
      state.cities.splice(existingIdx, 1);
    } else {
      state.cities.push({ id: nextCityId++, row: r, col: c, expanded: false });
    }
  } else if (activeTool === 'empty') {
    delete state.tiles[key];
    delete state.pinned[key];
  } else if (activeTool && activeTool.startsWith('pin-')) {
    const building = activeTool.slice(4);
    if (state.pinned[key] === building) {
      delete state.pinned[key];
    } else {
      state.pinned[key] = building;
    }
  } else if (activeTool) {
    state.tiles[key] = activeTool;
  }
  renderGrid();
}

function onTileMouseDown(e) {
  if (e.button !== 0) return;
  isMouseDown = true;
  const r = +e.currentTarget.dataset.r;
  const c = +e.currentTarget.dataset.c;
  applyTool(r, c);
}

function onTileMouseEnter(e) {
  if (!isMouseDown) return;
  if (activeTool === 'city') return;  // don't drag-place cities
  if (activeTool && activeTool.startsWith('pin-')) return;  // don't drag-place buildings
  const r = +e.currentTarget.dataset.r;
  const c = +e.currentTarget.dataset.c;
  applyTool(r, c);
  document.getElementById('hover-info').textContent = `(${r}, ${c})`;
}

function onTileRightClick(e) {
  e.preventDefault();
  const r = +e.currentTarget.dataset.r;
  const c = +e.currentTarget.dataset.c;
  const city = state.cities.find(ct => ct.row === r && ct.col === c);
  if (city) {
    city.expanded = !city.expanded;
    renderGrid();
  }
}

document.addEventListener('mouseup', () => { isMouseDown = false; });

// --- Toolbar ---

document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
  btn.addEventListener('click', () => {
    activeTool = btn.dataset.tool;
    document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('active-tool-label').textContent = activeTool;
  });
});

// --- Building toggles ---

function updateBuildingToggles() {
  document.querySelectorAll('.building-toggle').forEach(cb => {
    const building = cb.dataset.building;
    const excluded = state.excluded.includes(building);
    cb.checked = !excluded;
    const btn = cb.parentElement.querySelector('.tool-btn');
    btn.disabled = excluded;
    if (excluded && activeTool === btn.dataset.tool) {
      activeTool = null;
      document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
      document.getElementById('active-tool-label').textContent = 'none';
    }
  });
}

document.querySelectorAll('.building-toggle').forEach(cb => {
  cb.addEventListener('change', () => {
    const building = cb.dataset.building;
    if (cb.checked) {
      state.excluded = state.excluded.filter(b => b !== building);
    } else {
      if (!state.excluded.includes(building)) {
        state.excluded.push(building);
      }
    }
    updateBuildingToggles();
  });
});

// --- Optimise ---

document.getElementById('btn-optimise').addEventListener('click', async () => {
  const tilesArr = Object.entries(state.tiles).map(([key, terrain]) => {
    const [r, c] = key.split(',').map(Number);
    return { row: r, col: c, terrain };
  });
  const pinnedArr = Object.entries(state.pinned).map(([key, building]) => {
    const [r, c] = key.split(',').map(Number);
    return { row: r, col: c, building };
  });
  const payload = { tiles: tilesArr, cities: state.cities, pinned: pinnedArr, excluded: state.excluded };

  const resp = await fetch('/optimize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const result = await resp.json();

  resultPlacements = {};
  for (const p of result.placements) {
    resultPlacements[`${p.row},${p.col}`] = p.building;
  }
  resultMarkets = result.markets;
  resultBurns = {};
  for (const b of (result.burns || [])) {
    resultBurns[`${b.row},${b.col}`] = true;
  }

  const summary = result.markets
    .map(m => `City ${m.city_id}: ${m.income}/turn`)
    .join(' | ');
  document.getElementById('summary').textContent =
    `Total: ${result.total_income}/turn  |  ${summary}`;

  renderGrid();
});

// --- Clear result ---

document.getElementById('btn-clear-result').addEventListener('click', () => {
  resultPlacements = {};
  resultMarkets = [];
  resultBurns = {};
  document.getElementById('summary').textContent = 'No optimisation run yet.';
  renderGrid();
});

// --- Save / Load ---

document.getElementById('btn-save').addEventListener('click', () => {
  const json = JSON.stringify(state, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'polytopia-game.json';
  a.click();
});

document.getElementById('btn-load').addEventListener('click', () => {
  document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    try {
      state = JSON.parse(ev.target.result);
      if (!state.pinned) state.pinned = {};
      if (!state.excluded) state.excluded = [];
      nextCityId = (state.cities.reduce((m, c) => Math.max(m, c.id), 0)) + 1;
      resultPlacements = {};
      resultMarkets = [];
      updateBuildingToggles();
      renderGrid();
    } catch {
      alert('Invalid JSON file');
    }
  };
  reader.readAsText(file);
});

// --- Resize ---

document.getElementById('btn-resize').addEventListener('click', () => {
  state.rows = +document.getElementById('rows-input').value;
  state.cols = +document.getElementById('cols-input').value;
  renderGrid();
});

// --- Init ---

renderGrid();
updateBuildingToggles();
