<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pull Your Human Design Chart</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
<style>
  :root {
    --teal: #3D7A7A;
    --teal-light: #A8C8D8;
    --sage: #A8B89A;
    --linen: #F0EDE8;
    --linen-dark: #E5E0D8;
    --text-dark: #2C3E35;
    --text-mid: #5A6B5E;
    --white: #FFFFFF;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Lato', sans-serif;
    background: var(--linen);
    color: var(--text-dark);
    min-height: 100vh;
  }

  .page-wrap { max-width: 960px; margin: 0 auto; padding: 40px 24px 60px; }

  .intro { text-align: center; margin-bottom: 40px; }
  .intro h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    color: var(--teal);
    margin-bottom: 8px;
    line-height: 1.2;
  }
  .intro p { color: var(--text-mid); font-size: 1rem; font-weight: 300; }

  .form-card {
    background: var(--white);
    border-radius: 16px;
    padding: 36px 40px;
    box-shadow: 0 4px 24px rgba(61,122,122,0.08);
    margin-bottom: 40px;
  }

  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group.full { grid-column: 1 / -1; }

  label {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--teal);
  }

  input, select {
    padding: 12px 16px;
    border: 1.5px solid var(--linen-dark);
    border-radius: 8px;
    font-family: 'Lato', sans-serif;
    font-size: 0.95rem;
    color: var(--text-dark);
    background: var(--linen);
    transition: border-color 0.2s;
    -webkit-appearance: none;
    appearance: none;
  }
  input:focus, select:focus { outline: none; border-color: var(--teal); background: var(--white); }

  .time-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

  .btn-primary {
    width: 100%;
    margin-top: 24px;
    padding: 16px;
    background: var(--teal);
    color: var(--white);
    border: none;
    border-radius: 10px;
    font-family: 'Lato', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    cursor: pointer;
    transition: background 0.2s;
  }
  .btn-primary:hover { background: #2d6060; }
  .btn-primary:disabled { background: var(--teal-light); cursor: not-allowed; }

  .loading {
    display: none;
    text-align: center;
    padding: 60px 0;
    color: var(--teal);
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.2rem;
  }
  .spinner {
    width: 40px; height: 40px;
    border: 3px solid var(--teal-light);
    border-top-color: var(--teal);
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
    margin: 0 auto 16px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  #result { display: none; }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 12px;
  }
  .result-header h2 { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: var(--teal); }

  .btn-download {
    padding: 10px 22px;
    background: transparent;
    border: 2px solid var(--teal);
    border-radius: 8px;
    color: var(--teal);
    font-family: 'Lato', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
  }
  .btn-download:hover { background: var(--teal); color: var(--white); }

  .btn-reset {
    padding: 10px 22px;
    background: transparent;
    border: 2px solid var(--linen-dark);
    border-radius: 8px;
    color: var(--text-mid);
    font-family: 'Lato', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
  }

  .chart-layout {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 28px;
    align-items: start;
  }

  .bodygraph-wrap {
    background: var(--white);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 24px rgba(61,122,122,0.08);
  }

  .chart-name { font-family: 'Playfair Display', serif; font-size: 1.1rem; color: var(--teal); text-align: center; margin-bottom: 4px; }
  .chart-birthinfo { font-size: 0.78rem; color: var(--text-mid); text-align: center; margin-bottom: 16px; }

  #bodygraph-svg { width: 100%; height: auto; display: block; }

  .summary-panel { display: flex; flex-direction: column; gap: 16px; }

  .summary-card, .gates-card {
    background: var(--white);
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 4px 24px rgba(61,122,122,0.08);
  }

  .summary-card h3, .gates-card h3 {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: var(--teal);
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1.5px solid var(--linen-dark);
  }

  .summary-item { margin-bottom: 14px; padding-bottom: 14px; border-bottom: 1px solid var(--linen); }
  .summary-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
  .summary-label { font-size: 0.72rem; font-weight: 400; text-transform: none; letter-spacing: 0; color: var(--text-mid); margin-bottom: 3px; line-height: 1.4; }
  .summary-title { font-family: 'Playfair Display', serif; font-size: 1rem; color: var(--text-dark); font-weight: 600; margin-bottom: 2px; }
  .summary-desc { font-size: 0.8rem; color: var(--text-mid); line-height: 1.5; font-weight: 300; }

  .gate-rows { display: flex; flex-direction: column; gap: 7px; }
  .gate-row { display: flex; align-items: baseline; gap: 8px; }
  .gate-planet { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-mid); min-width: 62px; }
  .gate-num { font-family: 'Playfair Display', serif; font-size: 0.95rem; font-weight: 600; min-width: 32px; }
  .gate-name { font-size: 0.73rem; color: var(--text-mid); font-weight: 300; flex: 1; }
  .gate-section-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--sage); margin-top: 10px; margin-bottom: 4px; }

  /* City autocomplete */
  .autocomplete-wrap { position: relative; }
  .autocomplete-list {
    position: absolute;
    top: 100%;
    left: 0; right: 0;
    background: var(--white);
    border: 1.5px solid var(--teal);
    border-radius: 8px;
    margin-top: 4px;
    z-index: 100;
    box-shadow: 0 8px 24px rgba(61,122,122,0.12);
    max-height: 220px;
    overflow-y: auto;
  }
  .autocomplete-item {
    padding: 10px 16px;
    font-size: 0.88rem;
    color: var(--text-dark);
    cursor: pointer;
    border-bottom: 1px solid var(--linen);
    line-height: 1.4;
  }
  .autocomplete-item:last-child { border-bottom: none; }
  .autocomplete-item:hover { background: var(--linen); color: var(--teal); }
  .autocomplete-item .city-main { font-weight: 700; }
  .autocomplete-item .city-sub { font-size: 0.75rem; color: var(--text-mid); }

  .error-msg {
    display: none;
    background: #FEF0EE;
    border: 1.5px solid #F0A090;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #8B3A2A;
    margin-top: 16px;
    line-height: 1.5;
  }

  .disclaimer { font-size: 0.72rem; color: var(--text-mid); text-align: center; margin-top: 32px; font-weight: 300; line-height: 1.5; }

  @media (max-width: 700px) {
    .chart-layout { grid-template-columns: 1fr; }
    .form-grid { grid-template-columns: 1fr; }
    .form-card { padding: 24px 20px; }
    .intro h1 { font-size: 1.6rem; }
    .page-wrap { padding: 24px 16px 48px; }
  }
