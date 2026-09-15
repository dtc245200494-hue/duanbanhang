import { API } from './api.js';

// Application State
const state = {
  currentTab: 'dashboard',
  currentUser: null,
  stores: [],
  categories: [],
  products: [],
  expiringBatches: [],
  orders: [],
  recommendations: [],
  payments: [],
  activeAIMyBatch: null,
};

// Utilities
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
};

const showToast = (message, type = 'success') => {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : '⚠'}</span>
    <div>${message}</div>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
};

// ==========================================
// AUTHENTICATION & ROLE-BASED ACCESS CONTROL
// ==========================================
window.initAuth = async function () {
  try {
    let user = await API.getMyProfile();
    if (!user) {
      // Default initial login as Store Manager for instant demo
      const loginRes = await API.login('manager@freshmart.vn', 'Admin@123');
      user = loginRes.user;
    }
    state.currentUser = user;
  } catch (err) {
    console.warn('Khởi tạo tài khoản:', err);
  } finally {
    window.renderUserBar();
    window.applyRolePermissions();
  }
};

window.openAuthModal = function (tab = 'login') {
  window.switchAuthTab(tab);
  document.getElementById('auth-modal').classList.add('open');
};

window.closeAuthModal = function () {
  document.getElementById('auth-modal').classList.remove('open');
};

window.switchAuthTab = function (tab) {
  const isLogin = tab === 'login';
  document.getElementById('auth-tab-login').classList.toggle('active', isLogin);
  document.getElementById('auth-tab-register').classList.toggle('active', !isLogin);
  document.getElementById('form-login-box').style.display = isLogin ? 'block' : 'none';
  document.getElementById('form-register-box').style.display = !isLogin ? 'block' : 'none';
};

window.handleLoginSubmit = async function (e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  try {
    const res = await API.login(email, password);
    state.currentUser = res.user;
    window.renderUserBar();
    window.applyRolePermissions();
    window.closeAuthModal();
    showToast(`Đăng nhập thành công! Xin chào ${res.user.full_name} (${res.user.role_name || res.user.role_code})`);
    window.switchTab('dashboard');
  } catch (err) {
    showToast('Đăng nhập thất bại: ' + err.message, 'danger');
  }
};

window.handleRegisterSubmit = async function (e) {
  e.preventDefault();
  const email = document.getElementById('reg-email').value;
  const fullName = document.getElementById('reg-fullname').value;
  const phone = document.getElementById('reg-phone').value;
  const password = document.getElementById('reg-password').value;
  const roleCode = document.getElementById('reg-role').value;

  try {
    await API.register({
      email,
      full_name: fullName,
      phone,
      password,
      role_code: roleCode,
    });
    showToast('Đăng ký thành công! Đang tự động đăng nhập...');
    // Auto login
    const res = await API.login(email, password);
    state.currentUser = res.user;
    window.renderUserBar();
    window.applyRolePermissions();
    window.closeAuthModal();
    window.switchTab('dashboard');
  } catch (err) {
    showToast('Đăng ký thất bại: ' + err.message, 'danger');
  }
};

window.quickLoginAs = async function (email) {
  try {
    const res = await API.login(email, 'Admin@123');
    state.currentUser = res.user;
    window.renderUserBar();
    window.applyRolePermissions();
    window.closeAuthModal();
    showToast(`Đã đăng nhập vai trò: ${res.user.role_name || res.user.role_code}`);
    window.switchTab(state.currentTab);
  } catch (err) {
    showToast('Lỗi đăng nhập nhanh: ' + err.message, 'danger');
  }
};

window.handleLogout = function () {
  API.setToken('');
  state.currentUser = null;
  window.renderUserBar();
  window.applyRolePermissions();
  showToast('Đã đăng xuất tài khoản.');
  window.openAuthModal('login');
};

