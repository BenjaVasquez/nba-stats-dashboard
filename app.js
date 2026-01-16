let statsChart = null,
  all_db = { fixture: [], players: [] },
  currentStat = 'pts',
  selectedPlayer = null,
  isDragging = false,
  bgImage = new Image();

const teamColors = {
  ATL: '#E03A3E',
  BOS: '#007A33',
  BKN: '#000000',
  CHA: '#1D1160',
  CHI: '#CE1141',
  CLE: '#860038',
  DAL: '#00538C',
  DEN: '#0E2240',
  DET: '#C8102E',
  GSW: '#1D428A',
  HOU: '#CE1141',
  IND: '#FDB927',
  LAC: '#C8102E',
  LAL: '#552583',
  MEM: '#5D76A9',
  MIA: '#98002E',
  MIL: '#00471B',
  MIN: '#0C2340',
  NOP: '#0C2340',
  NYK: '#006BB6',
  OKC: '#007AC1',
  ORL: '#0077C0',
  PHI: '#006BB6',
  PHX: '#1D1160',
  POR: '#E03A3E',
  SAC: '#5A2D81',
  SAS: '#C4CED4',
  TOR: '#CE1141',
  UTA: '#002B5C',
  WAS: '#002B5C',
};

// --- DEFINICIÓN DE PLUGINS ---

const xAxisLogos = {
  id: 'xAxisLogos',
  afterDraw: (chart) => {
    const ctx = chart.ctx,
      xAxis = chart.scales.x,
      opponents = chart.data.datasets[0].opponents || [];
    xAxis.ticks.forEach((t, i) => {
      const logo = nbaLogos[opponents[i]];
      if (logo) {
        const img = new Image();
        img.src = logo;
        const x = xAxis.getPixelForTick(i);
        ctx.drawImage(img, x - 11, chart.chartArea.bottom + 35, 40, 40);
      }
    });
  },
};

// Plugin para la marca de agua del equipo en el fondo del gráfico
const backgroundImagePlugin = {
  id: 'customCanvasBackgroundImage',
  beforeDraw: (chart) => {
    if (bgImage.src && bgImage.complete) {
      const {
        ctx,
        chartArea: { top, left, width, height },
      } = chart;
      ctx.save();
      ctx.globalAlpha = 0.08;
      const size = Math.min(width, height) * 0.7;
      ctx.drawImage(
        bgImage,
        left + (width - size) / 2,
        top + (height - size) / 2,
        size,
        size
      );
      ctx.restore();
    }
  },
};

// --- REGISTRO SEGURO DE PLUGINS ---
try {
  const annotationPlugin = window['chartjs-plugin-annotation'];
  const datalabelsPlugin = window.ChartDataLabels;

  if (annotationPlugin && datalabelsPlugin) {
    Chart.register(
      datalabelsPlugin,
      annotationPlugin,
      backgroundImagePlugin,
      xAxisLogos
    );
    console.log('✅ Plugins registrados correctamente.');
  }
} catch (e) {
  console.error('⚠️ Error en registro de Chart.js:', e);
}

// --- FUNCIONES DE APOYO ---

const getDD = (g) =>
  g.status !== 'Played'
    ? 0
    : [g.pts, g.reb, g.ast, g.stl, g.blk].filter((v) => v >= 10).length >= 2
    ? 1
    : 0;
const getTD = (g) =>
  g.status !== 'Played'
    ? 0
    : [g.pts, g.reb, g.ast, g.stl, g.blk].filter((v) => v >= 10).length >= 3
    ? 1
    : 0;

function formatNBADate(dateStr) {
  if (!dateStr) return '';
  const months = [
    'Ene',
    'Feb',
    'Mar',
    'Abr',
    'May',
    'Jun',
    'Jul',
    'Ago',
    'Sep',
    'Oct',
    'Nov',
    'Dic',
  ];
  const d = new Date(dateStr.replace(/-/g, '/'));
  return isNaN(d) ? dateStr : `${months[d.getMonth()]} ${d.getDate()}`;
}

async function loadData() {
  try {
    const [playersRes, fixtureRes, injuriesRes] = await Promise.all([
      fetch('./data.json'),
      fetch('./fixture.json'),
      fetch('./injuries.json'),
      fetch('./team_history.json'),
    ]);

    const playersData = await playersRes.json();
    all_db.players = playersData.players;
    all_db.injuries = await injuriesRes.json();

    renderFixture(await fixtureRes.json());
    renderPlayers(all_db.players);
    initChart();
  } catch (e) {
    console.error('Error cargando datos', e);
  }
}

