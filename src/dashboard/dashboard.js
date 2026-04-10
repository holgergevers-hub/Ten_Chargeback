/* Ten Group Chargeback Risk Dashboard */

const COLORS = {
    blue: '#3b82f6',
    green: '#22c55e',
    red: '#ef4444',
    amber: '#f59e0b',
    purple: '#a855f7',
    cyan: '#06b6d4',
    pink: '#ec4899',
    indigo: '#6366f1',
    teal: '#14b8a6',
};

const CHART_COLORS = [
    COLORS.blue, COLORS.green, COLORS.amber,
    COLORS.red, COLORS.purple, COLORS.cyan,
    COLORS.pink, COLORS.indigo, COLORS.teal,
];

Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#334155';
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

function formatUSD(val) {
    return '$' + val.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function formatPct(val, total) {
    return (val / total * 100).toFixed(1) + '%';
}

function el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) {
        for (const [k, v] of Object.entries(attrs)) {
            if (k === 'className') node.className = v;
            else if (k === 'textContent') node.textContent = v;
            else node.setAttribute(k, v);
        }
    }
    if (children) {
        for (const child of Array.isArray(children) ? children : [children]) {
            if (typeof child === 'string') node.appendChild(document.createTextNode(child));
            else if (child) node.appendChild(child);
        }
    }
    return node;
}

async function loadData() {
    // Try fetching from file first (works with local HTTP server)
    for (const path of ['dashboard_data.json', '../../data/clean/dashboard_data.json']) {
        try {
            const resp = await fetch(path);
            if (resp.ok) return await resp.json();
        } catch (e) { /* continue */ }
    }
    // Fall back to embedded data (works via htmlpreview, file://, etc.)
    if (window.DASHBOARD_DATA) return window.DASHBOARD_DATA;
    console.error('Could not load dashboard_data.json');
    return null;
}

function renderKPIs(data) {
    const total = data.total_usd;
    const count = data.total_count;
    const chargebackAmt = (data.by_category.find(c => c.category === 'Chargeback') || {}).amount_usd || 0;
    const fraudAmt = (data.by_category.find(c => c.category === 'Fraud') || {}).amount_usd || 0;
    const recoveredAmt = (data.by_category.find(c => c.category === 'Recovered') || {}).amount_usd || 0;
    const recoveryRate = total > 0 ? (recoveredAmt / total * 100).toFixed(1) : '0.0';

    const kpis = [
        { label: 'Total Chargeback Exposure', value: formatUSD(total), detail: count + ' disputes across 3 platforms', cls: 'blue' },
        { label: 'Chargeback Amount', value: formatUSD(chargebackAmt), detail: formatPct(chargebackAmt, total) + ' of total exposure', cls: 'red' },
        { label: 'Fraud Notifications', value: formatUSD(fraudAmt), detail: (data.by_category.find(c => c.category === 'Fraud')?.count || 0) + ' fraud alerts', cls: 'amber' },
        { label: 'Recovery Rate', value: recoveryRate + '%', detail: formatUSD(recoveredAmt) + ' recovered', cls: 'green' },
    ];

    const row = document.getElementById('kpiRow');
    while (row.firstChild) row.removeChild(row.firstChild);

    for (const k of kpis) {
        row.appendChild(
            el('div', { className: 'kpi-card ' + k.cls }, [
                el('div', { className: 'kpi-label', textContent: k.label }),
                el('div', { className: 'kpi-value', textContent: k.value }),
                el('div', { className: 'kpi-detail', textContent: k.detail }),
            ])
        );
    }
}

function renderMonthlyTrend(data) {
    const months = data.monthly_trend.map(m => m.month);
    const amounts = data.monthly_trend.map(m => m.amount_usd);
    const counts = data.monthly_trend.map(m => m.count);

    new Chart(document.getElementById('monthlyTrend'), {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'Amount (USD)',
                    data: amounts,
                    backgroundColor: COLORS.blue + '80',
                    borderColor: COLORS.blue,
                    borderWidth: 1,
                    borderRadius: 4,
                    yAxisID: 'y',
                },
                {
                    label: 'Count',
                    data: counts,
                    type: 'line',
                    borderColor: COLORS.amber,
                    backgroundColor: COLORS.amber + '20',
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: COLORS.amber,
                    fill: true,
                    yAxisID: 'y1',
                },
            ],
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            scales: {
                y: {
                    position: 'left',
                    title: { display: true, text: 'Amount (USD)' },
                    ticks: { callback: v => formatUSD(v) },
                    grid: { color: '#334155' },
                },
                y1: {
                    position: 'right',
                    title: { display: true, text: 'Count' },
                    grid: { drawOnChartArea: false },
                },
                x: { grid: { color: '#334155' } },
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ctx => ctx.dataset.label === 'Amount (USD)'
                            ? ctx.dataset.label + ': ' + formatUSD(ctx.parsed.y)
                            : ctx.dataset.label + ': ' + ctx.parsed.y,
                    },
                },
            },
        },
    });
}