window.renderUserBar = function () {
  const user = state.currentUser;
  const nameEl = document.getElementById('current-user-name');
  const roleEl = document.getElementById('current-user-role');
  const btnAuthEl = document.getElementById('btn-auth-action');

  if (user) {
    if (nameEl) nameEl.textContent = user.full_name;
    if (roleEl) {
      roleEl.textContent = user.role_name || user.role_code;
      roleEl.className = 'badge ' + (user.role_code === 'admin' ? 'badge-critical' : user.role_code === 'store_manager' ? 'badge-info' : 'badge-success');
    }
    if (btnAuthEl) {
      btnAuthEl.innerHTML = '🚪 Đăng Xuất';
      btnAuthEl.onclick = window.handleLogout;
      btnAuthEl.className = 'btn btn-secondary btn-sm';
    }
  } else {
    if (nameEl) nameEl.textContent = 'Khách Vãng Lai';
    if (roleEl) {
      roleEl.textContent = 'Chưa đăng nhập';
      roleEl.className = 'badge badge-warning';
    }
    if (btnAuthEl) {
      btnAuthEl.innerHTML = '🔑 Đăng Nhập';
      btnAuthEl.onclick = () => window.openAuthModal('login');
      btnAuthEl.className = 'btn btn-primary btn-sm';
    }
  }
};

/**
 * Enforce Role-Based Access Control on the frontend navigation.
 */
window.applyRolePermissions = function () {
  const role = state.currentUser ? state.currentUser.role_code : 'customer';

  // Define allowed tabs per role
  const permissions = {
    customer: ['dashboard', 'categories', 'pos', 'orders'],
    store_manager: ['dashboard', 'expiring', 'recommendations', 'categories', 'products', 'pos', 'orders', 'payments'],
    admin: ['dashboard', 'expiring', 'recommendations', 'categories', 'products', 'pos', 'orders', 'payments'],
  };

  const allowedTabs = permissions[role] || permissions['customer'];

  document.querySelectorAll('.nav-item').forEach((el) => {
    const tabName = el.dataset.tab;
    const isAllowed = allowedTabs.includes(tabName);
    el.classList.toggle('hidden-by-role', !isAllowed);
  });

  // If user is on an unauthorized tab, redirect to pos or dashboard
  if (!allowedTabs.includes(state.currentTab)) {
    window.switchTab(allowedTabs[0] || 'pos');
  }
};

// ==========================================
// TAB NAVIGATION & VIEW LOADERS
// ==========================================
window.switchTab = (tabId) => {
  const role = state.currentUser ? state.currentUser.role_code : 'customer';
  const permissions = {
    customer: ['dashboard', 'categories', 'pos', 'orders'],
    store_manager: ['dashboard', 'expiring', 'recommendations', 'categories', 'products', 'pos', 'orders', 'payments'],
    admin: ['dashboard', 'expiring', 'recommendations', 'categories', 'products', 'pos', 'orders', 'payments'],
  };
  const allowed = permissions[role] || permissions['customer'];
  if (!allowed.includes(tabId)) {
    showToast(`Vai trò "${state.currentUser ? state.currentUser.role_name : 'Khách'}" không có quyền truy cập tab này!`, 'danger');
    return;
  }

  state.currentTab = tabId;
  document.querySelectorAll('.nav-item').forEach((el) => {
    el.classList.toggle('active', el.dataset.tab === tabId);
  });
  document.querySelectorAll('.tab-view').forEach((el) => {
    el.style.display = el.id === `view-${tabId}` ? 'block' : 'none';
  });

  if (tabId === 'dashboard') loadDashboard();
  if (tabId === 'expiring') loadExpiringView();
  if (tabId === 'recommendations') loadRecommendationsView();
  if (tabId === 'categories') loadCategoriesView();
  if (tabId === 'products') loadProductsView();
  if (tabId === 'pos') loadPOSView();
  if (tabId === 'orders') loadOrdersView();
  if (tabId === 'payments') loadPaymentsView();
};