</style>
</head>
<body>
<div class="page-wrap">

  <div class="intro">
    <h1>Pull Your Human Design Chart</h1>
    <p>Enter your birth details to generate your personalized chart</p>
  </div>

  <div class="form-card" id="form-section">
    <div class="form-grid">
      <div class="form-group full">
        <label for="name">Your Name</label>
        <input type="text" id="name" placeholder="First name or full name" />
      </div>
      <div class="form-group">
        <label for="birth-year">Birth Year</label>
        <select id="birth-year"></select>
      </div>
      <div class="form-group">
        <label for="birth-month">Birth Month</label>
        <select id="birth-month">
          <option value="">Select month</option>
          <option value="1">January</option><option value="2">February</option>
          <option value="3">March</option><option value="4">April</option>
          <option value="5">May</option><option value="6">June</option>
          <option value="7">July</option><option value="8">August</option>
          <option value="9">September</option><option value="10">October</option>
          <option value="11">November</option><option value="12">December</option>
        </select>
      </div>
      <div class="form-group">
        <label for="birth-day">Birth Day</label>
        <select id="birth-day"></select>
      </div>
      <div class="form-group">
        <label>Birth Time <span style="font-weight:300;text-transform:none;letter-spacing:0">(24hr clock)</span></label>
        <div class="time-row">
          <select id="birth-hour"></select>
          <select id="birth-minute"></select>
        </div>
      </div>
      <div class="form-group full">
        <label for="birth-place">Birth City</label>
        <div class="autocomplete-wrap">
          <input type="text" id="birth-place" placeholder="Start typing your birth city..." autocomplete="off" oninput="cityAutocomplete(this.value)" />
          <div class="autocomplete-list" id="autocomplete-list" style="display:none"></div>
        </div>
        <input type="hidden" id="birth-place-full" />
      </div>
    </div>
    <div class="error-msg" id="error-msg"></div>
    <button class="btn-primary" id="submit-btn" onclick="generateChart()">View Your Chart</button>
  </div>

  <div class="loading" id="loading">
    <div class="spinner"></div>
    Calculating your chart...
  </div>

  <div id="result">
    <div class="result-header">
      <h2 id="result-title">Your Human Design Chart</h2>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button class="btn-reset" onclick="resetForm()">← New Chart</button>
        <button class="btn-download" onclick="downloadChart()">↓ Download Chart</button>
      </div>
    </div>
    <div class="chart-layout">
      <div class="bodygraph-wrap">
        <div class="chart-name" id="chart-name"></div>
        <div class="chart-birthinfo" id="chart-birthinfo"></div>
        <svg id="bodygraph-svg" viewBox="0 0 400 550" xmlns="http://www.w3.org/2000/svg"></svg>
      </div>
      <div class="summary-panel">
        <div class="summary-card">
          <h3>Your Chart Summary</h3>
          <div id="summary-items"></div>
        </div>

      </div>
    </div>
    <p class="disclaimer">Birth time accuracy affects your chart. If unsure of your exact time, try a few variations to see how your chart shifts.</p>
  </div>

