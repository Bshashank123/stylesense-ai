/* shared.js — Auth helpers and nav used across all pages */

const API = '';

function getToken() { return localStorage.getItem('token'); }
function getUser() { try { return JSON.parse(localStorage.getItem('user')); } catch { return null; } }

function requireAuth() {
  if (!getToken()) { window.location.href = '/'; return false; }
  return true;
}

function logout() {
  localStorage.clear();
  window.location.href = '/';
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  // Don't set Content-Type for FormData
  if (options.body instanceof FormData) delete headers['Content-Type'];

  const res = await fetch(`${API}${path}`, { ...options, headers });

  if (res.status === 401) { logout(); return null; }

  return res;
}

function buildNav(activePage) {
  const navItems = [
    { id: 'dashboard', icon: '🏠', label: 'Home', href: '/dashboard' },
    { id: 'wardrobe', icon: '👚', label: 'Wardrobe', href: '/wardrobe' },
    { id: 'generate', icon: '✨', label: 'Generate', href: '/generate' },
    { id: 'result', icon: '📸', label: 'History', href: '/result' },
  ];

  return `
    <nav class="sidebar">
      <div class="sidebar-logo">✦ StyleSense</div>
      <div class="nav-items">
        ${navItems.map(item => `
          <a href="${item.href}" class="nav-item ${activePage === item.id ? 'active' : ''}">
            <span class="nav-icon">${item.icon}</span>
            <span class="nav-label">${item.label}</span>
          </a>
        `).join('')}
      </div>
      <button class="logout-btn" onclick="logout()">← Sign Out</button>
    </nav>
  `;
}

const NAV_CSS = `
  .sidebar {
    width: 220px; min-width: 220px;
    background: rgba(255,255,255,0.03);
    border-right: 1px solid rgba(255,255,255,0.07);
    display: flex; flex-direction: column;
    padding: 28px 16px;
    height: 100vh; position: sticky; top: 0;
  }
  .sidebar-logo {
    font-size: 20px; font-weight: 900;
    background: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 32px; padding: 0 8px;
  }
  .nav-items { display: flex; flex-direction: column; gap: 4px; flex: 1; }
  .nav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 12px; border-radius: 10px;
    text-decoration: none; color: rgba(255,255,255,0.45);
    font-size: 14px; font-weight: 500;
    transition: all 0.15s;
  }
  .nav-item:hover { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.8); }
  .nav-item.active { background: rgba(124,58,237,0.2); color: #c4b5fd; }
  .nav-icon { font-size: 18px; }
  .logout-btn {
    background: none; border: 1px solid rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.3); padding: 10px 12px;
    border-radius: 10px; cursor: pointer; font-size: 13px;
    font-family: 'Inter', sans-serif; transition: all 0.15s; text-align: left;
  }
  .logout-btn:hover { color: rgba(255,255,255,0.6); border-color: rgba(255,255,255,0.15); }

  @media (max-width: 768px) {
    .sidebar { width: 100%; height: auto; flex-direction: row; align-items: center; padding: 12px 16px; position: fixed; bottom: 0; left: 0; border-right: none; border-top: 1px solid rgba(255,255,255,0.07); z-index: 100; }
    .sidebar-logo { display: none; }
    .nav-items { flex-direction: row; }
    .nav-label { display: none; }
    .logout-btn { padding: 8px; font-size: 12px; }
  }
`;