// 1. Dashboard View
async function loadDashboard() {
  try {
    const [stores, products, expiring, orders, recs, payments] = await Promise.all([
      API.getStores(),
      API.getProducts(),
      API.getExpiringBatches(15),
      API.getOrders(),
      API.getAIRecommendations('pending'),
      API.getPayments(),
    ]);

    state.stores = stores;
    state.products = products;
    state.expiringBatches = expiring;
    state.orders = orders;
    state.recommendations = recs;
    state.payments = payments;

    const criticalCount = expiring.filter((b) => b.days_until_expiry <= 3).length;
    const totalRevenue = orders.reduce((acc, o) => acc + parseFloat(o.total_amount || 0), 0);

    document.getElementById('kpi-products').textContent = products.length;
    document.getElementById('kpi-expiring').textContent = expiring.length;
    document.getElementById('kpi-critical').textContent = criticalCount;
    document.getElementById('kpi-revenue').textContent = formatCurrency(totalRevenue);

    // Badges
    const badgeExpiring = document.getElementById('badge-expiring-count');
    if (badgeExpiring) badgeExpiring.textContent = expiring.length;

    const badgeRecs = document.getElementById('badge-recs-count');
    if (badgeRecs) badgeRecs.textContent = recs.length;

    // Render Urgent Batches Table
    const tbody = document.getElementById('dashboard-urgent-tbody');
    if (!tbody) return;

    if (expiring.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding: 30px;">Không có lô hàng cận date trong 15 ngày tới.</td></tr>`;
      return;
    }

    const isManagerOrAdmin = state.currentUser && ['admin', 'store_manager'].includes(state.currentUser.role_code);

    tbody.innerHTML = expiring
      .slice(0, 5)
      .map((b) => {
        let urgencyBadge = '';
        if (b.days_until_expiry <= 3) {
          urgencyBadge = `<span class="badge badge-critical">Còn ${b.days_until_expiry} ngày (Khẩn cấp)</span>`;
        } else if (b.days_until_expiry <= 7) {
          urgencyBadge = `<span class="badge badge-warning">Còn ${b.days_until_expiry} ngày</span>`;
        } else {
          urgencyBadge = `<span class="badge badge-info">Còn ${b.days_until_expiry} ngày</span>`;
        }

        return `
        <tr>
          <td>
            <div class="product-cell">
              <div>
                <div class="product-name">${b.product_name}</div>
                <div class="product-sku">Lô: <strong>${b.batch_code || '#' + b.id}</strong></div>
              </div>
            </div>
          </td>
          <td><strong>${b.stock_quantity}</strong> hộp/gói</td>
          <td>${urgencyBadge}</td>
          <td>
            ${
              b.discount_rate > 0
                ? `<span class="price-strike">${formatCurrency(b.original_price)}</span>
                   <span class="price-discounted">${formatCurrency(b.effective_unit_price)}</span>
                   <span class="discount-pill">-${b.discount_rate}%</span>`
                : `<span>${formatCurrency(b.original_price)}</span>`
            }
          </td>
          <td>
            ${
              isManagerOrAdmin
                ? `<button class="btn btn-primary btn-sm" onclick="window.openAIModal(${b.id})">🤖 AI Gợi ý</button>`
                : `<button class="btn btn-success btn-sm" onclick="window.switchTab('pos')">🛒 Mua Ngay</button>`
            }
          </td>
        </tr>
      `;
      })
      .join('');
  } catch (err) {
    console.error('Lỗi khi tải Dashboard:', err);
    showToast('Lỗi khi tải dữ liệu tổng quan', 'danger');
  }
}

// 2. Expiring Batches View
window.loadExpiringView = async function () {
  try {
    const daysSelect = document.getElementById('filter-expiry-days');
    const days = daysSelect ? daysSelect.value : 15;
    const expiring = await API.getExpiringBatches(days);
    state.expiringBatches = expiring;

    const tbody = document.getElementById('expiring-batches-tbody');
    if (!tbody) return;

    if (expiring.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-muted); padding: 40px;">Không có lô hàng cận date nào theo bộ lọc.</td></tr>`;
      return;
    }

    tbody.innerHTML = expiring
      .map((b) => {
        let urgencyBadge = '';
        if (b.days_until_expiry <= 3) {
          urgencyBadge = `<span class="badge badge-critical">Còn ${b.days_until_expiry} ngày</span>`;
        } else if (b.days_until_expiry <= 7) {
          urgencyBadge = `<span class="badge badge-warning">Còn ${b.days_until_expiry} ngày</span>`;
        } else {
          urgencyBadge = `<span class="badge badge-info">Còn ${b.days_until_expiry} ngày</span>`;
        }

        return `
        <tr>
          <td><strong>${b.batch_code || '#' + b.id}</strong></td>
          <td>
            <div class="product-name">${b.product_name}</div>
            <div class="product-sku">SKU: ${b.product_sku || 'N/A'} • ${b.store_name || 'Kho chính'}</div>
          </td>
          <td><strong>${b.stock_quantity}</strong></td>
          <td>${b.expiry_date}</td>
          <td>${urgencyBadge}</td>
          <td>
            ${
              b.discount_rate > 0
                ? `<span class="price-strike">${formatCurrency(b.original_price)}</span><br>
                   <span class="price-discounted">${formatCurrency(b.effective_unit_price)}</span>
                   <span class="discount-pill">-${b.discount_rate}%</span>`
                : `<span>${formatCurrency(b.original_price)}</span>`
            }
          </td>
          <td>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-primary btn-sm" onclick="window.openAIModal(${b.id})">
                🤖 AI Phân tích
              </button>
              <button class="btn btn-secondary btn-sm" onclick="window.quickApplyAI(${b.id})">
                ⚡ Áp dụng nhanh
              </button>
            </div>
          </td>
        </tr>
      `;
      })
      .join('');
  } catch (err) {
    showToast('Lỗi khi tải danh sách lô cận date: ' + err.message, 'danger');
  }
};

