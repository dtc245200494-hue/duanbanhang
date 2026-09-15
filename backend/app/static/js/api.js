/**
 * API Client wrapper for Smart Retail Backend (10 Relational Tables).
 */

const API_BASE = '/api/v1';

export const API = {
  // Token helper
  getToken() {
    return localStorage.getItem('smart_retail_token') || '';
  },

  setToken(token) {
    if (token) localStorage.setItem('smart_retail_token', token);
    else localStorage.removeItem('smart_retail_token');
  },

  getAuthHeaders() {
    const token = this.getToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
  },

  // Auth & RBAC
  async login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Đăng nhập thất bại');
    const data = await res.json();
    this.setToken(data.access_token);
    return data;
  },

  async register(userData) {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Đăng ký thất bại');
    return res.json();
  },

  async getMyProfile() {
    const token = this.getToken();
    if (!token) return null;
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: this.getAuthHeaders(),
    });
    if (!res.ok) {
      this.setToken('');
      return null;
    }
    return res.json();
  },

  async getUsers() {
    const res = await fetch(`${API_BASE}/auth/users`, {
      headers: this.getAuthHeaders(),
    });
    return res.json();
  },

  async getRoles() {
    const res = await fetch(`${API_BASE}/auth/roles`);
    return res.json();
  },

  // Categories
  async getCategories() {
    const res = await fetch(`${API_BASE}/categories`);
    return res.json();
  },

  async createCategory(data) {
    const res = await fetch(`${API_BASE}/categories`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi thêm danh mục');
    return res.json();
  },

  // Stores
  async getStores() {
    const res = await fetch(`${API_BASE}/stores`);
    return res.json();
  },

  async createStore(data) {
    const res = await fetch(`${API_BASE}/stores`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Products
  async getProducts(storeId = null) {
    const url = storeId ? `${API_BASE}/products?store_id=${storeId}` : `${API_BASE}/products`;
    const res = await fetch(url);
    return res.json();
  },

  async createProduct(data) {
    const res = await fetch(`${API_BASE}/products`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi tạo sản phẩm');
    return res.json();
  },

  // Batches & FEFO
  async getBatches(productId = null) {
    const url = productId ? `${API_BASE}/batches?product_id=${productId}` : `${API_BASE}/batches`;
    const res = await fetch(url);
    return res.json();
  },

  async getExpiringBatches(days = 15) {
    const res = await fetch(`${API_BASE}/batches/expiring?days=${days}`);
    return res.json();
  },

  async createBatch(data) {
    const res = await fetch(`${API_BASE}/batches`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi thêm lô hàng');
    return res.json();
  },

  async updateBatchDiscount(batchId, discountRate) {
    const res = await fetch(`${API_BASE}/batches/${batchId}/discount`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ discount_rate: discountRate }),
    });
    return res.json();
  },

  // AI Dynamic Discount Engine
  async evaluateAIDiscount(payload) {
    const res = await fetch(`${API_BASE}/ai-discount/evaluate`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi đánh giá AI');
    return res.json();
  },

  async applyAIDiscount(batchId, promptVersion = 'v1') {
    const res = await fetch(`${API_BASE}/ai-discount/${batchId}/apply?prompt_version=${promptVersion}`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi áp dụng AI');
    return res.json();
  },

  // AI Recommendations Workflow
  async getAIRecommendations(status = null) {
    const url = status ? `${API_BASE}/ai-recommendations?status=${status}` : `${API_BASE}/ai-recommendations`;
    const res = await fetch(url);
    return res.json();
  },

  async approveRecommendation(recId) {
    const res = await fetch(`${API_BASE}/ai-recommendations/${recId}/approve`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi duyệt đề xuất');
    return res.json();
  },

  async rejectRecommendation(recId) {
    const res = await fetch(`${API_BASE}/ai-recommendations/${recId}/reject`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi từ chối đề xuất');
    return res.json();
  },

  // Orders
  async getOrders() {
    const res = await fetch(`${API_BASE}/orders`);
    return res.json();
  },

  async createOrder(data) {
    const res = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi tạo đơn hàng');
    return res.json();
  },

  async updateOrderStatus(orderId, status) {
    const res = await fetch(`${API_BASE}/orders/${orderId}/status`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ status }),
    });
    return res.json();
  },

  // Payments
  async getPayments(orderId = null) {
    const url = orderId ? `${API_BASE}/payments?order_id=${orderId}` : `${API_BASE}/payments`;
    const res = await fetch(url);
    return res.json();
  },

  async updatePaymentStatus(paymentId, status) {
    const res = await fetch(`${API_BASE}/payments/${paymentId}/status`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Lỗi cập nhật thanh toán');
    return res.json();
  },
};
