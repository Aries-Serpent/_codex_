# 💰 Cost Estimator Dashboard

**Last Updated:** 2026-06-22

> **Live dashboard** — Actions-minute consumption and cost-tier classification for every gated workflow in this repository.  
> **Budget:** 3,000 Linux-equivalent minutes/month · GitHub Team + Copilot Pro Plus  
> **Policy:** [Cost Governance Policy](COST_GOVERNANCE.md) · **OKR:** OBJ-001 (Production: 2026-04-01)

---

<div id="cost-dashboard">
  <div id="dash-loading" style="text-align:center;padding:3rem;font-size:1.1rem;color:#888;">
    ⏳ Loading cost data…
  </div>
</div>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>

<style>
/* ── Dashboard layout ─────────────────────────────────────────── */
#cost-dashboard { font-family: inherit; }

.dash-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.2rem;
  margin: 1.5rem 0;
}

.stat-card {
  border-radius: 10px;
  padding: 1.2rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,.10);
  text-align: center;
  transition: transform .15s;
}
.stat-card:hover { transform: translateY(-2px); }
.stat-card .label { font-size: .82rem; font-weight: 600; text-transform: uppercase; letter-spacing: .07em; opacity: .7; }
.stat-card .value { font-size: 2.4rem; font-weight: 800; line-height: 1.1; margin: .3rem 0; }
.stat-card .sub   { font-size: .85rem; opacity: .65; }