function updateUI() {
  if (!selectedPlayer) return;
  const color = teamColors[selectedPlayer.team] || '#334155';
  document.getElementById('player-photo-container').style.borderColor = color;
  document.getElementById('player-name-display').innerText =
    selectedPlayer.name;
  document.getElementById('player-number-display').innerText =
    selectedPlayer.num ? `#${selectedPlayer.num}` : '';
  document.getElementById(
    'player-photo-main'
  ).src = `https://cdn.nba.com/headshots/nba/latest/1040x760/${selectedPlayer.id}.png`;

  bgImage.src = nbaLogos[selectedPlayer.team];
  document.getElementById('player-team-mini').src =
    nbaLogos[selectedPlayer.team];

  const bio = selectedPlayer.bio || {};
  document.getElementById('bio-pos').innerText = bio.pos || '---';
  document.getElementById('bio-height').innerText = bio.height || '---';
  document.getElementById('bio-weight').innerText = bio.weight || '---';
  document.getElementById('bio-age').innerText = bio.age || '--';
  document.getElementById('bio-birth').innerText = bio.birthdate || '---';
  document.getElementById('bio-country').innerText = bio.country || '---';

  const flag = document.getElementById('bio-flag');
  if (bio.flag) {
    flag.src = `https://flagcdn.com/w20/${bio.flag}.png`;
    flag.classList.remove('hidden');
  }

  const sAvg = selectedPlayer.season_averages || {
    pts: 0,
    reb: 0,
    ast: 0,
    tpm: 0,
    min: 0,
  };

  document.getElementById('header-avg-pts').innerText = sAvg.pts.toFixed(1);
  document.getElementById('header-avg-ast').innerText = sAvg.ast.toFixed(1);
  document.getElementById('header-avg-reb').innerText = sAvg.reb.toFixed(1);
  document.getElementById('header-avg-tpm').innerText = sAvg.tpm.toFixed(1);
  document.getElementById('header-avg-min').innerText = Math.round(sAvg.min);

  const injury = all_db.injuries[selectedPlayer.name];
  const badge = document.getElementById('injury-badge-main');
  badge.innerHTML = '';

  if (injury) {
    const div = document.createElement('div');
    div.className = `flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
      injury.status === 'red'
        ? 'bg-red-500/20 text-red-500 border border-red-500/30'
        : 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/30'
    } animate-pulse`;
    div.innerHTML = `<span>● ${injury.description}</span>`;
    badge.appendChild(div);
  }

  const history = selectedPlayer.last_15;
  const data = history.map((g) => {
    const pts = g.pts || 0;
    const reb = g.reb || 0;
    const ast = g.ast || 0;

    switch (currentStat) {
      case 'pts_reb':
        return pts + reb;
      case 'pts_ast':
        return pts + ast;
      case 'reb_ast':
        return reb + ast;
      case 'pra':
        return pts + reb + ast;
      case 'dd2':
        return g.dd2 || 0;
      case 'dd3':
        return g.dd3 || 0;
      default:
        return g[currentStat] || 0;
    }
  });

  statsChart.data.labels = history.map((g) => formatNBADate(g.date));
  statsChart.data.datasets[0].data = data;
  statsChart.data.datasets[0].opponents = history.map((g) => g.opponent);
  statsChart.options.scales.y.suggestedMax =
    currentStat === 'dd' || currentStat === 'td'
      ? 1.5
      : Math.max(...data, 5) * 1.25;
  statsChart.update();

  if (currentStat === 'dd2' || currentStat === 'dd3') {
    document.getElementById('threshold-value').innerText = '0.5';
  }

  statsChart.data.labels = history.map((g) =>
    g.date.slice(5).replace('-', '/')
  );
  statsChart.data.datasets[0].data = data;
  statsChart.update();

  updateThreshold(document.getElementById('threshold-value').innerText);
}

