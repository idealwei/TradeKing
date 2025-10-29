// API Configuration
const API_BASE_URL = window.location.origin + '/api';

// Chart.js default configuration
Chart.defaults.color = '#9ca3af';
Chart.defaults.borderColor = '#2d3748';
Chart.defaults.backgroundColor = '#3b82f6';

// Utility functions
const formatCurrency = (value) => {
    if (value === null || value === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
};

const formatNumber = (value, decimals = 2) => {
    if (value === null || value === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
};

const formatPercent = (value, decimals = 2) => {
    if (value === null || value === undefined) return '-';
    const formatted = formatNumber(value, decimals);
    return value >= 0 ? `+${formatted}%` : `${formatted}%`;
};

const formatTimestamp = (timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const getColorForValue = (value) => {
    if (value > 0) return '#10b981'; // green
    if (value < 0) return '#ef4444'; // red
    return '#9ca3af'; // gray
};

const showError = (message) => {
    console.error(message);
    alert(`Error: ${message}`);
};

const showSuccess = (message) => {
    console.log(message);
    // You can implement a toast notification here
};