</div>

<script>
// ─────────────────────────────────────────────────────────────────
// IMPORTANT: Replace this URL with your Railway API URL after deploy
// ─────────────────────────────────────────────────────────────────
const API_URL = "https://hd-chart-production.up.railway.app";

// ── Bodygraph rendering constants ──────────────────────────────────
const CENTER_POSITIONS = {
  HEAD:   { x: 200, y: 40,  w: 68,  h: 50,  shape: 'triangle-up' },
  AJNA:   { x: 200, y: 114, w: 68,  h: 50,  shape: 'triangle-down' },
  THROAT: { x: 200, y: 190, w: 88,  h: 36,  shape: 'rect' },
  G:      { x: 200, y: 266, w: 58,  h: 58,  shape: 'diamond' },
  SACRAL: { x: 200, y: 364, w: 88,  h: 36,  shape: 'rect' },
  EGO:    { x: 270, y: 248, w: 44,  h: 44,  shape: 'diamond' },
  SPLEEN: { x: 128, y: 294, w: 44,  h: 44,  shape: 'diamond' },
  SOLAR:  { x: 272, y: 320, w: 44,  h: 44,  shape: 'diamond' },
  ROOT:   { x: 200, y: 434, w: 88,  h: 36,  shape: 'rect' }
};

const CHANNELS = [
  [1,8],[2,14],[3,60],[4,63],[5,15],[6,59],[7,31],[9,52],[10,20],[11,56],
  [12,22],[13,33],[16,48],[17,62],[18,58],[19,49],[20,34],[20,57],[21,45],
  [23,43],[24,61],[25,51],[26,44],[27,50],[28,38],[29,46],[30,41],[32,54],
  [33,13],[34,57],[35,36],[37,40],[39,55],[42,53],[43,23],[44,26],[45,21],
  [46,29],[47,64],[48,16],[49,19],[50,27],[51,25],[52,9],[53,42],[54,32],
  [55,39],[56,11],[57,20],[58,18],[59,6],[60,3],[61,24],[62,17],[63,4],[64,47]
];

