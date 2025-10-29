// Portfolio page logic

let allocationChart = null;

// Load portfolio data
async function loadPortfolio() {
    const modelSelect = document.getElementById('portfolio-model-select');
    const modelChoice = modelSelect?.value || null;

    try {
        const snapshot = await api.getLatestSnapshot(modelChoice);

        // Update stats
        document.getElementById('portfolio-total-value').textContent = formatCurrency(snapshot.total_value);
        document.getElementById('portfolio-cash').textContent = formatCurrency(snapshot.cash_balance);

        const realizedElement = document.getElementById('portfolio-realized-pnl');
        realizedElement.textContent = formatCurrency(snapshot.realized_pnl);
        realizedElement.className = 'stat-value ' + (snapshot.realized_pnl >= 0 ? 'text-success' : 'text-danger');

        const unrealizedElement = document.getElementById('portfolio-unrealized-pnl');
        unrealizedElement.textContent = formatCurrency(snapshot.unrealized_pnl);
        unrealizedElement.className = 'stat-value ' + (snapshot.unrealized_pnl >= 0 ? 'text-success' : 'text-danger');

        // Load holdings table
        loadHoldings(snapshot);

        // Load allocation chart
        loadAllocationChart(snapshot);

    } catch (error) {
        console.error('Failed to load portfolio:', error);
        showError('Failed to load portfolio data');
    }
}

// Load holdings table
function loadHoldings(snapshot) {
    const table = document.getElementById('holdings-table');
    const positions = snapshot.positions || {};

    const holdings = Object.entries(positions)
        .filter(([symbol]) => symbol !== 'cash')
        .map(([symbol, data]) => ({
            symbol,
            quantity: data.quantity || 0,
            value: data.value || 0,
            unrealized_pnl: data.unrealized_pnl || 0,
            current_price: data.current_price || 0,
        }));

    if (holdings.length === 0) {
        table.innerHTML = '<tr><td colspan="6" class="loading">No holdings available.</td></tr>';
        return;
    }

    // Calculate percentage of portfolio
    const totalValue = snapshot.total_value;

    table.innerHTML = holdings.map(holding => {
        const percentOfPortfolio = (holding.value / totalValue) * 100;
        return `
            <tr>
                <td><strong>${holding.symbol}</strong></td>
                <td>${formatNumber(holding.quantity, 0)}</td>
                <td>${formatCurrency(holding.current_price)}</td>
                <td>${formatCurrency(holding.value)}</td>
                <td class="${holding.unrealized_pnl >= 0 ? 'text-success' : 'text-danger'}">
                    ${formatCurrency(holding.unrealized_pnl)}
                </td>
                <td>${formatPercent(percentOfPortfolio, 2)}</td>
            </tr>
        `;
    }).join('');
}

// Load asset allocation chart
function loadAllocationChart(snapshot) {
    const positions = snapshot.positions || {};

    const holdings = Object.entries(positions)
        .filter(([symbol]) => symbol !== 'cash')
        .map(([symbol, data]) => ({
            symbol,
            value: data.value || 0,
        }))
        .sort((a, b) => b.value - a.value);

    // Take top 10 and group others
    const top10 = holdings.slice(0, 10);
    const others = holdings.slice(10).reduce((sum, h) => sum + h.value, 0);

    const labels = [...top10.map(h => h.symbol)];
    const values = [...top10.map(h => h.value)];

    if (others > 0) {
        labels.push('Others');
        values.push(others);
    }

    // Add cash
    if (snapshot.cash_balance > 0) {
        labels.push('Cash');
        values.push(snapshot.cash_balance);
    }

    if (allocationChart) {
        allocationChart.destroy();
    }

    const ctx = document.getElementById('allocation-chart');
    if (!ctx) return;

    allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444',
                    '#06b6d4', '#ec4899', '#6366f1', '#14b8a6', '#f97316',
                    '#9ca3af'
                ],
                borderWidth: 2,
                borderColor: '#1a1f2e'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(2);
                            return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize portfolio page
document.addEventListener('DOMContentLoaded', () => {
    loadPortfolio();
    // Refresh every 30 seconds
    setInterval(loadPortfolio, 30000);
});
