// Decisions page logic

// Load decisions table
async function loadDecisions() {
    const modelFilter = document.getElementById('decision-model-filter')?.value || '';
    const limit = parseInt(document.getElementById('decision-limit')?.value || '50');

    try {
        const decisions = modelFilter
            ? await api.getDecisionsByFilter({ model_choice: modelFilter, limit })
            : await api.getLatestDecisions(limit);

        const table = document.getElementById('decisions-table');

        if (decisions.length === 0) {
            table.innerHTML = '<tr><td colspan="8" class="loading">No decisions found.</td></tr>';
            return;
        }

        table.innerHTML = decisions.map(decision => `
            <tr>
                <td><strong>#${decision.id}</strong></td>
                <td>${formatTimestamp(decision.timestamp)}</td>
                <td>
                    <span class="status-badge ${decision.model_choice === 'gpt5' ? 'status-success' : ''}">
                        ${decision.model_choice.toUpperCase()}
                    </span>
                </td>
                <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${decision.error_message ? `<span class="text-danger">Error</span>` : (decision.decision || 'N/A').substring(0, 100)}
                </td>
                <td>${decision.symbols ? decision.symbols.join(', ') : '-'}</td>
                <td>${formatNumber(decision.execution_time_ms || 0, 0)}</td>
                <td>
                    ${decision.error_message
                        ? '<span class="status-badge status-error">Failed</span>'
                        : '<span class="status-badge status-success">Success</span>'
                    }
                </td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="viewDecisionDetail(${decision.id})">
                        View
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load decisions:', error);
        document.getElementById('decisions-table').innerHTML =
            '<tr><td colspan="8" class="loading">Failed to load decisions.</td></tr>';
    }
}

// View decision detail
async function viewDecisionDetail(decisionId) {
    try {
        const decision = await api.getDecisionDetail(decisionId);

        const detailContainer = document.getElementById('decision-detail');
        detailContainer.innerHTML = `
            <div class="decision-detail">
                <div style="margin-bottom: 1.5rem;">
                    <h3>Decision #${decision.id}</h3>
                    <p style="color: #9ca3af;">
                        <strong>Model:</strong> ${decision.model_choice.toUpperCase()} |
                        <strong>Temperature:</strong> ${decision.temperature} |
                        <strong>Time:</strong> ${formatTimestamp(decision.timestamp)} |
                        <strong>Execution:</strong> ${formatNumber(decision.execution_time_ms || 0, 0)}ms
                    </p>
                </div>

                ${decision.symbols ? `
                <div style="margin-bottom: 1rem;">
                    <strong>Symbols Analyzed:</strong> ${decision.symbols.join(', ')}
                </div>
                ` : ''}

                ${decision.error_message ? `
                <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 0.5rem;">
                    <strong style="color: #ef4444;">Error:</strong>
                    <pre style="margin-top: 0.5rem; white-space: pre-wrap;">${decision.error_message}</pre>
                </div>
                ` : ''}

                <div style="margin-bottom: 1rem;">
                    <h4>Trading Decision:</h4>
                    <pre style="background: #0a0e1a; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; white-space: pre-wrap;">${decision.decision || 'No decision content'}</pre>
                </div>

                ${decision.prompt ? `
                <details style="margin-bottom: 1rem;">
                    <summary style="cursor: pointer; font-weight: 600; margin-bottom: 0.5rem;">View Full Prompt</summary>
                    <pre style="background: #0a0e1a; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; white-space: pre-wrap; font-size: 0.75rem;">${decision.prompt}</pre>
                </details>
                ` : ''}

                ${decision.account_data ? `
                <details style="margin-bottom: 1rem;">
                    <summary style="cursor: pointer; font-weight: 600; margin-bottom: 0.5rem;">Account Data</summary>
                    <pre style="background: #0a0e1a; padding: 1rem; border-radius: 0.5rem; overflow-x: auto;">${JSON.stringify(decision.account_data, null, 2)}</pre>
                </details>
                ` : ''}

                ${decision.positions_data ? `
                <details style="margin-bottom: 1rem;">
                    <summary style="cursor: pointer; font-weight: 600; margin-bottom: 0.5rem;">Positions Data</summary>
                    <pre style="background: #0a0e1a; padding: 1rem; border-radius: 0.5rem; overflow-x: auto;">${JSON.stringify(decision.positions_data, null, 2)}</pre>
                </details>
                ` : ''}

                ${decision.market_data ? `
                <details style="margin-bottom: 1rem;">
                    <summary style="cursor: pointer; font-weight: 600; margin-bottom: 0.5rem;">Market Data</summary>
                    <pre style="background: #0a0e1a; padding: 1rem; border-radius: 0.5rem; overflow-x: auto;">${JSON.stringify(decision.market_data, null, 2)}</pre>
                </details>
                ` : ''}

                ${decision.orders_data ? `
                <details style="margin-bottom: 1rem;">
                    <summary style="cursor: pointer; font-weight: 600; margin-bottom: 0.5rem;">Orders Data</summary>
                    <pre style="background: #0a0e1a; padding: 1rem; border-radius: 0.5rem; overflow-x: auto;">${JSON.stringify(decision.orders_data, null, 2)}</pre>
                </details>
                ` : ''}
            </div>
        `;

        document.getElementById('decision-modal').style.display = 'block';
    } catch (error) {
        console.error('Failed to load decision detail:', error);
        showError(`Failed to load decision detail: ${error.message}`);
    }
}

// Close modal
function closeModal() {
    document.getElementById('decision-modal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('decision-modal');
    if (event.target === modal) {
        closeModal();
    }
};

// Initialize decisions page
document.addEventListener('DOMContentLoaded', () => {
    loadDecisions();
    // Refresh every 30 seconds
    setInterval(loadDecisions, 30000);
});