// 3. AI Recommendations Workflow (Approval View)
window.loadRecommendationsView = async function () {
  try {
    const filterSelect = document.getElementById('filter-rec-status');
    const status = filterSelect ? filterSelect.value : null;
    const recs = await API.getAIRecommendations(status);
    state.recommendations = recs;

    const tbody = document.getElementById('recommendations-tbody');
    if (!tbody) return;

    if (recs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-muted); padding: 40px;">Không có đề xuất nào trong danh mục này.</td></tr>`;
      return;
    }

    tbody.innerHTML = recs
      .map((r) => {
        let statusBadge = '';
        if (r.status === 'approved') {
          statusBadge = `<span class="badge badge-success">✓ Đã duyệt (${r.approver_name || 'Quản lý'})</span>`;
        } else if (r.status === 'rejected') {
          statusBadge = `<span class="badge badge-critical">✕ Từ chối</span>`;
        } else {
          statusBadge = `<span class="badge badge-warning">⏳ Chờ duyệt</span>`;
        }

        return `
        <tr>
          <td><strong>#${r.id}</strong></td>
          <td>
            <div class="product-name">${r.product_name || 'Sản phẩm'}</div>
            <div class="product-sku">Lô: <strong>${r.batch_code || '#' + r.batch_id}</strong></div>
          </td>
          <td><strong style="color: #f87171; font-size: 1.1rem;">-${r.recommended_discount}%</strong></td>
          <td style="max-width: 320px; font-size: 0.85rem; color: var(--text-secondary);">${r.reason}</td>
          <td>${statusBadge}</td>
          <td style="font-size: 0.8rem; color: var(--text-muted);">${new Date(r.created_at).toLocaleString('vi-VN')}</td>
          <td>
            ${
              r.status === 'pending'
                ? `
              <div style="display: flex; gap: 8px;">
                <button class="btn btn-success btn-sm" onclick="window.handleApproveRec(${r.id})">✓ Duyệt</button>
                <button class="btn btn-danger btn-sm" onclick="window.handleRejectRec(${r.id})">✕ Bỏ</button>
              </div>
            `
                : '<span style="color: var(--text-muted); font-size: 0.8rem;">Đã xử lý</span>'
            }
          </td>
        </tr>
      `;
      })
      .join('');
  } catch (err) {
    showToast('Lỗi khi tải đề xuất AI: ' + err.message, 'danger');
  }
};

window.handleApproveRec = async function (recId) {
  try {
    await API.approveRecommendation(recId);
    showToast('Đã duyệt thành công! Tỷ lệ giảm giá đã được cập nhật cho lô hàng.');
    loadRecommendationsView();
  } catch (err) {
    showToast('Lỗi duyệt đề xuất: ' + err.message, 'danger');
  }
};

window.handleRejectRec = async function (recId) {
  try {
    await API.rejectRecommendation(recId);
    showToast('Đã từ chối đề xuất giảm giá.');
    loadRecommendationsView();
  } catch (err) {
    showToast('Lỗi từ chối đề xuất: ' + err.message, 'danger');
  }
};

// 4. Categories View
window.loadCategoriesView = async function () {
  try {
    const categories = await API.getCategories();
    state.categories = categories;

    const tbody = document.getElementById('categories-tbody');
    if (!tbody) return;

    tbody.innerHTML = categories
      .map(
        (c) => `
      <tr>
        <td>#${c.id}</td>
        <td><strong>${c.name}</strong></td>
        <td>${c.description || '-'}</td>
        <td><span class="badge badge-info">${c.product_count} sản phẩm</span></td>
      </tr>
    `
      )
      .join('');
  } catch (err) {
    showToast('Lỗi tải danh mục: ' + err.message, 'danger');
  }
};

window.handleCreateCategory = async function (e) {
  e.preventDefault();
  const name = document.getElementById('cat-name').value;
  const description = document.getElementById('cat-desc').value;

  try {
    await API.createCategory({ name, description });
    showToast('Đã thêm danh mục mới thành công!');
    document.getElementById('cat-form').reset();
    loadCategoriesView();
  } catch (err) {
    showToast('Lỗi thêm danh mục: ' + err.message, 'danger');
  }
};