function initChart() {
  const ctx = document.getElementById('statsChart').getContext('2d');
  statsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          opponents: [],
          backgroundColor: (ctx) => {
            const v = ctx.raw,
              thr =
                statsChart?.options?.plugins?.annotation?.annotations?.line1
                  ?.yMin || 20.5;
            return v === 0
              ? 'rgba(239, 68, 68, 0.2)'
              : v >= thr
              ? '#10b981'
              : '#ef4444';
          },
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { bottom: 65 } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#1e293b' } },
        x: { grid: { display: false } },
      },
      plugins: {
        legend: { display: false },
        datalabels: {
          anchor: 'end',
          align: 'top',
          color: '#fff',
          font: { weight: 'bold', size: 11 },
          formatter: (v) => (v === 0 ? 'DNP' : v),
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(2, 6, 23, 0.95)',
          titleColor: '#3b82f6',
          titleFont: { size: 13, weight: '900' },
          bodyFont: { size: 11 },
          padding: 12,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            title: (items) => {
              const g = selectedPlayer.last_15[items[0].dataIndex];
              const resLabel = g.result === 'W' ? 'Ganó' : 'Perdió';
              const margen = g.margin > 0 ? `+${g.margin}` : g.margin;
              return [`vs ${g.opponent}`, `${resLabel} (${margen} pts)`];
            },
            label: (item) => {
              const g = selectedPlayer.last_15[item.dataIndex];

              // Cálculo de porcentajes
              const triPct = g.tpa > 0 ? ((g.tpm / g.tpa) * 100).toFixed(0) : 0;
              const libPct =
                g.ft_a > 0 ? ((g.ft_m / g.ft_a) * 100).toFixed(0) : 0;

              return [
                `Puntos: ${g.pts}`,
                `Asistencias: ${g.ast} | Rebotes: ${g.reb}`,
                `Triples: ${g.tpm}/${g.tpa} (${triPct}%)`,
                `Libres: ${g.ft_m}/${g.ft_a} (${libPct}%)`,
                `Minutos: ${g.min}'`,
              ];
            },
          },
        },
        annotation: {
          annotations: {
            line1: {
              type: 'line',
              yMin: 20.5,
              yMax: 20.5,
              borderColor: '#facc15',
              borderWidth: 2,
              label: {
                display: true,
                content: (ctx) =>
                  ctx.chart.options.plugins.annotation.annotations.line1.yMin,
                position: 'end',
                backgroundColor: '#facc15',
                color: '#000',
              },
            },
          },
        },
      },
    },
  });

  // --- LÓGICA DE INTERACCIÓN (DRAG LINE) ---
  const canv = document.getElementById('statsChart');
  canv.onmousedown = () => {
    isDragging = true;
  };
  window.onmouseup = () => {
    isDragging = false;
  };
  canv.onmousemove = (e) => {
    if (isDragging) {
      const r = canv.getBoundingClientRect();
      const y = statsChart.scales.y.getValueForPixel(e.clientY - r.top);
      if (y >= 0) {
        // Redondeo a .5 para facilidad de uso
        updateThreshold(Math.round(y * 2) / 2);
      }
    }
  };
}

function updateThreshold(v) {
  const val = parseFloat(v);
  document.getElementById('threshold-value').innerText = val;
  if (statsChart) {
    statsChart.options.plugins.annotation.annotations.line1.yMin = val;
    statsChart.options.plugins.annotation.annotations.line1.yMax = val;

    const d = statsChart.data.datasets[0].data,
      h = d.filter((x) => x >= val && x > 0).length,
      t = d.filter((x) => x > 0).length;
    const pct = t > 0 ? ((h / t) * 100).toFixed(1) : 0;

    const hr = document.getElementById('hit-rate');
    hr.innerText = pct + '%';
    hr.className = `text-4xl font-black ${
      pct >= 50 ? 'text-green-500' : 'text-red-500'
    }`;
    document.getElementById('hit-fraction').innerText = `(${h}/${t} games)`;

    statsChart.update('none'); // Update sin animación para fluidez al arrastrar
  }
}

window.changeStat = (s) => {
  currentStat = s;
  updateUI();
};
window.searchPlayer = (q) =>
  renderPlayers(
    all_db.players
      .filter((p) => p.name.toLowerCase().includes(q.toLowerCase()))
      .slice(0, 50)
  );

