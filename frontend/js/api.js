// frontend/js/api.js

// Base URL for the backend API – auto-detected from the browser's current location.
// If you're testing on the laptop itself, use localhost. When users connect via hotspot,
// they'll use the laptop's IP. This makes it portable.
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`;

/**
 * Helper function to make API requests.
 * - Attaches JWT token if available.
 * - Automatically parses JSON.
 * - Throws an error with detail message for non-2xx responses.
 *
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {string} path - API endpoint path (e.g., '/api/auth/login')
 * @param {object|null} body - Request body (for POST/PUT). Will be JSON-stringified if not FormData.
 * @returns {Promise<any>} Parsed JSON response.
 */
async function api(method, path, body = null) {
    const headers = {};

    // If body is FormData (file uploads), let fetch set Content-Type automatically.
    if (!(body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    // Attach JWT token if present.
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers,
    };

    if (body) {
        options.body = body instanceof FormData ? body : JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${path}`, options);

    // Parse JSON – all our API responses are JSON.
    const data = await response.json();

    // If the request was not successful, throw an error with the detail message.
    if (!response.ok) {
        const error = new Error(data.detail || 'Request failed');
        error.status = response.status;
        throw error;
    }

    return data;
}