const CENTER_GATES = {
  HEAD:   [64,61,63],
  AJNA:   [47,24,4,17,43,11],
  THROAT: [62,23,56,35,12,45,33,8,31,20,16],
  G:      [7,1,13,10,25,15,46,2],
  SACRAL: [5,14,29,59,9,3,42,27,34],
  EGO:    [21,40,26,51],
  SPLEEN: [48,57,44,50,32,28,18],
  SOLAR:  [30,55,49,37,22,36,6],
  ROOT:   [60,52,19,39,53,54,58,38,41]
};

const GATE_NAMES = {
  1:"Self-Expression",2:"Receptivity",3:"Ordering",4:"Formulization",5:"Fixed Rhythms",
  6:"Friction",7:"The Role of the Self",8:"Contribution",9:"Focus",10:"Behavior of the Self",
  11:"Ideas",12:"Caution",13:"The Listener",14:"Power Skills",15:"Modesty",16:"Skills",
  17:"Following",18:"Correction",19:"Wanting",20:"The Now",21:"Biting Through",22:"Openness",
  23:"Assimilation",24:"Rationalization",25:"Innocence",26:"The Trickster",27:"Caring",
  28:"The Game Player",29:"Perseverance",30:"Recognition of Feelings",31:"Leading",
  32:"Continuity",33:"Privacy",34:"Power",35:"Change",36:"Crisis",37:"Friendship",
  38:"Opposition",39:"Provocation",40:"Aloneness",41:"Contraction",42:"Growth",43:"Insight",
  44:"Coming to Meet",45:"Gathering Together",46:"Pushing Upward",47:"Realization",
  48:"The Well",49:"Revolution",50:"Values",51:"The Arousing",52:"Stillness",53:"Beginnings",
  54:"Ambition",55:"Abundance",56:"Stimulation",57:"The Gentle",58:"Vitality",59:"Sexuality",
  60:"Acceptance",61:"Mystery",62:"Preponderance of the Small",63:"Doubt",64:"Confusion"
};

const GATE_POSITIONS = {
  64:{x:170,y:22}, 61:{x:200,y:16}, 63:{x:230,y:22},
  47:{x:165,y:92}, 24:{x:200,y:88}, 4:{x:235,y:92},
  17:{x:230,y:108}, 43:{x:200,y:134}, 11:{x:170,y:108},
  62:{x:150,y:180}, 23:{x:162,y:193}, 56:{x:156,y:207},
  35:{x:250,y:180}, 12:{x:238,y:193}, 45:{x:244,y:207},
  33:{x:228,y:174}, 8:{x:160,y:174}, 31:{x:234,y:212},
  20:{x:163,y:212}, 16:{x:250,y:220},
  7:{x:160,y:250}, 1:{x:168,y:265}, 13:{x:160,y:282},
  10:{x:193,y:244}, 25:{x:207,y:244}, 15:{x:222,y:265},
  46:{x:230,y:282}, 2:{x:227,y:297},
  21:{x:296,y:232}, 40:{x:298,y:250}, 26:{x:296,y:268}, 51:{x:296,y:286},
  48:{x:98,y:270}, 57:{x:90,y:288}, 44:{x:90,y:308}, 50:{x:98,y:324},
  32:{x:112,y:340}, 28:{x:102,y:352}, 18:{x:108,y:312},
  30:{x:302,y:302}, 55:{x:312,y:318}, 49:{x:302,y:336},
  37:{x:292,y:352}, 22:{x:312,y:290}, 36:{x:302,y:368}, 6:{x:290,y:382},
  5:{x:150,y:354}, 14:{x:162,y:368}, 29:{x:150,y:382},
  59:{x:250,y:354}, 9:{x:238,y:368}, 3:{x:250,y:382},
  42:{x:172,y:350}, 27:{x:228,y:350}, 34:{x:205,y:348},
  60:{x:150,y:422}, 52:{x:162,y:438}, 19:{x:150,y:454},
  39:{x:250,y:422}, 53:{x:238,y:438}, 54:{x:250,y:454},
  58:{x:173,y:460}, 38:{x:227,y:460}, 41:{x:200,y:465}
};

