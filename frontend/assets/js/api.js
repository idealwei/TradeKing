// API Client for TradeKing Backend

class TradeKingAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Health Check
    async getHealth() {
        return this.request('/health');
    }

    // Trading Decisions
    async executeDecision(data = {}) {
        return this.request('/decisions/execute', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async getLatestDecisions(limit = 10) {
        return this.request(`/decisions/latest?limit=${limit}`);
    }

    async getDecisionDetail(decisionId) {
        return this.request(`/decisions/${decisionId}`);
    }

    async getDecisionsByFilter(filters = {}) {
        const params = new URLSearchParams();
        if (filters.model_choice) params.append('model_choice', filters.model_choice);
        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        if (filters.limit) params.append('limit', filters.limit);

        const query = params.toString();
        return this.request(`/decisions${query ? '?' + query : ''}`);
    }

    // Model Performance
    async getModelPerformance() {
        return this.request('/models/performance');
    }

    async getModelPerformanceByChoice(modelChoice) {
        return this.request(`/models/performance/${modelChoice}`);
    }

    // Portfolio
    async getLatestSnapshot(modelChoice = null) {
        const query = modelChoice ? `?model_choice=${modelChoice}` : '';
        return this.request(`/portfolio/latest${query}`);
    }

    async getEquityCurve(modelChoice, limit = 1000) {
        return this.request(`/portfolio/equity-curve?model_choice=${modelChoice}&limit=${limit}`);
    }
}

// Create global API instance
const api = new TradeKingAPI(API_BASE_URL);