function renderByPlatform(data) {
    new Chart(document.getElementById('byPlatform'), {
        type: 'bar',
        data: {
            labels: data.by_platform.map(p => p.platform),
            datasets: [{
                label: 'Amount (USD)',
                data: data.by_platform.map(p => p.amount_usd),
                backgroundColor: [COLORS.blue, COLORS.green, COLORS.purple],
                borderRadius: 6,
            }],
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => formatUSD(ctx.parsed.x) } },
            },
            scales: {
                x: { ticks: { callback: v => formatUSD(v) }, grid: { color: '#334155' } },
                y: { grid: { display: false } },
            },
        },
    });
}

function renderByCategory(data) {
    new Chart(document.getElementById('byCategory'), {
        type: 'doughnut',
        data: {
            labels: data.by_category.map(c => c.category),
            datasets: [{
                data: data.by_category.map(c => c.amount_usd),
                backgroundColor: [COLORS.red, COLORS.amber, COLORS.green, COLORS.blue],
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            cutout: '60%',
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ctx => ctx.label + ': ' + formatUSD(ctx.parsed) + ' (' + formatPct(ctx.parsed, data.total_usd) + ')',
                    },
                },
            },
        },
    });
}

function renderByRegion(data) {
    const regions = data.by_region;
    new Chart(document.getElementById('byRegion'), {
        type: 'bar',
        data: {
            labels: regions.map(r => r.region),
            datasets: [{
                label: 'Amount (USD)',
                data: regions.map(r => r.amount_usd),
                backgroundColor: CHART_COLORS.slice(0, regions.length),
                borderRadius: 6,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: ctx => formatUSD(ctx.parsed.y) } },
            },
            scales: {
                y: { ticks: { callback: v => formatUSD(v) }, grid: { color: '#334155' } },
                x: { grid: { display: false } },
            },
        },
    });
}

function renderByCurrency(data) {
    new Chart(document.getElementById('byCurrency'), {
        type: 'doughnut',
        data: {
            labels: data.by_currency.map(c => c.currency),
            datasets: [{
                data: data.by_currency.map(c => c.amount_original),
                backgroundColor: CHART_COLORS.slice(0, data.by_currency.length),
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            cutout: '60%',
            plugins: {
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const item = data.by_currency[ctx.dataIndex];
                            return item.currency + ': ' + item.amount_original.toLocaleString() + ' (' + formatUSD(item.amount_usd) + ' USD)';
                        },
                    },
                },
            },
        },
    });
}

function renderMerchantTable(data) {
    const tbody = document.querySelector('#merchantTable tbody');
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);

    for (const m of data.by_merchant) {
        const tr = el('tr', null, [
            el('td', { textContent: m.merchant }),
            el('td', { textContent: m.platform }),
            el('td', { textContent: String(m.count) }),
            el('td', { className: 'amount-cell', textContent: formatUSD(m.amount_usd) }),
            el('td', { className: 'pct-cell', textContent: formatPct(m.amount_usd, data.total_usd) }),
        ]);
        tbody.appendChild(tr);
    }
}

function renderTypeTable(data) {
    const tbody = document.querySelector('#typeTable tbody');
    while (tbody.firstChild) tbody.removeChild(tbody.firstChild);

    for (const t of data.by_record_type) {
        const tr = el('tr', null, [
            el('td', { textContent: t.type }),
            el('td', { textContent: String(t.count) }),
            el('td', { className: 'amount-cell', textContent: formatUSD(t.amount_usd) }),
            el('td', { className: 'pct-cell', textContent: formatPct(t.amount_usd, data.total_usd) }),
        ]);
        tbody.appendChild(tr);
    }
}

function exportToPdf() {
    const btn = document.getElementById('exportPdf');
    btn.disabled = true;
    btn.textContent = 'Generating…';

    const element = document.body;

    const opt = {
        margin: [10, 10, 10, 10],
        filename: 'Ten_Group_Chargeback_Dashboard.pdf',
        image: { type: 'jpeg', quality: 0.95 },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: '#0f172a',
            logging: false,
        },
        jsPDF: {
            unit: 'mm',
            format: 'a3',
            orientation: 'landscape',
        },
        pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
    };

    html2pdf().set(opt).from(element).save().then(function () {
        btn.disabled = false;
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1v9M8 10L5 7M8 10l3-3M2 12v2h12v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg> Export PDF';
    });
}

async function init() {
    const data = await loadData();
    if (!data) {
        const msg = el('h1', { textContent: 'Error: Could not load dashboard_data.json' });
        msg.style.color = '#ef4444';
        msg.style.padding = '40px';
        document.body.appendChild(msg);
        return;
    }

    renderKPIs(data);
    renderMonthlyTrend(data);
    renderByPlatform(data);
    renderByCategory(data);
    renderByRegion(data);
    renderByCurrency(data);
    renderMerchantTable(data);
    renderTypeTable(data);
}

init();