function getCenterForGate(gate) {
  for (const [center, gates] of Object.entries(CENTER_GATES)) {
    if (gates.includes(gate)) return center;
  }
  return null;
}

function renderCenter(name, pos, isDefined) {
  const fill   = isDefined ? 'var(--teal)' : 'var(--white)';
  const stroke = isDefined ? '#2d6060'     : 'var(--sage)';
  const label  = isDefined ? '#FFFFFF'     : 'var(--sage)';
  const sw     = 1.5;
  let shape = '';

  if (pos.shape === 'rect') {
    shape = `<rect x="${pos.x-pos.w/2}" y="${pos.y-pos.h/2}" width="${pos.w}" height="${pos.h}" rx="6" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  } else if (pos.shape === 'diamond') {
    const hw = pos.w/2, hh = pos.h/2;
    shape = `<polygon points="${pos.x},${pos.y-hh} ${pos.x+hw},${pos.y} ${pos.x},${pos.y+hh} ${pos.x-hw},${pos.y}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  } else if (pos.shape === 'triangle-up') {
    shape = `<polygon points="${pos.x},${pos.y-pos.h/2} ${pos.x-pos.w/2},${pos.y+pos.h/2} ${pos.x+pos.w/2},${pos.y+pos.h/2}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  } else if (pos.shape === 'triangle-down') {
    shape = `<polygon points="${pos.x},${pos.y+pos.h/2} ${pos.x-pos.w/2},${pos.y-pos.h/2} ${pos.x+pos.w/2},${pos.y-pos.h/2}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  }

  const shortNames = {HEAD:'HEAD',AJNA:'AJNA',THROAT:'THROAT',G:'G',SACRAL:'SACRAL',EGO:'EGO',SPLEEN:'SPLEEN',SOLAR:'SOLAR',ROOT:'ROOT'};
  shape += `<text x="${pos.x}" y="${pos.y+1}" text-anchor="middle" dominant-baseline="middle" fill="${label}" font-family="Lato,sans-serif" font-size="7.5" font-weight="700" letter-spacing="0.5">${shortNames[name]}</text>`;
  return shape;
}

function renderBodygraph(data) {
  const svg = document.getElementById('bodygraph-svg');
  const definedCenters  = new Set(data.defined_centers);
  const personalityGates = new Set(data.personality_gates);
  const designGates      = new Set(data.design_gates);
  const allGates         = new Set(data.all_gates);
  let html = '';

  // Channels (draw first, behind centers)
  for (const [a, b] of CHANNELS) {
    const ca = getCenterForGate(a), cb = getCenterForGate(b);
    if (!ca || !cb) continue;
    const pa = CENTER_POSITIONS[ca], pb = CENTER_POSITIONS[cb];
    const isDefined = allGates.has(a) && allGates.has(b);
    const color = isDefined ? '#3D7A7A' : '#E0DDD8';
    const width = isDefined ? 3 : 1;
    html += `<line x1="${pa.x}" y1="${pa.y}" x2="${pb.x}" y2="${pb.y}" stroke="${color}" stroke-width="${width}" stroke-linecap="round"/>`;
  }

  // Centers
  for (const [name, pos] of Object.entries(CENTER_POSITIONS)) {
    html += renderCenter(name, pos, definedCenters.has(name));
  }

  // Gate numbers
  for (const [gStr, pos] of Object.entries(GATE_POSITIONS)) {
    const gate = parseInt(gStr);
    const inP  = personalityGates.has(gate);
    const inD  = designGates.has(gate);
    const inB  = inP && inD;
    let fill = '#CECAC4';
    let fw = '400', fs = '7';
    if (inB)  { fill = '#2C3E35'; fw = '700'; fs = '7.5'; }
    else if (inP) { fill = '#3D7A7A'; fw = '700'; fs = '7.5'; }
    else if (inD) { fill = '#A8B89A'; fw = '700'; fs = '7.5'; }
    html += `<text x="${pos.x}" y="${pos.y}" text-anchor="middle" dominant-baseline="middle" fill="${fill}" font-family="Lato,sans-serif" font-size="${fs}" font-weight="${fw}">${gate}</text>`;
  }

  svg.innerHTML = html;
}

function renderSummary(data) {
  const typeDescs = {
    'Generator':           'Your gifts are energy, desire, and the ability to sustain. You\'re here to do what truly lights you up.',
    'Manifesting Generator':'Your gifts are speed, multi-passionate energy, and finding better ways. You\'re here to respond and move fast.',
    'Manifestor':          'Your gifts are initiating, creating impact, and setting things in motion. You\'re here to act independently.',
    'Projector':           'Your gifts are guiding, seeing the big picture, and leading with wisdom. You\'re here to be recognized.',
    'Reflector':           'Your gifts are sampling, reflecting, and showing communities their own health. You\'re here to be a mirror.'
  };

  const items = [
    { label: 'Type',            title: data.type,       desc: typeDescs[data.type] || '' },
    { label: 'Strategy',        title: '',              desc: data.strategy },
    { label: 'Inner Authority', title: data.authority,  desc: data.authority_desc },
    { label: 'Profile',         title: data.profile.split(' — ')[0], desc: (data.profile.split(' — ')[1] || '') },
    { label: 'Signature',       title: data.signature,  desc: 'The feeling that tells you you\'re aligned.' },
    { label: 'Not-Self Theme',  title: data.not_self,   desc: 'The feeling that signals something is off.' },
    { label: 'Defined Centers', title: '',              desc: data.defined_centers.join(', ') || 'None — you are a Reflector' },
  ];

  document.getElementById('summary-items').innerHTML = items.map(i => `
    <div class="summary-item">
      <div class="summary-label">${i.label}</div>
      ${i.title ? `<div class="summary-title">${i.title}</div>` : ''}
      ${i.desc  ? `<div class="summary-desc">${i.desc}</div>`   : ''}
    </div>
  `).join('');
}

function renderGates(data) {
  const pLabels = {
    sun:'Sun', earth:'Earth', north_node:'N.Node', south_node:'S.Node',
    moon:'Moon', mercury:'Mercury', venus:'Venus', mars:'Mars'
  };
  const planetOrder = ['sun','earth','north_node','south_node','moon','mercury','venus','mars'];

  let html = '<div class="gate-rows">';
  html += `<div class="gate-section-label">Personality (Conscious)</div>`;
  for (const p of planetOrder) {
    const g = data.personality[p];
    if (!g) continue;
    html += `<div class="gate-row">
      <span class="gate-planet">${pLabels[p]}</span>
      <span class="gate-num" style="color:#3D7A7A">${g.gate}.${g.line}</span>
      <span class="gate-name">${g.name}</span>
    </div>`;
  }
  html += `<div class="gate-section-label" style="margin-top:12px">Design (Unconscious)</div>`;
  for (const p of planetOrder) {
    const g = data.design[p];
    if (!g) continue;
    html += `<div class="gate-row">
      <span class="gate-planet">${pLabels[p]}</span>
      <span class="gate-num" style="color:#A8B89A">${g.gate}.${g.line}</span>
      <span class="gate-name">${g.name}</span>
    </div>`;
  }
  html += '</div>';
  document.getElementById('gates-list').innerHTML = html;
}

// ── Form helpers ──────────────────────────────────────────────────
function populateSelects() {
  const yearSel = document.getElementById('birth-year');
  yearSel.innerHTML = '<option value="">Year</option>';
  for (let y = new Date().getFullYear() - 1; y >= 1920; y--) {
    yearSel.innerHTML += `<option value="${y}">${y}</option>`;
  }
  const daySel = document.getElementById('birth-day');
  daySel.innerHTML = '<option value="">Day</option>';
  for (let d = 1; d <= 31; d++) daySel.innerHTML += `<option value="${d}">${d}</option>`;

  const hourSel = document.getElementById('birth-hour');
  hourSel.innerHTML = '<option value="">Hour</option>';
  for (let h = 0; h < 24; h++) hourSel.innerHTML += `<option value="${h}">${String(h).padStart(2,'0')}</option>`;

  const minSel = document.getElementById('birth-minute');
  minSel.innerHTML = '<option value="">Min</option>';
  for (let m = 0; m < 60; m++) minSel.innerHTML += `<option value="${m}">${String(m).padStart(2,'0')}</option>`;
}

function showError(msg) {
  const el = document.getElementById('error-msg');
  el.innerHTML = msg;
  el.style.display = 'block';
}
function hideError() { document.getElementById('error-msg').style.display = 'none'; }

async function generateChart() {
  hideError();

  const name   = document.getElementById('name').value.trim();
  const year   = parseInt(document.getElementById('birth-year').value);
  const month  = parseInt(document.getElementById('birth-month').value);
  const day    = parseInt(document.getElementById('birth-day').value);
  const hour   = parseInt(document.getElementById('birth-hour').value);
  const minute = parseInt(document.getElementById('birth-minute').value);
  const city   = document.getElementById('birth-place-full').value.trim() || document.getElementById('birth-place').value.trim();

  if (!year || !month || !day) { showError('Please select your full birth date.'); return; }
  if (isNaN(hour) || isNaN(minute)) { showError('Please select your birth time. If unknown, use 12:00.'); return; }
  if (!city) { showError('Please enter your birth city.'); return; }

  document.getElementById('form-section').style.display = 'none';
  document.getElementById('loading').style.display = 'block';

  try {
    const response = await fetch(`${API_URL}/chart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, year, month, day, hour, minute, city })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Something went wrong. Please try again.');
    }

    const data = await response.json();

    document.getElementById('loading').style.display = 'none';
    document.getElementById('result').style.display = 'block';

    const displayName = name || 'Your';
    document.getElementById('chart-name').textContent = displayName + (displayName === 'Your' ? '' : "'s") + ' Human Design Chart';
    document.getElementById('result-title').textContent = displayName + (displayName === 'Your' ? '' : "'s") + ' Human Design Chart';

    const monthNames = ['','January','February','March','April','May','June','July','August','September','October','November','December'];
    document.getElementById('chart-birthinfo').textContent =
      `${monthNames[month]} ${day}, ${year} · ${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')} · ${city}`;

    renderBodygraph(data);
    renderSummary(data);


    window._chartData = data;
    window._chartMeta = { name, year, month, day, hour, minute, city };

  } catch (err) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('form-section').style.display = 'block';
    showError(`
      <strong>Couldn't generate your chart.</strong><br>
      ${err.message}<br><br>
      <small>If the error mentions "city not found", try being more specific — e.g. "Lansing, Michigan, United States"</small>
    `);
  }
}

function resetForm() {
  document.getElementById('result').style.display = 'none';
  document.getElementById('form-section').style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function downloadChart() {
  const data = window._chartData;
  const meta = window._chartMeta;
  if (!data) return;

  const svgContent     = document.getElementById('bodygraph-svg').outerHTML;
  const summaryContent = document.getElementById('summary-items').innerHTML;
  const chartName      = document.getElementById('chart-name').textContent;
  const chartInfo      = document.getElementById('chart-birthinfo').textContent;

  const html = `<!DOCTYPE html><html><head>
<meta charset="UTF-8"><title>${chartName}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
<style>
:root{--teal:#3D7A7A;--teal-light:#A8C8D8;--sage:#A8B89A;--linen:#F0EDE8;--linen-dark:#E5E0D8;--text-dark:#2C3E35;--text-mid:#5A6B5E;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Lato',sans-serif;background:var(--linen);color:var(--text-dark);padding:40px 32px;}
.wrap{max-width:920px;margin:0 auto;}
h1{font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--teal);margin-bottom:4px;}
.info{font-size:0.85rem;color:var(--text-mid);margin-bottom:28px;}
.layout{display:grid;grid-template-columns:1fr 320px;gap:24px;align-items:start;}
.bg-wrap{background:#fff;border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(61,122,122,0.08);}
svg{width:100%;height:auto;}
.card{background:#fff;border-radius:14px;padding:20px 22px;box-shadow:0 4px 20px rgba(61,122,122,0.08);}
.card h3{font-family:'Playfair Display',serif;font-size:1rem;color:var(--teal);margin-bottom:12px;padding-bottom:8px;border-bottom:1.5px solid var(--linen-dark);}
.summary-item{margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid var(--linen);}
.summary-item:last-child{border-bottom:none;margin-bottom:0;padding-bottom:0;}
.summary-label{font-size:0.6rem;font-weight:700;text-transform:none;letter-spacing:0;color:var(--text-mid);margin-bottom:2px;line-height:1.4;}
.summary-title{font-family:'Playfair Display',serif;font-size:0.95rem;color:var(--teal);font-weight:600;margin-bottom:2px;}
.summary-desc{font-size:0.75rem;color:var(--text-mid);line-height:1.5;font-weight:300;}
.footer{margin-top:24px;font-size:0.7rem;color:var(--text-mid);text-align:center;}
</style></head><body>
<div class="wrap">
<h1>${chartName}</h1>
<p class="info">${chartInfo}</p>
<div class="layout">
<div class="bg-wrap">${svgContent}</div>
<div class="card"><h3>Chart Summary</h3>${summaryContent}</div>
</div>
<p class="footer">Generated by ROI of Peace · roiofpeace.com</p>
</div></body></html>`;

  const blob = new Blob([html], { type: 'text/html' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = `${(meta.name || 'chart').replace(/\s+/g,'-').toLowerCase()}-human-design.html`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

populateSelects();

// ── City Autocomplete (OpenStreetMap Nominatim — no API key needed) ──
let _autocompleteTimer = null;

async function cityAutocomplete(val) {
  const list = document.getElementById("autocomplete-list");
  clearTimeout(_autocompleteTimer);
  if (val.length < 2) { list.style.display = "none"; return; }
  _autocompleteTimer = setTimeout(async () => {
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(val)}&format=json&addressdetails=1&limit=6&featuretype=city,town,village`, { headers: {"Accept-Language": "en"} });
      const data = await res.json();
      if (!data.length) { list.style.display = "none"; return; }
      list.innerHTML = data.map((item, i) => {
        const addr = item.address;
        const city = addr.city || addr.town || addr.village || addr.county || item.name;
        const state = addr.state || addr.region || "";
        const country = addr.country || "";
        const full = [city, state, country].filter(Boolean).join(", ");
        return `<div class="autocomplete-item" onclick="selectCity(${i})" data-full="${full}"><span class="city-main">${city}</span><br><span class="city-sub">${[state,country].filter(Boolean).join(", ")}</span></div>`;
      }).join("");
      list.style.display = "block";
    } catch(e) { list.style.display = "none"; }
  }, 350);
}

function selectCity(i) {
  const list = document.getElementById("autocomplete-list");
  const item = list.querySelectorAll(".autocomplete-item")[i];
  const full = item.getAttribute("data-full");
  document.getElementById("birth-place").value = full;
  document.getElementById("birth-place-full").value = full;
  list.style.display = "none";
}

document.addEventListener("click", (e) => {
  if (!e.target.closest(".autocomplete-wrap")) {
    document.getElementById("autocomplete-list").style.display = "none";
  }
});
</script>
</body>
</html>