// 5. Products & Stock View
window.loadProductsView = async function () {
  try {
    const [products, categories] = await Promise.all([API.getProducts(), API.getCategories()]);
    state.products = products;
    state.categories = categories;

    const tbody = document.getElementById('products-tbody');
    if (!tbody) return;

    tbody.innerHTML = products
      .map(
        (p) => `
      <tr>
        <td>#${p.id}</td>
        <td>
          <div class="product-cell">
            <img src="${p.image_url || 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=100'}" class="product-img" alt="${p.name}">
            <div>
              <div class="product-name">${p.name}</div>
              <div class="product-sku">SKU: ${p.sku || 'N/A'} • Danh mục: <strong>${p.category_name || 'Khác'}</strong></div>
            </div>
          </div>
        </td>
        <td>${formatCurrency(p.original_price)}</td>
        <td><strong>${p.total_stock}</strong> sp</td>
        <td>${new Date(p.created_at).toLocaleDateString('vi-VN')}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="window.openAddBatchModal(${p.id}, '${p.name}')">
            + Nhập Lô Mới
          </button>
        </td>
      </tr>
    `
      )
      .join('');
  } catch (err) {
    showToast('Lỗi khi tải danh sách sản phẩm', 'danger');
  }
};

// 6. POS / Checkout View
window.loadPOSView = async function () {
  try {
    const [stores, products, categories] = await Promise.all([
      API.getStores(),
      API.getProducts(),
      API.getCategories(),
    ]);
    state.stores = stores;
    state.products = products;
    state.categories = categories;

    // Fill Store select
    const storeSelect = document.getElementById('pos-store');
    if (storeSelect) {
      storeSelect.innerHTML = stores.map((s) => `<option value="${s.id}">${s.name}</option>`).join('');
    }

    // Fill Product select
    const prodSelect = document.getElementById('pos-product');
    if (prodSelect) {
      prodSelect.innerHTML = products
        .map(
          (p) =>
            `<option value="${p.id}">${p.name} [${p.category_name || 'Hàng tươi'}] (Tồn: ${p.total_stock} - ${formatCurrency(p.original_price)})</option>`
        )
        .join('');
    }

    // Fill customer defaults if user is logged in
    if (state.currentUser) {
      const nameInput = document.getElementById('pos-name');
      const phoneInput = document.getElementById('pos-phone');
      if (nameInput && !nameInput.value) nameInput.value = state.currentUser.full_name;
      if (phoneInput && !phoneInput.value) phoneInput.value = state.currentUser.phone || '';
    }
  } catch (err) {
    showToast('Lỗi nạp thông tin POS', 'danger');
  }
};

window.handleCreateOrder = async function (e) {
  e.preventDefault();
  const storeId = document.getElementById('pos-store').value;
  const customerName = document.getElementById('pos-name').value;
  const customerPhone = document.getElementById('pos-phone').value;
  const shippingAddress = document.getElementById('pos-address').value;
  const note = document.getElementById('pos-note').value;
  const paymentMethod = document.getElementById('pos-payment-method').value;
  const productId = parseInt(document.getElementById('pos-product').value, 10);
  const quantity = parseInt(document.getElementById('pos-quantity').value, 10);

  try {
    const orderData = {
      store_id: storeId ? parseInt(storeId, 10) : null,
      user_id: state.currentUser ? state.currentUser.id : null,
      customer_name: customerName,
      customer_phone: customerPhone,
      shipping_address: shippingAddress,
      note: note,
      payment_method: paymentMethod,
      items: [{ product_id: productId, quantity: quantity }],
    };

    const res = await API.createOrder(orderData);
    showToast(`Tạo đơn #${res.id} thành công! Phương thức: ${paymentMethod.toUpperCase()}`);
    document.getElementById('pos-form').reset();
    window.switchTab('orders');
  } catch (err) {
    showToast('Lỗi tạo đơn: ' + err.message, 'danger');
  }
};

