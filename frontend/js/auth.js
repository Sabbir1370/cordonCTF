// frontend/js/auth.js

/**
 * Register a new user.
 * @param {string} username
 * @param {string} password
 * @param {string} role - 'player' or 'admin'
 * @returns {Promise<object>} - e.g., { message: "Account created successfully" }
 */
async function registerUser(username, password, role = 'player') {
    return await api('POST', '/api/auth/register', { username, password, role });
}

/**
 * Login and store the JWT token + role in localStorage.
 * @param {string} username
 * @param {string} password
 * @returns {Promise<object>} - e.g., { access_token, token_type, role }
 */
async function loginUser(username, password) {
    const data = await api('POST', '/api/auth/login', { username, password });
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('role', data.role);
    localStorage.setItem('username', username);
    return data;
}

/**
 * Logout: clear stored token and user info.
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    // Redirect to login page (or homepage)
    window.location.href = 'login.html';
}

/**
 * Check if a user is logged in (token exists).
 * @returns {boolean}
 */
function isLoggedIn() {
    return !!localStorage.getItem('access_token');
}

/**
 * Get the current user's role from localStorage.
 * @returns {string|null}
 */
function getCurrentUserRole() {
    return localStorage.getItem('role');
}

/**
 * Redirect to login page if not authenticated.
 * Call this on pages that require login.
 */
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = 'login.html';
    }
}