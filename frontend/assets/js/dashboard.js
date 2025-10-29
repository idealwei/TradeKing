// Dashboard page logic

let equityChart = null;
let currentScale = 'linear';

// Load all dashboard data
async function loadDashboard() {
    try {
        await Promise.all([
            loadModelPerformance(),
            loadLatestDecision(),
            loadStats(),
            loadEquityCurve(),
        ]);
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// Load overall statistics
async function loadStats() {
    try {
        const [decisions, models, portfolio] = await Promise.all([
            api.getLatestDecisions(1),
            api.getModelPerformance(),
            api.getLatestSnapshot().catch(() => null),
        ]);

        // Total decisions
        const totalDecisions = models.reduce((sum, m) => sum + m.total_decisions, 0);
        document.getElementById('total-decisions').textContent = formatNumber(totalDecisions, 0);

        // Portfolio value
        if (portfolio) {
            document.getElementById('portfolio-value').textContent = formatCurrency(portfolio.total_value);
            const pnlElement = document.getElementById('total-pnl');
            pnlElement.textContent = formatCurrency(portfolio.total_pnl);
            pnlElement.className = 'stat-value ' + (portfolio.total_pnl >= 0 ? 'text-success' : 'text-danger');
        }

        // Average response time
        const avgTime = models.reduce((sum, m) => sum + (m.avg_execution_time_ms || 0), 0) / models.length;
        document.getElementById('avg-time').textContent = `${formatNumber(avgTime, 0)}ms`;

    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Load model performance cards
async function loadModelPerformance() {
    try {
        const models = await api.getModelPerformance();
        const container = document.getElementById('models-grid');

        if (models.length === 0) {
            container.innerHTML = '<p class="loading">No model performance data available yet.</p>';
            return;
        }

        container.innerHTML = models.map(model => `
            <div class="model-card">
                <div class="model-header">
                    <div class="model-name">${model.model_choice}</div>
                    <div class="model-badge">Active</div>
                </div>
                <div class="model-stats">
                    <div class="model-stat">
                        <span>Total Decisions</span>
                        <span class="model-stat-value">${model.total_decisions}</span>
                    </div>
                    <div class="model-stat">
                        <span>Success Rate</span>
                        <span class="model-stat-value ${model.total_decisions > 0 ? 'text-success' : ''}">
                            ${model.total_decisions > 0 ? formatPercent((model.successful_decisions / model.total_decisions) * 100, 1) : '-'}
                        </span>
                    </div>
                    <div class="model-stat">
                        <span>Total P&L</span>
                        <span class="model-stat-value ${model.total_profit_loss >= 0 ? 'text-success' : 'text-danger'}">
                            ${formatCurrency(model.total_profit_loss)}
                        </span>
                    </div>
                    <div class="model-stat">
                        <span>Avg Exec Time</span>
                        <span class="model-stat-value">${formatNumber(model.avg_execution_time_ms || 0, 0)}ms</span>
                    </div>
                    <div class="model-stat">
                        <span>Last Decision</span>
                        <span class="model-stat-value text-muted">${formatTimestamp(model.last_decision_at)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load model performance:', error);
        document.getElementById('models-grid').innerHTML = '<p class="loading">Failed to load model performance.</p>';
    }
}

// Load latest decision
async function loadLatestDecision() {
    try {
        const modelFilter = document.getElementById('model-filter')?.value || '';
        const decisions = modelFilter
            ? await api.getDecisionsByFilter({ model_choice: modelFilter, limit: 1 })
            : await api.getLatestDecisions(1);

        const container = document.getElementById('latest-decision');

        if (decisions.length === 0) {
            container.innerHTML = '<p class="loading">No decisions available yet.</p>';
            return;
        }

        const decision = decisions[0];
        container.innerHTML = `
            <div class="decision-header">
                <div class="decision-meta">
                    <div class="decision-meta-item">
                        <strong>Model:</strong> ${decision.model_choice.toUpperCase()}
                    </div>
                    <div class="decision-meta-item">
                        <strong>Time:</strong> ${formatTimestamp(decision.timestamp)}
                    </div>
                    <div class="decision-meta-item">
                        <strong>Execution:</strong> ${formatNumber(decision.execution_time_ms || 0, 0)}ms
                    </div>
                    ${decision.symbols ? `
                    <div class="decision-meta-item">
                        <strong>Symbols:</strong> ${decision.symbols.join(', ')}
                    </div>
                    ` : ''}
                </div>
                ${decision.error_message ? `
                <span class="status-badge status-error">Error</span>
                ` : `
                <span class="status-badge status-success">Success</span>
                `}
            </div>
            <div class="decision-content">${decision.error_message || decision.decision || 'No decision content'}</div>
        `;
    } catch (error) {
        console.error('Failed to load latest decision:', error);
        document.getElementById('latest-decision').innerHTML = '<p class="loading">Failed to load latest decision.</p>';
    }
}

// Load equity curve
async function loadEquityCurve() {
    const modelSelect = document.getElementById('equity-model-select');
    const modelChoice = modelSelect?.value || 'gpt5';

    try {
        const data = await api.getEquityCurve(modelChoice);

        if (equityChart) {
            equityChart.destroy();
        }

        const ctx = document.getElementById('equity-chart');
        if (!ctx) return;

        equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: `${modelChoice.toUpperCase()} Portfolio Value`,
                    data: data.data_points.map(point => ({
                        x: new Date(point.timestamp),
                        y: point.total_value
                    })),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return `Value: ${formatCurrency(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        type: currentScale,
                        title: {
                            display: true,
                            text: 'Portfolio Value ($)'
                        },
                        ticks: {
                            callback: (value) => formatCurrency(value)
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to load equity curve:', error);
        const ctx = document.getElementById('equity-chart');
        if (ctx && equityChart) {
            equityChart.destroy();
            equityChart = null;
        }
    }
}

// Toggle between linear and logarithmic scale
function toggleScale() {
    currentScale = currentScale === 'linear' ? 'logarithmic' : 'linear';
    loadEquityCurve();
}

// Execute new trading decision
async function executeDecision() {
    const button = event.target;
    button.disabled = true;
    button.textContent = 'Executing...';

    try {
        const result = await api.executeDecision();
        showSuccess('Decision executed successfully!');
        // Reload dashboard after execution
        await loadDashboard();
    } catch (error) {
        showError(`Failed to execute decision: ${error.message}`);
    } finally {
        button.disabled = false;
        button.textContent = 'Execute New Decision';
    }
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
    // Refresh data every 30 seconds
    setInterval(loadDashboard, 30000);
});