// 7. Orders View
window.loadOrdersView = async function () {
  try {
    const orders = await API.getOrders();
    state.orders = orders;
    const tbody = document.getElementById('orders-tbody');
    if (!tbody) return;

    if (orders.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color: var(--text-muted); padding: 40px;">Chưa có đơn hàng nào.</td></tr>`;
      return;
    }

    const isManagerOrAdmin = state.currentUser && ['admin', 'store_manager'].includes(state.currentUser.role_code);

    tbody.innerHTML = orders
      .map((o) => {
        let statusBadge = '';
        if (o.status === 'completed') statusBadge = '<span class="badge badge-success">Hoàn thành</span>';
        else if (o.status === 'shipping') statusBadge = '<span class="badge badge-info">Đang giao</span>';
        else if (o.status === 'confirmed') statusBadge = '<span class="badge badge-warning">Đã xác nhận</span>';
        else if (o.status === 'cancelled') statusBadge = '<span class="badge badge-critical">Đã hủy</span>';
        else statusBadge = '<span class="badge badge-warning">Chờ xử lý</span>';

        const payment = o.payments && o.payments.length > 0 ? o.payments[0] : null;
        let payBadge = '<span class="badge badge-warning">Chờ thanh toán</span>';
        if (payment && payment.status === 'paid') {
          payBadge = `<span class="badge badge-success">✓ Đã TT (${payment.payment_method.toUpperCase()})</span>`;
        }

        const itemsSummary = o.items
          .map(
            (i) =>
              `<div>• <strong>${i.product_name || 'SP'}</strong> (Lô: ${i.batch_code || 'FEFO'}): ${i.quantity} x ${formatCurrency(i.unit_price)}</div>`
          )
          .join('');

        return `
        <tr>
          <td><strong>#${o.id}</strong></td>
          <td>
            <div style="font-weight: 600;">${o.customer_name}</div>
            <div style="font-size: 0.8rem; color: var(--text-muted);">${o.customer_phone}</div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">${o.shipping_address}</div>
          </td>
          <td>${itemsSummary}</td>
          <td><strong>${formatCurrency(o.total_amount)}</strong></td>
          <td>${payBadge}</td>
          <td>${statusBadge}</td>
          <td>${new Date(o.created_at).toLocaleString('vi-VN')}</td>
          <td>
            ${
              isManagerOrAdmin
                ? `
              <select class="form-select" style="padding: 4px 8px; font-size: 0.8rem;" onchange="window.changeOrderStatus(${o.id}, this.value)">
                <option value="pending" ${o.status === 'pending' ? 'selected' : ''}>Chờ duyệt</option>
                <option value="confirmed" ${o.status === 'confirmed' ? 'selected' : ''}>Xác nhận</option>
                <option value="shipping" ${o.status === 'shipping' ? 'selected' : ''}>Đang giao</option>
                <option value="completed" ${o.status === 'completed' ? 'selected' : ''}>Hoàn thành</option>
                <option value="cancelled" ${o.status === 'cancelled' ? 'selected' : ''}>Hủy (Hoàn kho)</option>
              </select>
            `
                : `<span style="font-size: 0.8rem; color: var(--text-muted);">${o.status.toUpperCase()}</span>`
            }
          </td>
        </tr>
      `;
      })
      .join('');
  } catch (err) {
    showToast('Lỗi khi tải đơn hàng', 'danger');
  }
};

window.changeOrderStatus = async function (orderId, newStatus) {
  try {
    await API.updateOrderStatus(orderId, newStatus);
    showToast(`Đã cập nhật trạng thái đơn #${orderId}`);
    loadOrdersView();
  } catch (err) {
    showToast('Lỗi cập nhật: ' + err.message, 'danger');
  }
};

// 8. Payments View
window.loadPaymentsView = async function () {
  try {
    const payments = await API.getPayments();
    state.payments = payments;
    const tbody = document.getElementById('payments-tbody');
    if (!tbody) return;

    if (payments.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-muted); padding: 40px;">Chưa có giao dịch thanh toán nào.</td></tr>`;
      return;
    }

    tbody.innerHTML = payments
      .map((p) => {
        let statusBadge = '';
        if (p.status === 'paid') statusBadge = '<span class="badge badge-success">✓ Đã thanh toán</span>';
        else if (p.status === 'failed') statusBadge = '<span class="badge badge-critical">✕ Thất bại</span>';
        else statusBadge = '<span class="badge badge-warning">⏳ Chờ thu tiền</span>';

        return `
        <tr>
          <td><strong>#PAY-${p.id}</strong></td>
          <td>Đơn hàng <strong>#${p.order_id}</strong></td>
          <td><span class="badge badge-info">${p.payment_method.toUpperCase()}</span></td>
          <td><strong>${formatCurrency(p.amount)}</strong></td>
          <td>${statusBadge}</td>
          <td>${p.paid_at ? new Date(p.paid_at).toLocaleString('vi-VN') : '-'}</td>
          <td>
            ${
              p.status !== 'paid'
                ? `<button class="btn btn-success btn-sm" onclick="window.markPaymentPaid(${p.id})">✓ Xác Nhận Đã Thu</button>`
                : '<span style="color: var(--text-muted); font-size: 0.8rem;">Đã quyết toán</span>'
            }
          </td>
        </tr>
      `;
      })
      .join('');
  } catch (err) {
    showToast('Lỗi khi tải giao dịch thanh toán', 'danger');
  }
};