function renderFixture(games) {
  const container = document.getElementById('fixture-list');
  container.innerHTML = '';
  let currentDay = '';

  games.forEach((game) => {
    if (game.DAY_LABEL !== currentDay) {
      const header = document.createElement('div');
      header.className =
        'bg-slate-900/90 px-4 py-2 text-[10px] font-black text-blue-400 uppercase tracking-widest border-y border-slate-800 sticky top-0 z-10';
      header.innerText = game.DAY_LABEL;
      container.appendChild(header);
      currentDay = game.DAY_LABEL;
    }

    const div = document.createElement('div');
    div.className =
      'p-5 flex justify-between items-center border-b border-slate-800/40 hover:bg-slate-800/40 cursor-pointer transition-all';
    div.innerHTML = `
      <div class="text-center w-16"><img src="${
        nbaLogos[game.AWAY_TEAM]
      }" class="w-8 h-8 mb-1 mx-auto"><span class="text-[10px] font-black text-white">${
      game.AWAY_TEAM
    }</span></div>
      <div class="flex-1 text-center">
        <span class="text-blue-500 font-black italic text-[9px] block">VS</span>
        <span class="text-xl font-black text-white block">${
          game.TIME_ONLY
        }</span>
        <span class="text-[7px] text-slate-500 font-bold uppercase block truncate">${
          game.STADIUM
        }</span>
      </div>
      <div class="text-center w-16"><img src="${
        nbaLogos[game.HOME_TEAM]
      }" class="w-8 h-8 mb-1 mx-auto"><span class="text-[10px] font-black text-white">${
      game.HOME_TEAM
    }</span></div>`;
    div.onclick = () =>
      renderPlayers(
        all_db.players.filter(
          (p) => p.team === game.HOME_TEAM || p.team === game.AWAY_TEAM
        )
      );
    container.appendChild(div);
  });
}

function renderPlayers(list) {
  const c = document.getElementById('player-list');
  c.innerHTML = '';

  // Ordenar: Sanos primero, lesionados al final
  const sorted = [...list].sort(
    (a, b) =>
      (all_db.injuries[a.name] ? 1 : 0) - (all_db.injuries[b.name] ? 1 : 0)
  );

  let lastTeam = '';
  sorted.forEach((p) => {
    const teamName = p.team_full || p.team;
    if (teamName !== lastTeam) {
      const h = document.createElement('div');
      h.className =
        'text-[9px] font-black text-slate-500 uppercase px-3 py-3 mt-2 border-l border-slate-800 bg-slate-900/30';
      h.innerText = teamName;
      c.appendChild(h);
      lastTeam = teamName;
    }

    const injury = all_db.injuries[p.name];
    let injuryIcon = '';
    if (injury) {
      const color = injury.status === 'red' ? 'bg-red-600' : 'bg-yellow-600';
      injuryIcon = `<div class="absolute -top-1 -right-1 w-4 h-4 rounded-full border border-slate-900 flex items-center justify-center ${color}">
        <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="6" class="w-2 h-2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </div>`;
    }

    const b = document.createElement('button');
    b.className = `w-full text-left p-2 rounded-lg hover:bg-slate-800 flex items-center gap-3 transition-all ${
      injury ? 'opacity-60' : ''
    }`;
    b.innerHTML = `<div class="relative"><img src="https://cdn.nba.com/headshots/nba/latest/1040x760/${p.id}.png" class="w-10 h-10 rounded-full bg-slate-900 border border-slate-800">${injuryIcon}</div>
      <div class="flex-1 overflow-hidden"><span class="text-sm font-bold text-white block truncate">${p.name}</span><p class="text-[9px] text-slate-500 uppercase">${p.bio.pos}</p></div>`;
    b.onclick = () => {
      selectedPlayer = p;
      updateUI();
    };
    c.appendChild(b);
  });
}

document.addEventListener('DOMContentLoaded', loadData);


function updateTeamRecord(teamAbb) {
  const history = all_db.team_history[teamAbb] || [];
  const wins = history.filter((g) => g.wl === 'W').length;
  const losses = history.filter((g) => g.wl === 'L').length;

  const container = document.getElementById('team-record-display');
  if (container) {
    container.innerHTML = `
            <div class="text-[10px] font-black text-slate-500 uppercase mb-1">Récord Equipo (Desde 2023)</div>
            <div class="flex items-center gap-2">
                <span class="text-green-500 font-black text-xl">${wins}W</span>
                <span class="text-slate-600">-</span>
                <span class="text-red-500 font-black text-xl">${losses}L</span>
            </div>
        `;
  }
}

// En app.js, cambia la función triggerDeepUpdate:
async function triggerDeepUpdate() {
    if(!confirm("¿Deseas iniciar la actualización en la nube?")) return;

    try {
        // Llamamos a nuestra función secreta en Netlify, no a GitHub directamente
        const response = await fetch('/.netlify/functions/trigger-update');
        
        if (response.ok) {
            alert("🚀 Orden enviada con éxito.");
        } else {
            alert("❌ Error en el servidor.");
        }
    } catch (error) {
        alert("❌ Error de conexión.");
    }
}