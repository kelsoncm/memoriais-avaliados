/**
 * RSC-TAE Dashboard - Interactive Analytics Controller (IFRN)
 * Uses Chart.js for data visualization and handles real-time filtering,
 * KPI metrics calculation, and tabular exploration.
 */

(function () {
  'use strict';

  // Global State
  let rawSummaryData = null;
  let campusData = [];
  let cargoData = [];
  let chartInstances = {};

  // Color Constants (IFRN Brand Palette)
  const COLORS = {
    greenPrimary: '#006633',
    greenLight: '#10a352',
    greenSoft: 'rgba(0, 102, 51, 0.15)',
    bluePrimary: '#0ea5e9',
    amberPrimary: '#f59e0b',
    purplePrimary: '#8b5cf6',
    slate900: '#0f172a',
    slate500: '#64748b',
    slate200: '#e2e8f0',
    niveis: {
      'RSC-VI': '#006633',
      'RSC-V': '#0ea5e9',
      'RSC-IV': '#8b5cf6',
      'RSC-III': '#f59e0b',
      'RSC-II': '#ec4899',
      'RSC-I': '#64748b'
    },
    tipoCampus: {
      'Reitoria': '#004d26',
      'Capital': '#008744',
      'Interior': '#0ea5e9',
      'Outro': '#94a3b8'
    }
  };

  /**
   * Resolve multiple fallback candidate URLs for dataset assets
   */
  function getCandidateUrls(filename) {
    const base = window.SITE_BASEURL || '';
    const cleanBase = base.endsWith('/') ? base.slice(0, -1) : base;
    return [
      `${cleanBase}/data/${filename}`,
      `data/${filename}`,
      `./data/${filename}`,
      `../docs/data/${filename}`,
      `../data/processed/${filename}`,
      `/data/${filename}`,
      `/docs/data/${filename}`
    ];
  }

  /**
   * Fetch with fallback strategy across candidate URLs
   */
  async function fetchWithFallback(filename, isJson = true) {
    const urls = getCandidateUrls(filename);
    for (const url of urls) {
      try {
        const res = await fetch(url);
        if (res.ok) {
          return isJson ? await res.json() : await res.text();
        }
      } catch (err) {
        // Try next candidate url
      }
    }
    throw new Error(`Não foi possível localizar o arquivo ${filename} em nenhuma das rotas relativas.`);
  }

  /**
   * Fetch aggregated summary JSON and CSV fallbacks
   */
  async function loadData() {
    try {
      rawSummaryData = await fetchWithFallback('agg_summary.json', true);
      
      // Load CSV datasets for tables
      await loadCsvDatasets();

      initDashboard();
    } catch (err) {
      console.error('Erro ao carregar dados do dashboard:', err);
      showDataLoadError(err);
    }
  }

  /**
   * Loads CSV datasets for advanced table views
   */
  async function loadCsvDatasets() {
    try {
      const campusText = await fetchWithFallback('agg_campus_mes.csv', false);
      if (campusText) campusData = parseCsv(campusText);
    } catch (e) {
      console.warn('Usando dados embutidos de Campus do JSON:', e.message);
    }

    try {
      const cargoText = await fetchWithFallback('agg_cargo_nivel.csv', false);
      if (cargoText) cargoData = parseCsv(cargoText);
    } catch (e) {
      console.warn('Usando dados embutidos de Cargo do JSON:', e.message);
    }
  }

  /**
   * CSV parser with quotes handling
   */
  function parseCsv(text) {
    const lines = text.trim().split('\n');
    if (lines.length < 2) return [];
    const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
    return lines.slice(1).map(line => {
      const values = [];
      let inQuotes = false;
      let curr = '';
      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
          inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
          values.push(curr.trim().replace(/^"|"$/g, ''));
          curr = '';
        } else {
          curr += char;
        }
      }
      values.push(curr.trim().replace(/^"|"$/g, ''));

      const row = {};
      headers.forEach((h, idx) => {
        row[h] = values[idx] || '';
      });
      return row;
    });
  }

  /**
   * Initialize UI, KPI cards, Filters and Charts
   */
  function initDashboard() {
    populateFilterDropdowns();
    updateDashboardView();
    setupEventListeners();
  }

  /**
   * Populate Campus filter select
   */
  function populateFilterDropdowns() {
    const campusSelect = document.getElementById('filterCampus');
    if (!campusSelect || !rawSummaryData.ranking_campi) return;

    campusSelect.innerHTML = '<option value="">Todos os Campi</option>';
    rawSummaryData.ranking_campi.forEach(item => {
      const opt = document.createElement('option');
      opt.value = item.campus;
      opt.textContent = `${item.campus} (${item.total})`;
      campusSelect.appendChild(opt);
    });
  }

  /**
   * Computes filtered subset and updates KPIs and Charts dynamically
   */
  function updateDashboardView() {
    const tipoFilter = document.getElementById('filterTipoCampus')?.value || '';
    const campusFilter = document.getElementById('filterCampus')?.value || '';

    let items = rawSummaryData.ranking_campi || [];
    
    // Map campus type from campusData if available
    const tipoMap = {};
    campusData.forEach(cd => { if (cd.campus) tipoMap[cd.campus] = cd.tipo_campus; });

    if (tipoFilter) {
      items = items.filter(c => {
        const t = tipoMap[c.campus] || (c.campus === 'Reitoria' ? 'Reitoria' : (c.campus.includes('Natal') ? 'Capital' : 'Interior'));
        return t === tipoFilter;
      });
    }

    if (campusFilter) {
      items = items.filter(c => c.campus === campusFilter);
    }

    // Dynamic KPI Calculation
    const totalAvaliados = items.reduce((acc, curr) => acc + (curr.total || curr.total_processos || 0), 0);
    const totalCampi = items.length;

    const totalEl = document.getElementById('kpiTotalAvaliados');
    if (totalEl) totalEl.textContent = totalAvaliados.toLocaleString('pt-BR');

    const ativosEl = document.getElementById('kpiTotalAtivos');
    if (ativosEl && rawSummaryData.meta) {
      ativosEl.textContent = (rawSummaryData.meta.total_tae_ativos || 1360).toLocaleString('pt-BR');
    }

    const cobEl = document.getElementById('kpiTaxaCobertura');
    if (cobEl && rawSummaryData.meta) {
      cobEl.textContent = `${rawSummaryData.meta.taxa_cobertura_global_pct || 35.9}%`;
    }

    const campiEl = document.getElementById('kpiTotalCampi');
    if (campiEl) campiEl.textContent = totalCampi;

    const cargosEl = document.getElementById('kpiTotalCargos');
    if (cargosEl && rawSummaryData.meta) {
      const atend = rawSummaryData.meta.total_cargos_atendidos || 55;
      const exist = rawSummaryData.meta.total_cargos_existentes || 92;
      cargosEl.textContent = `${atend} / ${exist}`;
    }

    const topNivelEl = document.getElementById('kpiTopNivel');
    if (topNivelEl && rawSummaryData.distribuicao_niveis) {
      const topPair = Object.entries(rawSummaryData.distribuicao_niveis).sort((a, b) => b[1] - a[1])[0];
      if (topPair) {
        const pct = ((topPair[1] / (rawSummaryData.meta?.total_geral_avaliados || 488)) * 100).toFixed(1);
        topNivelEl.textContent = `${topPair[0]} (${pct}%)`;
      }
    }

    renderAllCharts(items);
  }

  /**
   * Render all Chart.js visualizations
   */
  function renderAllCharts(filteredItems) {
    destroyExistingCharts();

    renderNivelDonutChart();
    renderTipoCampusChart();
    renderCampusRankingChart(filteredItems);
    renderCampusNivelStackedChart(filteredItems);
    renderTopCargosChart();
    renderClassesChart();
  }

  function destroyExistingCharts() {
    Object.keys(chartInstances).forEach(key => {
      if (chartInstances[key]) {
        chartInstances[key].destroy();
      }
    });
    chartInstances = {};
  }

  /**
   * Chart 1: Distribuição Geral por Nível RSC (Doughnut)
   */
  function renderNivelDonutChart() {
    const ctx = document.getElementById('chartNiveis')?.getContext('2d');
    if (!ctx) return;

    const dataObj = rawSummaryData.distribuicao_niveis || {};
    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);
    const bgColors = labels.map(l => COLORS.niveis[l] || '#64748b');

    chartInstances.niveis = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 14, font: { family: 'Inter', size: 12, weight: '500' } }
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const val = ctx.raw;
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((val / total) * 100).toFixed(1);
                return ` ${ctx.label}: ${val} processos (${pct}%)`;
              }
            }
          }
        },
        cutout: '62%'
      }
    });
  }

  /**
   * Chart 2: Distribuição por Tipo de Campus (Doughnut)
   */
  function renderTipoCampusChart() {
    const ctx = document.getElementById('chartTipoCampus')?.getContext('2d');
    if (!ctx) return;

    const dataObj = rawSummaryData.distribuicao_tipo_campus || {};
    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);
    const bgColors = labels.map(l => COLORS.tipoCampus[l] || '#94a3b8');

    chartInstances.tipoCampus = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 14, font: { family: 'Inter', size: 12, weight: '500' } }
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const val = ctx.raw;
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((val / total) * 100).toFixed(1);
                return ` ${ctx.label}: ${val} memoriais (${pct}%)`;
              }
            }
          }
        },
        cutout: '62%'
      }
    });
  }

  /**
   * Chart 3: Ranking de Processos por Campus (Horizontal Bar)
   */
  function renderCampusRankingChart(items) {
    const ctx = document.getElementById('chartCampusRanking')?.getContext('2d');
    if (!ctx) return;

    const topItems = items.slice(0, 15);
    const labels = topItems.map(i => i.campus);
    const values = topItems.map(i => i.total);

    chartInstances.campusRanking = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Total de Processos',
          data: values,
          backgroundColor: labels.map((l, idx) => idx === 0 ? COLORS.greenPrimary : 'rgba(0, 102, 51, 0.75)'),
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.raw} memoriais avaliados`
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: COLORS.slate200 },
            ticks: { font: { family: 'Inter', size: 11 } }
          },
          y: {
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 12, weight: '500' } }
          }
        }
      }
    });
  }

  /**
   * Chart 4: Níveis Pretendidos por Campus (Stacked Bar)
   */
  function renderCampusNivelStackedChart(items) {
    const ctx = document.getElementById('chartCampusNivel')?.getContext('2d');
    if (!ctx || !rawSummaryData.campus_niveis) return;

    const targetCampi = items.slice(0, 10).map(i => i.campus);
    const rawCross = rawSummaryData.campus_niveis.filter(cn => targetCampi.includes(cn.campus));

    const datasetVI = [];
    const datasetV = [];
    const datasetIII = [];

    targetCampi.forEach(cName => {
      const match = rawCross.find(r => r.campus === cName) || {};
      datasetVI.push(match['RSC-VI'] || 0);
      datasetV.push(match['RSC-V'] || 0);
      datasetIII.push(match['RSC-III'] || 0);
    });

    chartInstances.campusNivel = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: targetCampi,
        datasets: [
          {
            label: 'RSC-VI',
            data: datasetVI,
            backgroundColor: COLORS.niveis['RSC-VI'],
            borderRadius: 4
          },
          {
            label: 'RSC-V',
            data: datasetV,
            backgroundColor: COLORS.niveis['RSC-V'],
            borderRadius: 4
          },
          {
            label: 'RSC-III',
            data: datasetIII,
            backgroundColor: COLORS.niveis['RSC-III'],
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            stacked: true,
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 11 } }
          },
          y: {
            stacked: true,
            beginAtZero: true,
            grid: { color: COLORS.slate200 },
            ticks: { font: { family: 'Inter', size: 11 } }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 12, font: { family: 'Inter', size: 11 } }
          }
        }
      }
    });
  }

  /**
   * Chart 5: Top Cargos com Processos Avaliados (Horizontal Bar)
   */
  function renderTopCargosChart() {
    const ctx = document.getElementById('chartTopCargos')?.getContext('2d');
    if (!ctx || !rawSummaryData.top_cargos) return;

    const top10 = rawSummaryData.top_cargos.slice(0, 10);
    const labels = top10.map(i => i.cargo);
    const values = top10.map(i => i.total_avaliados || i.total || 0);

    chartInstances.topCargos = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Total de Memoriais',
          data: values,
          backgroundColor: '#0284c7',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const item = top10[ctx.dataIndex];
                if (item && item.total_ativos) {
                  return ` ${item.total_avaliados} avaliados de ${item.total_ativos} ativos (${item.taxa_adesao_pct}% adesão)`;
                }
                return ` ${ctx.raw} memoriais`;
              }
            }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: COLORS.slate200 },
            ticks: { font: { family: 'Inter', size: 11 } }
          },
          y: {
            grid: { display: false },
            ticks: { font: { family: 'Inter', size: 11, weight: '500' } }
          }
        }
      }
    });
  }

  /**
   * Chart 6: Distribuição por Classe do PCCTAE (Doughnut)
   */
  function renderClassesChart() {
    const ctx = document.getElementById('chartClasses')?.getContext('2d');
    if (!ctx) return;

    const dataObj = rawSummaryData.distribuicao_classes || {};
    const labels = Object.keys(dataObj);
    const values = Object.values(dataObj);
    const bgColors = ['#10b981', '#3b82f6', '#8b5cf6'];

    chartInstances.classes = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 14, font: { family: 'Inter', size: 12, weight: '500' } }
          },
          tooltip: {
            callbacks: {
              label: function (ctx) {
                const cl = ctx.label;
                const adesao = rawSummaryData.adesao_classes?.[cl];
                if (adesao) {
                  return ` ${cl}: ${adesao.total_avaliados} avaliados / ${adesao.total_ativos} ativos (${adesao.taxa_adesao_pct}% adesão)`;
                }
                const val = ctx.raw;
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((val / total) * 100).toFixed(1);
                return ` ${cl}: ${val} memoriais (${pct}%)`;
              }
            }
          }
        },
        cutout: '62%'
      }
    });
  }

  /**
   * Render Interactive Data Table
   */
  function renderDataTable(viewType) {
    const thead = document.getElementById('tableThead');
    const tbody = document.getElementById('tableTbody');
    const searchInput = document.getElementById('tableSearchInput')?.value.toLowerCase() || '';

    if (!thead || !tbody) return;

    const totalGeral = rawSummaryData.meta?.total_geral_avaliados || 488;

    if (viewType === 'campus') {
      thead.innerHTML = `
        <tr>
          <th>Campus / Unidade</th>
          <th>Lotação</th>
          <th>TAEs Ativos</th>
          <th>Memoriais Avaliados</th>
          <th>Taxa de Adesão</th>
          <th>Participação (% Total)</th>
        </tr>
      `;

      let rows = (rawSummaryData.ranking_campi && rawSummaryData.ranking_campi.length > 0) ? rawSummaryData.ranking_campi : campusData;

      if (searchInput) {
        rows = rows.filter(r => (r.campus || '').toLowerCase().includes(searchInput) || (r.tipo_campus || '').toLowerCase().includes(searchInput));
      }

      tbody.innerHTML = rows.map(r => {
        const totalProc = r.total_processos !== undefined ? r.total_processos : (r.total || 0);
        const ativos = r.total_ativos || '—';
        const taxa = r.taxa_adesao_pct !== undefined ? `${r.taxa_adesao_pct}%` : '—';
        const part = r.participacao_pct !== undefined ? `${r.participacao_pct}%` : `${((totalProc / totalGeral) * 100).toFixed(1)}%`;
        const badgeColor = Number(r.taxa_adesao_pct) >= 50 ? 'green' : (Number(r.taxa_adesao_pct) >= 30 ? 'blue' : 'amber');

        return `
        <tr>
          <td><strong>${r.campus}</strong></td>
          <td><span class="badge ${r.tipo_campus === 'Capital' ? 'green' : (r.tipo_campus === 'Reitoria' ? 'blue' : 'amber')}">${r.tipo_campus}</span></td>
          <td>${ativos}</td>
          <td><strong>${totalProc}</strong></td>
          <td><span class="badge ${badgeColor}">${taxa}</span></td>
          <td><span class="badge slate">${part}</span></td>
        </tr>
        `;
      }).join('');
    } else {
      thead.innerHTML = `
        <tr>
          <th>Cargo PCCTAE</th>
          <th>Classe</th>
          <th>TAEs Ativos</th>
          <th>Memoriais Avaliados</th>
          <th>Taxa de Adesão</th>
          <th>Participação (% Total)</th>
        </tr>
      `;

      let rows = (rawSummaryData.top_cargos && rawSummaryData.top_cargos.length > 0) ? rawSummaryData.top_cargos : cargoData;

      if (searchInput) {
        rows = rows.filter(r => (r.cargo || '').toLowerCase().includes(searchInput) || (r.classe_cargo || '').toLowerCase().includes(searchInput));
      }

      tbody.innerHTML = rows.map(r => {
        const totalAval = r.total_avaliados !== undefined ? r.total_avaliados : (r.total || r.total_processos || 0);
        const ativos = r.total_ativos || '—';
        const taxa = r.taxa_adesao_pct !== undefined ? `${r.taxa_adesao_pct}%` : '—';
        const part = r.participacao_pct !== undefined ? `${r.participacao_pct}%` : `${((totalAval / totalGeral) * 100).toFixed(1)}%`;
        const badgeColor = Number(r.taxa_adesao_pct) >= 50 ? 'green' : (Number(r.taxa_adesao_pct) >= 30 ? 'blue' : 'amber');

        return `
        <tr>
          <td><strong>${r.cargo}</strong></td>
          <td><span class="badge blue">${r.classe_cargo || 'Classe D'}</span></td>
          <td>${ativos}</td>
          <td><strong>${totalAval}</strong></td>
          <td><span class="badge ${badgeColor}">${taxa}</span></td>
          <td><span class="badge slate">${part}</span></td>
        </tr>
        `;
      }).join('');
    }
  }

  /**
   * Setup UI Event Listeners
   */
  function setupEventListeners() {
    const filterTipo = document.getElementById('filterTipoCampus');
    const filterCampus = document.getElementById('filterCampus');
    const btnReset = document.getElementById('btnResetFilters');
    const tableSearch = document.getElementById('tableSearchInput');
    const tabCampus = document.getElementById('tabViewCampus');
    const tabCargo = document.getElementById('tabViewCargo');

    let currentTableTab = 'campus';

    if (filterTipo) filterTipo.addEventListener('change', () => updateDashboardView());
    if (filterCampus) filterCampus.addEventListener('change', () => updateDashboardView());

    if (btnReset) {
      btnReset.addEventListener('click', () => {
        if (filterTipo) filterTipo.value = '';
        if (filterCampus) filterCampus.value = '';
        if (tableSearch) tableSearch.value = '';
        updateDashboardView();
        renderDataTable(currentTableTab);
      });
    }

    if (tableSearch) {
      tableSearch.addEventListener('input', () => {
        renderDataTable(currentTableTab);
      });
    }

    if (tabCampus && tabCargo) {
      tabCampus.addEventListener('click', () => {
        currentTableTab = 'campus';
        tabCampus.classList.add('active');
        tabCargo.classList.remove('active');
        renderDataTable('campus');
      });

      tabCargo.addEventListener('click', () => {
        currentTableTab = 'cargo';
        tabCargo.classList.add('active');
        tabCampus.classList.remove('active');
        renderDataTable('cargo');
      });
    }
  }

  function showDataLoadError(err) {
    const mainEl = document.querySelector('.main-content');
    if (mainEl) {
      const banner = document.createElement('div');
      banner.className = 'callout warning';
      banner.innerHTML = `
        <strong>Aviso de Carregamento de Dados:</strong> Não foi possível carregar os arquivos agregados (${err.message}).
        Verifique se o script <code>src/process.py</code> foi executado previamente para gerar os dados em <code>docs/data/</code>.
      `;
      mainEl.prepend(banner);
    }
  }

  // Initialize on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadData);
  } else {
    loadData();
  }
})();