window.markPaymentPaid = async function (paymentId) {
  try {
    await API.updatePaymentStatus(paymentId, 'paid');
    showToast('Đã xác nhận thanh toán thành công!');
    loadPaymentsView();
  } catch (err) {
    showToast('Lỗi cập nhật thanh toán: ' + err.message, 'danger');
  }
};

// AI Discount Modal Logic
window.openAIModal = async function (batchId) {
  try {
    const batches = await API.getBatches();
    const batch = batches.find((b) => b.id === batchId);
    if (!batch) return;

    state.activeAIMyBatch = batch;
    document.getElementById('ai-modal-batch-code').textContent = batch.batch_code || '#' + batch.id;
    document.getElementById('ai-modal-expiry').textContent = `${batch.expiry_date} (còn ${batch.days_until_expiry} ngày)`;
    document.getElementById('ai-modal-stock').textContent = `${batch.stock_quantity} sản phẩm`;
    document.getElementById('ai-modal-current-price').textContent = `${formatCurrency(batch.effective_unit_price)} (Giảm ${batch.discount_rate}%)`;

    document.getElementById('ai-rec-result').style.display = 'none';
    document.getElementById('ai-modal').classList.add('open');
  } catch (err) {
    showToast('Không thể mở modal AI: ' + err.message, 'danger');
  }
};

window.closeAIModal = function () {
  document.getElementById('ai-modal').classList.remove('open');
};

window.runAIEvaluation = async function () {
  if (!state.activeAIMyBatch) return;

  const runBtn = document.getElementById('btn-run-ai');
  runBtn.disabled = true;
  runBtn.textContent = '⏳ Đang phân tích...';

  try {
    const dailySales = parseFloat(document.getElementById('ai-input-sales').value) || 2.5;
    const competitorPrice = parseFloat(document.getElementById('ai-input-comp-price').value) || null;
    const customInst = document.getElementById('ai-input-custom').value;
    const promptVersion = document.getElementById('ai-select-prompt').value;

    const res = await API.evaluateAIDiscount({
      batch_id: state.activeAIMyBatch.id,
      average_daily_sales: dailySales,
      competitor_price: competitorPrice,
      custom_instruction: customInst,
    });

    state.latestAIRecommendation = res;

    const resultBox = document.getElementById('ai-rec-result');
    resultBox.style.display = 'block';

    document.getElementById('ai-res-rate').textContent = `-${res.suggested_discount_rate}%`;
    document.getElementById('ai-res-price').textContent = formatCurrency(res.suggested_price);
    document.getElementById('ai-res-engine').textContent = res.engine_used === 'openai_gpt' ? 'OpenAI GPT-4' : 'Rule-Based Fallback Engine';
    document.getElementById('ai-res-urgency').textContent = res.urgency_level.toUpperCase();
    document.getElementById('ai-res-reason').textContent = res.reasoning;
    document.getElementById('ai-res-confidence').textContent = `${Math.round(res.confidence_score * 100)}%`;

    showToast('AI đã hoàn tất đề xuất và ghi nhận vào danh sách Chờ duyệt!');
  } catch (err) {
    showToast('Lỗi chạy AI: ' + err.message, 'danger');
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = '🤖 Chạy Phân Tích AI';
  }
};

window.applyLatestAIDiscount = async function () {
  if (!state.latestAIRecommendation || !state.activeAIMyBatch) return;
  try {
    await API.updateBatchDiscount(
      state.activeAIMyBatch.id,
      state.latestAIRecommendation.suggested_discount_rate
    );
    showToast(`Đã áp dụng chiết khấu ${state.latestAIRecommendation.suggested_discount_rate}% cho lô ${state.activeAIMyBatch.batch_code}!`);
    window.closeAIModal();
    if (state.currentTab === 'dashboard') loadDashboard();
    if (state.currentTab === 'expiring') loadExpiringView();
  } catch (err) {
    showToast('Lỗi khi áp dụng giá: ' + err.message, 'danger');
  }
};