.card-green  { background: #e8f8f0; color: #1b7a47; border: 1.5px solid #a3e4be; }
.card-yellow { background: #fffbea; color: #7d5f00; border: 1.5px solid #ffe680; }
.card-red    { background: #fff0f0; color: #a41818; border: 1.5px solid #ffb3b3; }
.card-blue   { background: #eff6ff; color: #1e40af; border: 1.5px solid #bfdbfe; }

@media (prefers-color-scheme: dark) {
  .card-green  { background: #0f2e1e; color: #6ee7b7; border-color: #166534; }
  .card-yellow { background: #2a2000; color: #fde68a; border-color: #854d0e; }
  .card-red    { background: #2a0a0a; color: #fca5a5; border-color: #991b1b; }
  .card-blue   { background: #0f1c3a; color: #93c5fd; border-color: #1e3a8a; }
}

/* ── Chart containers ─────────────────────────────────────────── */
.charts-row {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.5rem;
  margin: 2rem 0;
  align-items: start;
}
@media (max-width: 700px) {
  .charts-row { grid-template-columns: 1fr; }
}
.chart-box {
  border-radius: 10px;
  padding: 1.2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
  background: var(--md-default-bg-color, #fff);
}
[data-md-color-scheme="slate"] .chart-box { background: #1e2229; }
.chart-title {
  font-weight: 700;
  font-size: .9rem;
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-bottom: .8rem;
  opacity: .7;
}

/* ── Budget progress bar ──────────────────────────────────────── */
.progress-wrap { margin: 1.2rem 0; }
.progress-bar-bg {
  background: #e5e7eb;
  border-radius: 999px;
  height: 20px;
  overflow: hidden;
  position: relative;
}
[data-md-color-scheme="slate"] .progress-bar-bg { background: #374151; }
.progress-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width .6s cubic-bezier(.4,0,.2,1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: .75rem;
  font-weight: 700;
  color: #fff;
}
.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: .8rem;
  margin-top: .3rem;
  opacity: .7;
}

/* ── Gated workflows table ────────────────────────────────────── */
.wf-table {
  width: 100%;
  border-collapse: collapse;
  font-size: .88rem;
  margin: 1rem 0;
}
.wf-table th {
  text-align: left;
  padding: .55rem .8rem;
  border-bottom: 2px solid #e5e7eb;
  font-size: .78rem;
  text-transform: uppercase;
  letter-spacing: .07em;
  opacity: .65;
}
.wf-table td { padding: .5rem .8rem; border-bottom: 1px solid #e5e7eb; }
[data-md-color-scheme="slate"] .wf-table th,
[data-md-color-scheme="slate"] .wf-table td { border-color: #374151; }
.tier-badge {
  display: inline-block;
  padding: .15rem .65rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: .75rem;
  letter-spacing: .05em;
}
.tier-GREEN  { background: #d1fae5; color: #065f46; }
.tier-YELLOW { background: #fef9c3; color: #713f12; }
.tier-RED    { background: #fee2e2; color: #7f1d1d; }
[data-md-color-scheme="slate"] .tier-GREEN  { background: #064e3b; color: #6ee7b7; }
[data-md-color-scheme="slate"] .tier-YELLOW { background: #451a03; color: #fde68a; }
[data-md-color-scheme="slate"] .tier-RED    { background: #450a0a; color: #fca5a5; }

/* ── Recent runs ──────────────────────────────────────────────── */
.runs-table { width:100%; border-collapse:collapse; font-size:.85rem; }
.runs-table th { padding:.4rem .7rem; border-bottom:2px solid #e5e7eb; font-size:.75rem; text-transform:uppercase; letter-spacing:.06em; opacity:.6; }
.runs-table td { padding:.4rem .7rem; border-bottom:1px solid #f3f4f6; }
[data-md-color-scheme="slate"] .runs-table th,
[data-md-color-scheme="slate"] .runs-table td { border-color:#374151; }
.conclusion-success { color: #16a34a; font-weight:600; }
.conclusion-failure { color: #dc2626; font-weight:600; }
.conclusion-other   { color: #6b7280; }

/* ── Footer meta ──────────────────────────────────────────────── */
.dash-meta { font-size:.78rem; opacity:.55; text-align:right; margin-top:2rem; }
</style>

<script>
(function () {
  /* ── Resolve base URL for relative fetch ─────────────────────────────── */
  const BASE = (() => {
    const scripts = document.querySelectorAll('script[src]');
    // Try to detect GitHub Pages base path from window.location
    const p = window.location.pathname.replace(/\/$/, '');
    const base = p.includes('/_codex_') ? '/_codex_' : '';
    return base;
  })();

  const DATA_URL = BASE + '/ops/cost-data.json';

  /* ── Colour helpers ───────────────────────────────────────────────────── */
  const TIER_COLOR = { GREEN: '#10b981', YELLOW: '#f59e0b', RED: '#ef4444' };
  const TIER_EMOJI = { GREEN: '✅', YELLOW: '⚠️', RED: '🔴' };

  function pctColor(pct) {
    if (pct < 60) return '#10b981';
    if (pct < 85) return '#f59e0b';
    return '#ef4444';
  }

  /* ── HTML helpers ─────────────────────────────────────────────────────── */
  function badge(tier) {
    return `<span class="tier-badge tier-${tier}">${TIER_EMOJI[tier] || ''} ${tier}</span>`;
  }

  function fmtDate(iso) {
    if (!iso) return '–';
    try {
      return new Date(iso).toLocaleString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    } catch { return iso.slice(0, 16); }
  }

  function conclusionClass(c) {
    if (c === 'success')  return 'conclusion-success';
    if (c === 'failure')  return 'conclusion-failure';
    return 'conclusion-other';
  }

  /* ── Main render ──────────────────────────────────────────────────────── */
  function render(d) {
    const b = d.budget;
    const tc = d.tier_counts;
    const pct = b.pct_used;
    const fillColor = pctColor(pct);
    const month = d.month || '—';

    /* stat cards */
    const cards = `
<div class="dash-grid">
  <div class="stat-card ${pct < 60 ? 'card-green' : pct < 85 ? 'card-yellow' : 'card-red'}">
    <div class="label">Used this month</div>
    <div class="value">${b.used_minutes.toLocaleString()}</div>
    <div class="sub">of ${b.total_minutes.toLocaleString()} min (${pct}%)</div>
  </div>
  <div class="stat-card card-blue">
    <div class="label">Remaining</div>
    <div class="value">${b.remaining_minutes.toLocaleString()}</div>
    <div class="sub">min left in ${month}</div>
  </div>
  <div class="stat-card card-green">
    <div class="label">Green runs</div>
    <div class="value">${tc.GREEN}</div>
    <div class="sub">auto-approved this month</div>
  </div>
  <div class="stat-card card-yellow">
    <div class="label">Yellow runs</div>
    <div class="value">${tc.YELLOW}</div>
    <div class="sub">warned this month</div>
  </div>
  <div class="stat-card card-red">
    <div class="label">Red runs</div>
    <div class="value">${tc.RED}</div>
    <div class="sub">blocked this month</div>
  </div>
</div>`;

    /* budget bar */
    const bar = `
<div class="progress-wrap">
  <div class="progress-bar-bg">
    <div class="progress-bar-fill" style="width:${Math.min(pct,100)}%;background:${fillColor};">
      ${pct >= 15 ? pct + '%' : ''}
    </div>
  </div>
  <div class="progress-label">
    <span>0 min</span>
    <span style="color:${fillColor};font-weight:700;">${b.used_minutes.toLocaleString()} / ${b.total_minutes.toLocaleString()} min</span>
    <span>${b.total_minutes.toLocaleString()} min</span>
  </div>
</div>`;

    /* gated workflows table */
    const gwRows = (d.gated_workflows || []).map(w => `
<tr>
  <td><a href="https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/${w.file}" target="_blank" rel="noopener">${w.name}</a></td>
  <td>${badge(w.tier)}</td>
  <td style="text-align:right;font-variant-numeric:tabular-nums;">${w.effective_minutes}</td>
  <td>${w.runner}</td>
  <td style="text-align:center;">${w.pushes_to_ghcr ? '📦 yes' : '—'}</td>
</tr>`).join('');

    const gwTable = `
<table class="wf-table">
  <thead><tr>
    <th>Workflow</th><th>Tier</th><th>Eff. min</th><th>Runner</th><th>GHCR push</th>
  </tr></thead>
  <tbody>${gwRows}</tbody>
</table>`;

    /* recent runs table */
    const rrRows = (d.recent_runs || []).slice(0, 15).map(r => `
<tr>
  <td><a href="${r.html_url}" target="_blank" rel="noopener">${r.name || '—'}</a></td>
  <td>${badge(r.tier)}</td>
  <td style="text-align:right;font-variant-numeric:tabular-nums;">${r.effective_minutes}</td>
  <td class="${conclusionClass(r.conclusion)}">${r.conclusion || '—'}</td>
  <td style="font-size:.8em;opacity:.7;">${fmtDate(r.created_at)}</td>
</tr>`).join('');

    const rrTable = rrRows ? `
<table class="runs-table">
  <thead><tr><th>Workflow</th><th>Tier</th><th>Eff. min</th><th>Result</th><th>Started</th></tr></thead>
  <tbody>${rrRows}</tbody>
</table>` : '<p style="opacity:.6;font-size:.9rem;">No recent runs found.</p>';

    /* assemble */
    const html = `
<h2 style="margin-top:0;">📊 Monthly Budget — ${month}</h2>
${bar}
${cards}

<div class="charts-row">
  <div class="chart-box">
    <div class="chart-title">Tier breakdown (this month)</div>
    <canvas id="tierChart" height="220"></canvas>
  </div>
  <div class="chart-box">
    <div class="chart-title">Daily usage — last 30 days (effective min)</div>
    <canvas id="trendChart" height="220"></canvas>
  </div>
</div>

<h3>🔴 Gated Workflows</h3>
<p style="font-size:.88rem;opacity:.7;">These workflows require stakeholder approval before running. Check the
<a href="COST_GOVERNANCE.md">Cost Governance Policy</a> for details.</p>
${gwTable}

<h3>🕒 Recent Workflow Runs</h3>
${rrTable}

<div class="dash-meta">
  Generated: ${new Date(d.generated_at).toLocaleString()} ·
  <a href="https://github.com/Aries-Serpent/_codex_/blob/main/scripts/ci/generate_cost_dashboard_data.py"
     target="_blank" rel="noopener">data script</a>
</div>`;

    document.getElementById('cost-dashboard').innerHTML = html;
    _drawCharts(d, tc);
  }

  function _drawCharts(d, tc) {
    /* Tier donut */
    const tierCtx = document.getElementById('tierChart');
    if (tierCtx) {
      const isDark = document.documentElement.getAttribute('data-md-color-scheme') === 'slate';
      new Chart(tierCtx, {
        type: 'doughnut',
        data: {
          labels: ['🟢 GREEN', '🟡 YELLOW', '🔴 RED'],
          datasets: [{
            data: [tc.GREEN, tc.YELLOW, tc.RED],
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
            borderWidth: 0,
          }]
        },
        options: {
          cutout: '65%',
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: isDark ? '#d1d5db' : '#374151', font: { size: 12 } }
            },
            tooltip: {
              callbacks: {
                label: ctx => ` ${ctx.label}: ${ctx.parsed} runs`
              }
            }
          }
        }
      });
    }

    /* Trend bar */
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx && d.trend && d.trend.length) {
      const isDark = document.documentElement.getAttribute('data-md-color-scheme') === 'slate';
      const labels = d.trend.map(t => {
        const [, m, day] = t.date.split('-');
        return `${m}/${day}`;
      });
      const values = d.trend.map(t => t.minutes);

      new Chart(trendCtx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Effective minutes',
            data: values,
            backgroundColor: values.map(v =>
              v < 30 ? '#10b981' : v < 90 ? '#f59e0b' : '#ef4444'
            ),
            borderRadius: 4,
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: ctx => ` ${ctx.parsed.y.toFixed(1)} eff-min`
              }
            }
          },
          scales: {
            x: { ticks: { color: isDark ? '#9ca3af' : '#6b7280', maxRotation: 45, font: { size: 10 } }, grid: { display: false } },
            y: { ticks: { color: isDark ? '#9ca3af' : '#6b7280', font: { size: 10 } }, beginAtZero: true }
          }
        }
      });
    } else if (trendCtx) {
      trendCtx.parentElement.innerHTML += '<p style="opacity:.5;font-size:.85rem;">No trend data available yet.</p>';
    }
  }

  /* ── Fetch & render ───────────────────────────────────────────────────── */
  fetch(DATA_URL)
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(render)
    .catch(err => {
      document.getElementById('cost-dashboard').innerHTML = `
<div style="padding:2rem;text-align:center;opacity:.6;">
  <p>⚠️ Could not load cost data (<code>${err.message}</code>).</p>
  <p style="font-size:.85rem;">The dashboard data is generated at Pages build time.
  If you are viewing a preview build, the data file may not yet be present.</p>
  <p style="font-size:.85rem;">
    <a href="https://github.com/Aries-Serpent/_codex_/blob/main/docs/ops/COST_GOVERNANCE.md">
      View Cost Governance Policy
    </a>
  </p>
</div>`;
    });
})();
</script>