window.quickApplyAI = async function (batchId) {
  try {
    const res = await API.applyAIDiscount(batchId, 'v1');
    showToast(`⚡ Đã tự động áp dụng giảm giá -${res.suggested_discount_rate}% cho lô hàng!`);
    loadExpiringView();
  } catch (err) {
    showToast('Lỗi áp dụng AI nhanh: ' + err.message, 'danger');
  }
};

// Modal for adding new batch
window.openAddBatchModal = function (productId, productName) {
  document.getElementById('batch-product-id').value = productId;
  document.getElementById('batch-product-name').textContent = productName;
  document.getElementById('add-batch-modal').classList.add('open');
};

window.closeAddBatchModal = function () {
  document.getElementById('add-batch-modal').classList.remove('open');
};

window.handleAddBatch = async function (e) {
  e.preventDefault();
  const productId = parseInt(document.getElementById('batch-product-id').value, 10);
  const batchCode = document.getElementById('batch-code').value;
  const stockQuantity = parseInt(document.getElementById('batch-quantity').value, 10);
  const expiryDate = document.getElementById('batch-expiry-date').value;
  const discountRate = parseInt(document.getElementById('batch-discount').value || 0, 10);

  try {
    await API.createBatch({
      product_id: productId,
      batch_code: batchCode,
      stock_quantity: stockQuantity,
      expiry_date: expiryDate,
      discount_rate: discountRate,
    });
    showToast('Đã thêm lô hàng mới thành công!');
    window.closeAddBatchModal();
    document.getElementById('add-batch-form').reset();
    loadProductsView();
  } catch (err) {
    showToast('Lỗi thêm lô hàng: ' + err.message, 'danger');
  }
};

// Modal for adding product
window.openAddProductModal = async function () {
  const [stores, categories] = await Promise.all([API.getStores(), API.getCategories()]);
  const storeSelect = document.getElementById('new-prod-store');
  const catSelect = document.getElementById('new-prod-cat');
  storeSelect.innerHTML = stores.map((s) => `<option value="${s.id}">${s.name}</option>`).join('');
  catSelect.innerHTML = categories.map((c) => `<option value="${c.id}">${c.name}</option>`).join('');
  document.getElementById('add-product-modal').classList.add('open');
};

window.closeAddProductModal = function () {
  document.getElementById('add-product-modal').classList.remove('open');
};

window.handleAddProduct = async function (e) {
  e.preventDefault();
  const storeId = parseInt(document.getElementById('new-prod-store').value, 10);
  const catId = parseInt(document.getElementById('new-prod-cat').value, 10);
  const name = document.getElementById('new-prod-name').value;
  const sku = document.getElementById('new-prod-sku').value;
  const originalPrice = parseFloat(document.getElementById('new-prod-price').value);
  const imageUrl = document.getElementById('new-prod-img').value;

  try {
    await API.createProduct({
      store_id: storeId,
      category_id: catId,
      name,
      sku,
      original_price: originalPrice,
      image_url: imageUrl,
    });
    showToast('Đã tạo sản phẩm mới thành công!');
    window.closeAddProductModal();
    document.getElementById('add-product-form').reset();
    loadProductsView();
  } catch (err) {
    showToast('Lỗi thêm sản phẩm: ' + err.message, 'danger');
  }
};

// Initial setup
document.addEventListener('DOMContentLoaded', async () => {
  await window.initAuth();

  const posForm = document.getElementById('pos-form');
  if (posForm) posForm.addEventListener('submit', window.handleCreateOrder);

  const addBatchForm = document.getElementById('add-batch-form');
  if (addBatchForm) addBatchForm.addEventListener('submit', window.handleAddBatch);

  const addProdForm = document.getElementById('add-product-form');
  if (addProdForm) addProdForm.addEventListener('submit', window.handleAddProduct);

  const catForm = document.getElementById('cat-form');
  if (catForm) catForm.addEventListener('submit', window.handleCreateCategory);

  const loginForm = document.getElementById('form-login');
  if (loginForm) loginForm.addEventListener('submit', window.handleLoginSubmit);

  const regForm = document.getElementById('form-register');
  if (regForm) regForm.addEventListener('submit', window.handleRegisterSubmit);
});
