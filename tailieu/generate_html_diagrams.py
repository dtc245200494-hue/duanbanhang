import os
import html

TARGET_DIRS = [
    "d:/duanbanhang/tailieu/images",
    "d:/duanbanhang/docs/images"
]

for d in TARGET_DIRS:
    os.makedirs(d, exist_ok=True)

def wrap_viewer(title, svg_content):
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} - Interactive Viewer</title>
<style>
:root {{ color-scheme: light dark; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font: 14px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  background: #f8fafc;
  color: #0f172a;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}
@media (prefers-color-scheme: dark) {{
  body {{ background: #0f172a; color: #f1f5f9; }}
}}
header {{
  padding: 10px 18px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  z-index: 10;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
@media (prefers-color-scheme: dark) {{
  header {{ background: #1e293b; border-color: #334155; }}
}}
h1 {{
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #1e3a8a;
  display: flex;
  align-items: center;
  gap: 8px;
}}
@media (prefers-color-scheme: dark) {{
  h1 {{ color: #60a5fa; }}
}}
.ctl {{
  display: flex;
  gap: 8px;
  align-items: center;
  margin-left: auto;
}}
button, input {{
  font: inherit;
  color: inherit;
}}
.ctl button {{
  padding: 6px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.15s;
}}
.ctl button:hover {{
  background: #f1f5f9;
  border-color: #94a3b8;
}}
@media (prefers-color-scheme: dark) {{
  .ctl button {{ background: #334155; border-color: #475569; }}
  .ctl button:hover {{ background: #475569; }}
}}
.ctl input {{
  padding: 6px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
  width: 220px;
}}
@media (prefers-color-scheme: dark) {{
  .ctl input {{ background: #334155; border-color: #475569; }}
}}
#hits {{
  font-size: 12px;
  color: #64748b;
  min-width: 60px;
}}
#stage {{
  flex: 1;
  overflow: hidden;
  position: relative;
  background: #ffffff;
  cursor: grab;
  touch-action: none;
}}
@media (prefers-color-scheme: dark) {{
  #stage {{ background: #0b0f19; }}
}}
#stage.drag {{
  cursor: grabbing;
}}
.page {{
  position: absolute;
  transform-origin: 0 0;
  display: block;
}}
.page svg {{
  display: block;
}}
.hit {{
  filter: drop-shadow(0 0 4px #f59e0b) drop-shadow(0 0 8px #f59e0baa);
}}
.hit.cursel {{
  filter: drop-shadow(0 0 5px #ef4444) drop-shadow(0 0 12px #ef4444cc);
}}
</style>
</head>
<body>
<header>
  <h1>📐 {html.escape(title)}</h1>
  <div class="ctl">
    <input id="q" type="search" placeholder="🔍 Tìm kiếm thành phần…">
    <span id="hits"></span>
    <button id="zout" title="Thu nhỏ">−</button>
    <button id="zin" title="Phóng to">+</button>
    <button id="fit" title="Vừa màn hình">Vừa khung</button>
  </div>
</header>
<main id="stage">
  <div class="page" id="diagram-container">
    {svg_content}
  </div>
</main>
<script>
const stage = document.getElementById('stage');
const page = document.getElementById('diagram-container');
const svg = page.querySelector('svg');
let view = {{ x: 0, y: 0, s: 1 }};

function apply() {{
  page.style.transform = `translate(${{view.x}}px,${{view.y}}px) scale(${{view.s}})`;
}}

function svgSize() {{
  return [
    parseFloat(svg.getAttribute('width')) || 1200,
    parseFloat(svg.getAttribute('height')) || 800
  ];
}}

function fit() {{
  const [w, h] = svgSize();
  const r = stage.getBoundingClientRect();
  const s = Math.min((r.width - 40) / w, (r.height - 40) / h, 2.5);
  view = {{ s, x: (r.width - w * s) / 2, y: (r.height - h * s) / 2 }};
  apply();
}}

stage.addEventListener('wheel', e => {{
  e.preventDefault();
  const r = stage.getBoundingClientRect();
  const mx = e.clientX - r.left;
  const my = e.clientY - r.top;
  const k = Math.exp(-e.deltaY * 0.0015);
  const s = Math.min(Math.max(view.s * k, 0.1), 10);
  view.x = mx - (mx - view.x) * s / view.s;
  view.y = my - (my - view.y) * s / view.s;
  view.s = s;
  apply();
}}, {{ passive: false }});

let drag = null;
stage.addEventListener('pointerdown', e => {{
  if (e.target.closest('a')) return;
  drag = {{ x: e.clientX, y: e.clientY }};
  stage.classList.add('drag');
  stage.setPointerCapture(e.pointerId);
}});

stage.addEventListener('pointermove', e => {{
  if (!drag) return;
  view.x += e.clientX - drag.x;
  view.y += e.clientY - drag.y;
  drag = {{ x: e.clientX, y: e.clientY }};
  apply();
}});

stage.addEventListener('pointerup', () => {{
  drag = null;
  stage.classList.remove('drag');
}});

function zoom(k) {{
  const r = stage.getBoundingClientRect();
  const mx = r.width / 2;
  const my = r.height / 2;
  const s = Math.min(Math.max(view.s * k, 0.1), 10);
  view.x = mx - (mx - view.x) * s / view.s;
  view.y = my - (my - view.y) * s / view.s;
  view.s = s;
  apply();
}}

document.getElementById('zin').onclick = () => zoom(1.25);
document.getElementById('zout').onclick = () => zoom(0.8);
document.getElementById('fit').onclick = fit;

const q = document.getElementById('q');
const hitEl = document.getElementById('hits');
let hits = [], hi = -1;

function search() {{
  hits.forEach(el => el.classList.remove('hit', 'cursel'));
  hits = [];
  hi = -1;
  const t = q.value.trim().toLowerCase();
  if (t) {{
    const all = [...svg.querySelectorAll('text')];
    hits = all.filter(el => el.textContent.toLowerCase().includes(t));
    hits.forEach(el => el.classList.add('hit'));
  }}
  hitEl.textContent = t ? hits.length + ' kết quả' : '';
}}

function centre(el) {{
  const r = stage.getBoundingClientRect();
  const b = el.getBoundingClientRect();
  view.x += r.left + r.width / 2 - (b.left + b.width / 2);
  view.y += r.top + r.height / 2 - (b.top + b.height / 2);
  apply();
}}

q.addEventListener('input', search);
q.addEventListener('keydown', e => {{
  if (e.key === 'Escape') {{ q.value = ''; search(); q.blur(); }}
  if (e.key !== 'Enter' || !hits.length) return;
  if (hi >= 0) hits[hi].classList.remove('cursel');
  hi = (hi + 1) % hits.length;
  hits[hi].classList.add('cursel');
  centre(hits[hi]);
}});

window.addEventListener('resize', fit);
setTimeout(fit, 50);
</script>
</body>
</html>
"""

# ================= 1. SVG: USE CASE =================
def svg_usecase():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="780" viewBox="0 0 1200 780">
  <defs>
    <style>
      .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }
      .header { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: bold; fill: #0F172A; text-anchor: middle; }
      .actor-name { font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #0F172A; text-anchor: middle; }
      .actor-role { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-style: italic; fill: #64748B; text-anchor: middle; }
      .uc-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #0F172A; text-anchor: middle; dominant-baseline: middle; }
      .uc-ai { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #065F46; text-anchor: middle; dominant-baseline: middle; }
      .uc-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #334155; text-anchor: middle; dominant-baseline: middle; }
      .leg-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #0F172A; }
      .leg-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #334155; dominant-baseline: middle; }
    </style>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569" />
    </marker>
  </defs>

  <text x="600" y="35" class="title">SƠ ĐỒ USE CASE TỔNG QUÁT HỆ THỐNG QUẢN LÝ BÁN HÀNG TÍCH HỢP AI</text>

  <!-- Boundary -->
  <rect x="240" y="55" width="720" height="700" rx="16" fill="#F8FAFC" stroke="#1E3A8A" stroke-width="2.5" />
  <text x="600" y="85" class="header">«system» HỆ THỐNG QUẢN LÝ BÁN HÀNG TÍCH HỢP AI (AI POS)</text>

  <!-- Admin Actor -->
  <g transform="translate(100, 360)">
    <circle cx="0" cy="-35" r="16" fill="#FEF3C7" stroke="#B45309" stroke-width="2.5" />
    <line x1="0" y1="-19" x2="0" y2="25" stroke="#B45309" stroke-width="2.5" stroke-linecap="round" />
    <line x1="-28" y1="-5" x2="28" y2="-5" stroke="#B45309" stroke-width="2.5" stroke-linecap="round" />
    <line x1="0" y1="25" x2="-22" y2="65" stroke="#B45309" stroke-width="2.5" stroke-linecap="round" />
    <line x1="0" y1="25" x2="22" y2="65" stroke="#B45309" stroke-width="2.5" stroke-linecap="round" />
    <text x="0" y="88" class="actor-name">Quản trị viên</text>
    <text x="0" y="106" class="actor-role">(Admin)</text>
  </g>

  <!-- Owner Actor -->
  <g transform="translate(1100, 360)">
    <circle cx="0" cy="-35" r="16" fill="#DBEAFE" stroke="#1E3A8A" stroke-width="2.5" />
    <line x1="0" y1="-19" x2="0" y2="25" stroke="#1E3A8A" stroke-width="2.5" stroke-linecap="round" />
    <line x1="-28" y1="-5" x2="28" y2="-5" stroke="#1E3A8A" stroke-width="2.5" stroke-linecap="round" />
    <line x1="0" y1="25" x2="-22" y2="65" stroke="#1E3A8A" stroke-width="2.5" stroke-linecap="round" />
    <line x1="0" y1="25" x2="22" y2="65" stroke="#1E3A8A" stroke-width="2.5" stroke-linecap="round" />
    <text x="0" y="88" class="actor-name">Chủ cửa hàng</text>
    <text x="0" y="106" class="actor-role">(Owner)</text>
  </g>

  <!-- Top Center UC -->
  <ellipse cx="600" cy="130" rx="120" ry="28" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
  <text x="600" y="130" class="uc-text">Đăng nhập &amp; Xác thực JWT</text>

  <!-- Left Column UCs -->
  <ellipse cx="430" cy="220" rx="120" ry="28" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
  <text x="430" y="220" class="uc-text">Quản lý Tài khoản (Admin)</text>

  <ellipse cx="430" cy="310" rx="120" ry="28" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
  <text x="430" y="310" class="uc-text">Quản lý Danh mục &amp; SP</text>

  <ellipse cx="430" cy="400" rx="120" ry="28" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
  <text x="430" y="400" class="uc-text">Nhập hàng &amp; Quản lý Kho</text>

  <ellipse cx="430" cy="490" rx="120" ry="28" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
  <text x="430" y="490" class="uc-text">Xem Dashboard Doanh thu</text>

  <ellipse cx="430" cy="580" rx="120" ry="28" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
  <text x="430" y="580" class="uc-text">Xuất báo cáo Excel / PDF</text>

  <!-- Right Column UCs -->
  <ellipse cx="770" cy="220" rx="120" ry="28" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
  <text x="770" y="220" class="uc-text">Bán hàng tại quầy (POS)</text>

  <ellipse cx="770" cy="310" rx="120" ry="28" fill="#FFFFFF" stroke="#2563EB" stroke-width="2" />
  <text x="770" y="310" class="uc-text">Hủy đơn hàng &amp; Hoàn kho</text>

  <ellipse cx="770" cy="400" rx="120" ry="28" fill="#F0FDF4" stroke="#10B981" stroke-width="2" />
  <text x="770" y="400" class="uc-ai">Trợ lý AI: Tư vấn Sản phẩm</text>

  <ellipse cx="770" cy="490" rx="120" ry="28" fill="#F0FDF4" stroke="#10B981" stroke-width="2" />
  <text x="770" y="490" class="uc-ai">Trợ lý AI: Phân tích Kinh doanh</text>

  <ellipse cx="770" cy="620" rx="110" ry="24" fill="#F1F5F9" stroke="#64748B" stroke-width="1.5" />
  <text x="770" y="615" class="uc-sub">«include»</text>
  <text x="770" y="630" class="uc-sub">Cập nhật tồn kho tự động</text>

  <!-- Lines Admin -->
  <line x1="130" y1="360" x2="480" y2="130" stroke="#D97706" stroke-width="1.8" />
  <line x1="130" y1="360" x2="310" y2="220" stroke="#D97706" stroke-width="1.8" />
  <line x1="130" y1="360" x2="310" y2="310" stroke="#D97706" stroke-width="1.8" />
  <line x1="130" y1="360" x2="310" y2="400" stroke="#D97706" stroke-width="1.8" />
  <line x1="130" y1="360" x2="310" y2="490" stroke="#D97706" stroke-width="1.8" />
  <line x1="130" y1="360" x2="310" y2="580" stroke="#D97706" stroke-width="1.8" />
  <line x1="130" y1="360" x2="650" y2="490" stroke="#D97706" stroke-width="1.5" />

  <!-- Lines Owner -->
  <line x1="1070" y1="360" x2="720" y2="130" stroke="#2563EB" stroke-width="1.8" />
  <line x1="1070" y1="360" x2="890" y2="220" stroke="#2563EB" stroke-width="1.8" />
  <line x1="1070" y1="360" x2="890" y2="310" stroke="#2563EB" stroke-width="1.8" />
  <line x1="1070" y1="360" x2="890" y2="400" stroke="#2563EB" stroke-width="1.8" />
  <line x1="1070" y1="360" x2="890" y2="490" stroke="#2563EB" stroke-width="1.8" />
  <line x1="1070" y1="360" x2="550" y2="310" stroke="#2563EB" stroke-width="1.5" />
  <line x1="1070" y1="360" x2="550" y2="400" stroke="#2563EB" stroke-width="1.5" />
  <line x1="1070" y1="360" x2="550" y2="490" stroke="#2563EB" stroke-width="1.5" />

  <!-- Include dashed arrow -->
  <line x1="770" y1="248" x2="770" y2="590" stroke="#475569" stroke-width="1.5" stroke-dasharray="5,5" marker-end="url(#arrow)" />
  <text x="780" y="360" font-family="'Segoe UI', Arial" font-size="11" font-style="italic" fill="#475569">«include»</text>

  <!-- Legend -->
  <rect x="260" y="670" width="340" height="65" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" />
  <text x="275" y="690" class="leg-title">Quy ước chuẩn UML 2.5:</text>
  <line x1="275" y1="705" x2="325" y2="705" stroke="#2563EB" stroke-width="1.8" />
  <text x="335" y="705" class="leg-text">Association (Đường liền nét không mũi tên)</text>
  <line x1="275" y1="722" x2="325" y2="722" stroke="#475569" stroke-width="1.5" stroke-dasharray="4,4" />
  <text x="335" y="722" class="leg-text">«include» (Quan hệ phụ thuộc bắt buộc)</text>
</svg>"""

# ================= 2. SVG: CLASS DIAGRAM =================
def svg_class_diagram():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="780" viewBox="0 0 1380 780">
  <defs>
    <style>
      .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }
      .class-hdr { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #FFFFFF; text-anchor: middle; dominant-baseline: middle; }
      .attr { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #1E293B; }
      .meth { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-style: italic; fill: #0F172A; }
      .multi { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #1D4ED8; }
      .multi-orange { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #B45309; }
      .rel-lbl { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 600; fill: #475569; }
    </style>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563EB" />
    </marker>
    <marker id="arr-orange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#D97706" />
    </marker>
    <marker id="arr-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669" />
    </marker>
  </defs>

  <text x="690" y="35" class="title">SƠ ĐỒ LỚP LĨNH VỰC &amp; THỰC THỂ HỆ THỐNG (DOMAIN CLASS DIAGRAM)</text>

  <!-- ROW 1 -->
  <!-- User (Top Left) -->
  <g transform="translate(50, 65)">
    <rect width="250" height="230" rx="8" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2" />
    <rect width="250" height="32" rx="8" fill="#1E3A8A" />
    <text x="125" y="17" class="class-hdr">«entity» User</text>
    <text x="12" y="55" class="attr">+ id: int [PK]</text>
    <text x="12" y="73" class="attr">+ username: str [UK]</text>
    <text x="12" y="91" class="attr">+ password_hash: str</text>
    <text x="12" y="109" class="attr">+ full_name: str</text>
    <text x="12" y="127" class="attr">+ role: str</text>
    <text x="12" y="145" class="attr">+ is_active: bool</text>
    <text x="12" y="163" class="attr">+ created_at: datetime</text>
    <line x1="0" y1="175" x2="250" y2="175" stroke="#1E3A8A" stroke-width="1.2" />
    <text x="12" y="195" class="meth">+ verify_password(pwd): bool</text>
    <text x="12" y="213" class="meth">+ is_admin(): bool</text>
  </g>

  <!-- Category (Top Center Left) -->
  <g transform="translate(360, 65)">
    <rect width="230" height="150" rx="8" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2" />
    <rect width="230" height="32" rx="8" fill="#1E3A8A" />
    <text x="115" y="17" class="class-hdr">«entity» Category</text>
    <text x="12" y="55" class="attr">+ id: int [PK]</text>
    <text x="12" y="75" class="attr">+ name: str [UK]</text>
    <text x="12" y="95" class="attr">+ description: str</text>
    <line x1="0" y1="110" x2="230" y2="110" stroke="#1E3A8A" stroke-width="1.2" />
    <text x="12" y="132" class="meth">+ get_active_products(): list</text>
  </g>

  <!-- Product (Top Center Right) -->
  <g transform="translate(680, 65)">
    <rect width="260" height="260" rx="8" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2" />
    <rect width="260" height="32" rx="8" fill="#1E3A8A" />
    <text x="130" y="17" class="class-hdr">«entity» Product</text>
    <text x="12" y="55" class="attr">+ id: int [PK]</text>
    <text x="12" y="73" class="attr">+ code: str [UK]</text>
    <text x="12" y="91" class="attr">+ name: str</text>
    <text x="12" y="109" class="attr">+ category_id: int [FK]</text>
    <text x="12" y="127" class="attr">+ import_price: float</text>
    <text x="12" y="145" class="attr">+ sell_price: float</text>
    <text x="12" y="163" class="attr">+ stock: int</text>
    <text x="12" y="181" class="attr">+ status: str</text>
    <text x="12" y="199" class="attr">+ description: str</text>
    <line x1="0" y1="210" x2="260" y2="210" stroke="#1E3A8A" stroke-width="1.2" />
    <text x="12" y="230" class="meth">+ check_stock(qty): bool</text>
    <text x="12" y="248" class="meth">+ update_stock(qty): void</text>
  </g>

  <!-- AIService (Top Right) -->
  <g transform="translate(1030, 65)">
    <rect width="250" height="170" rx="8" fill="#F0FDF4" stroke="#059669" stroke-width="2" />
    <rect width="250" height="32" rx="8" fill="#059669" />
    <text x="125" y="17" class="class-hdr">«service» AIService</text>
    <text x="12" y="58" class="attr">- api_key: str</text>
    <text x="12" y="78" class="attr">- model: str</text>
    <line x1="0" y1="92" x2="250" y2="92" stroke="#059669" stroke-width="1.2" />
    <text x="12" y="112" class="meth">+ consult_products(q): str</text>
    <text x="12" y="132" class="meth">+ analyze_revenue(): str</text>
    <text x="12" y="152" class="meth">- _mask_sensitive(d): dict</text>
  </g>

  <!-- ROW 2 -->
  <!-- PurchaseReceipt (Bottom Left) -->
  <g transform="translate(50, 460)">
    <rect width="250" height="210" rx="8" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2" />
    <rect width="250" height="32" rx="8" fill="#1E3A8A" />
    <text x="125" y="17" class="class-hdr">«entity» PurchaseReceipt</text>
    <text x="12" y="55" class="attr">+ id: int [PK]</text>
    <text x="12" y="75" class="attr">+ code: str [UK]</text>
    <text x="12" y="95" class="attr">+ supplier: str</text>
    <text x="12" y="115" class="attr">+ user_id: int [FK]</text>
    <text x="12" y="135" class="attr">+ total_amount: float</text>
    <text x="12" y="155" class="attr">+ status: str</text>
    <line x1="0" y1="170" x2="250" y2="170" stroke="#1E3A8A" stroke-width="1.2" />
    <text x="12" y="192" class="meth">+ confirm_receipt(): void</text>
  </g>

  <!-- Customer (Bottom Center Left) -->
  <g transform="translate(360, 460)">
    <rect width="230" height="200" rx="8" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2" />
    <rect width="230" height="32" rx="8" fill="#1E3A8A" />
    <text x="115" y="17" class="class-hdr">«entity» Customer</text>
    <text x="12" y="55" class="attr">+ id: int [PK]</text>
    <text x="12" y="75" class="attr">+ name: str</text>
    <text x="12" y="95" class="attr">+ phone: str [UK]</text>
    <text x="12" y="115" class="attr">+ email: str</text>
    <text x="12" y="135" class="attr">+ address: str</text>
    <text x="12" y="155" class="attr">+ customer_group: str</text>
    <line x1="0" y1="168" x2="230" y2="168" stroke="#1E3A8A" stroke-width="1.2" />
    <text x="12" y="188" class="meth">+ get_order_history(): list</text>
  </g>

  <!-- Order (Bottom Center Right) -->
  <g transform="translate(680, 430)">
    <rect width="260" height="270" rx="8" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2" />
    <rect width="260" height="32" rx="8" fill="#1E3A8A" />
    <text x="130" y="17" class="class-hdr">«entity» Order</text>
    <text x="12" y="55" class="attr">+ id: int [PK]</text>
    <text x="12" y="73" class="attr">+ code: str [UK]</text>
    <text x="12" y="91" class="attr">+ customer_id: int [FK]</text>
    <text x="12" y="109" class="attr">+ user_id: int [FK]</text>
    <text x="12" y="127" class="attr">+ total_amount: float</text>
    <text x="12" y="145" class="attr">+ discount: float</text>
    <text x="12" y="163" class="attr">+ final_amount: float</text>
    <text x="12" y="181" class="attr">+ payment_method: str</text>
    <text x="12" y="199" class="attr">+ status: str</text>
    <text x="12" y="217" class="attr">+ created_at: datetime</text>
    <line x1="0" y1="228" x2="260" y2="228" stroke="#1E3A8A" stroke-width="1.2" />
    <text x="12" y="246" class="meth">+ calculate_total(): float</text>
    <text x="12" y="262" class="meth">+ cancel_and_refund(): bool</text>
  </g>

  <!-- OrderDetail (Bottom Right) -->
  <g transform="translate(1030, 460)">
    <rect width="250" height="200" rx="8" fill="#FFFFFF" stroke="#1E3A8A" stroke-width="2" />
    <rect width="250" height="32" rx="8" fill="#1E3A8A" />
    <text x="125" y="17" class="class-hdr">«entity» OrderDetail</text>
    <text x="12" y="55" class="attr">+ id: int [PK]</text>
    <text x="12" y="75" class="attr">+ order_id: int [FK]</text>
    <text x="12" y="95" class="attr">+ product_id: int [FK]</text>
    <text x="12" y="115" class="attr">+ quantity: int</text>
    <text x="12" y="135" class="attr">+ price: float</text>
    <text x="12" y="155" class="attr">+ total: float</text>
    <line x1="0" y1="168" x2="250" y2="168" stroke="#1E3A8A" stroke-width="1.2" />
    <text x="12" y="188" class="meth">+ subtotal(): float</text>
  </g>

  <!-- ================= RELATIONSHIPS ================= -->
  <!-- 1. Category 1 ─── 0..* Product -->
  <line x1="590" y1="130" x2="680" y2="130" stroke="#2563EB" stroke-width="2" />
  <text x="598" y="122" class="multi">1</text>
  <text x="655" y="122" class="multi">0..*</text>
  <text x="635" y="145" class="rel-lbl" text-anchor="middle">chứa</text>

  <!-- 2. Order 1 ◆─── 1..* OrderDetail (Composition) -->
  <polygon points="940,540 952,548 964,540 952,532" fill="#1E3A8A" stroke="#1E3A8A" />
  <line x1="964" y1="540" x2="1030" y2="540" stroke="#1E3A8A" stroke-width="2" />
  <text x="968" y="528" class="multi">1</text>
  <text x="1005" y="528" class="multi">1..*</text>
  <text x="985" y="560" class="rel-lbl" text-anchor="middle">«composition»</text>

  <!-- 3. Product 1 ───► 0..* OrderDetail -->
  <path d="M 940 280 L 985 280 L 985 490 L 1030 490" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arr-blue)" />
  <text x="948" y="272" class="multi">1</text>
  <text x="995" y="482" class="multi">0..*</text>

  <!-- 4. Customer 0..1 ───► 0..* Order -->
  <line x1="590" y1="540" x2="670" y2="540" stroke="#2563EB" stroke-width="2" marker-end="url(#arr-blue)" />
  <text x="598" y="530" class="multi">0..1</text>
  <text x="645" y="530" class="multi">0..*</text>
  <text x="630" y="560" class="rel-lbl" text-anchor="middle">đặt mua</text>

  <!-- 5. User 1 ───► 0..* Order (Lập đơn hàng: Đi qua khe giữa, không cắt qua Category!) -->
  <path d="M 300 240 L 335 240 L 335 375 L 810 375 L 810 420" fill="none" stroke="#D97706" stroke-width="2" marker-end="url(#arr-orange)" />
  <text x="308" y="232" class="multi-orange">1</text>
  <text x="818" y="415" class="multi-orange">0..*</text>
  <text x="560" y="365" class="rel-lbl" fill="#B45309" text-anchor="middle">lập đơn hàng (creates order)</text>

  <!-- 6. User 1 ───► 0..* PurchaseReceipt (Nhập kho) -->
  <line x1="175" y1="295" x2="175" y2="450" stroke="#D97706" stroke-width="2" marker-end="url(#arr-orange)" />
  <text x="185" y="320" class="multi-orange">1</text>
  <text x="185" y="445" class="multi-orange">0..*</text>
  <text x="120" y="380" class="rel-lbl" fill="#B45309">nhập kho</text>

  <!-- 7. AIService ─ ─ ─► Product («use») -->
  <line x1="1030" y1="140" x2="950" y2="140" stroke="#059669" stroke-width="1.8" stroke-dasharray="5,5" marker-end="url(#arr-green)" />
  <text x="990" y="130" class="rel-lbl" fill="#059669" text-anchor="middle">«use»</text>

  <!-- 8. AIService ─ ─ ─► Order («analyze»: Đi vòng ngoài cùng) -->
  <path d="M 1280 150 L 1320 150 L 1320 730 L 810 730 L 810 710" fill="none" stroke="#059669" stroke-width="1.8" stroke-dasharray="5,5" marker-end="url(#arr-green)" />
  <text x="1080" y="748" class="rel-lbl" fill="#059669" text-anchor="middle">«analyze»</text>
</svg>"""

# ================= 3. SVG: ERD =================
def svg_erd():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1380" height="780" viewBox="0 0 1380 780">
  <defs>
    <style>
      .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }
      .tbl-hdr { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #FFFFFF; text-anchor: middle; dominant-baseline: middle; }
      .pk { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: bold; fill: #B91C1C; }
      .fk { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: bold; fill: #1D4ED8; }
      .col { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #334155; }
      .card { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #1D4ED8; }
      .card-orange { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #B45309; }
      .lbl { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; font-weight: 600; fill: #475569; }
    </style>
    <marker id="arr-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563EB" />
    </marker>
    <marker id="arr-orange" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#D97706" />
    </marker>
  </defs>

  <text x="690" y="35" class="title">SƠ ĐỒ QUAN HỆ THỰC THỂ CSDL (ERD - 7 BẢNG CỐT LÕI SALES.DB)</text>

  <!-- ROW 1 -->
  <!-- USERS -->
  <g transform="translate(50, 65)">
    <rect width="250" height="210" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="2" />
    <rect width="250" height="30" rx="8" fill="#1E3A8A" />
    <text x="125" y="16" class="tbl-hdr">USERS</text>
    <text x="14" y="52" class="pk">PK id : integer</text>
    <text x="14" y="74" class="col">UK username : varchar(50)</text>
    <text x="14" y="96" class="col">password_hash : varchar(255)</text>
    <text x="14" y="118" class="col">full_name : varchar(100)</text>
    <text x="14" y="140" class="col">role : varchar(20)</text>
    <text x="14" y="162" class="col">is_active : boolean</text>
    <text x="14" y="184" class="col">created_at : timestamp</text>
  </g>

  <!-- CATEGORIES -->
  <g transform="translate(360, 65)">
    <rect width="230" height="140" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="2" />
    <rect width="230" height="30" rx="8" fill="#1E3A8A" />
    <text x="115" y="16" class="tbl-hdr">CATEGORIES</text>
    <text x="14" y="52" class="pk">PK id : integer</text>
    <text x="14" y="78" class="col">UK name : varchar(100)</text>
    <text x="14" y="104" class="col">description : text</text>
  </g>

  <!-- PRODUCTS -->
  <g transform="translate(680, 65)">
    <rect width="260" height="260" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="2" />
    <rect width="260" height="30" rx="8" fill="#1E3A8A" />
    <text x="130" y="16" class="tbl-hdr">PRODUCTS</text>
    <text x="14" y="52" class="pk">PK id : integer</text>
    <text x="14" y="72" class="col">UK code : varchar(50)</text>
    <text x="14" y="92" class="col">name : varchar(200)</text>
    <text x="14" y="112" class="fk">FK category_id : integer</text>
    <text x="14" y="132" class="col">import_price : decimal(12,2)</text>
    <text x="14" y="152" class="col">sell_price : decimal(12,2)</text>
    <text x="14" y="172" class="col">stock : integer</text>
    <text x="14" y="192" class="col">status : varchar(20)</text>
    <text x="14" y="212" class="col">description : text</text>
  </g>

  <!-- INVENTORIES -->
  <g transform="translate(1030, 65)">
    <rect width="250" height="140" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="2" />
    <rect width="250" height="30" rx="8" fill="#1E3A8A" />
    <text x="125" y="16" class="tbl-hdr">INVENTORIES</text>
    <text x="14" y="52" class="pk">PK id : integer</text>
    <text x="14" y="78" class="fk">FK product_id : integer</text>
    <text x="14" y="104" class="col">quantity : integer</text>
  </g>

  <!-- ROW 2 -->
  <!-- CUSTOMERS -->
  <g transform="translate(50, 440)">
    <rect width="250" height="190" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="2" />
    <rect width="250" height="30" rx="8" fill="#1E3A8A" />
    <text x="125" y="16" class="tbl-hdr">CUSTOMERS</text>
    <text x="14" y="52" class="pk">PK id : integer</text>
    <text x="14" y="75" class="col">name : varchar(100)</text>
    <text x="14" y="98" class="col">UK phone : varchar(20)</text>
    <text x="14" y="121" class="col">email : varchar(100)</text>
    <text x="14" y="144" class="col">address : text</text>
    <text x="14" y="167" class="col">customer_group : varchar(50)</text>
  </g>

  <!-- ORDERS -->
  <g transform="translate(360, 410)">
    <rect width="260" height="260" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="2" />
    <rect width="260" height="30" rx="8" fill="#1E3A8A" />
    <text x="130" y="16" class="tbl-hdr">ORDERS</text>
    <text x="14" y="52" class="pk">PK id : integer</text>
    <text x="14" y="72" class="col">UK code : varchar(50)</text>
    <text x="14" y="92" class="fk">FK customer_id : integer</text>
    <text x="14" y="112" class="fk">FK user_id : integer</text>
    <text x="14" y="132" class="col">total_amount : decimal(12,2)</text>
    <text x="14" y="152" class="col">discount : decimal(12,2)</text>
    <text x="14" y="172" class="col">final_amount : decimal(12,2)</text>
    <text x="14" y="192" class="col">payment_method : varchar(30)</text>
    <text x="14" y="212" class="col">status : varchar(20)</text>
    <text x="14" y="232" class="col">created_at : timestamp</text>
  </g>

  <!-- ORDER_DETAILS -->
  <g transform="translate(700, 440)">
    <rect width="240" height="190" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="2" />
    <rect width="240" height="30" rx="8" fill="#1E3A8A" />
    <text x="120" y="16" class="tbl-hdr">ORDER_DETAILS</text>
    <text x="14" y="52" class="pk">PK id : integer</text>
    <text x="14" y="78" class="fk">FK order_id : integer</text>
    <text x="14" y="104" class="fk">FK product_id : integer</text>
    <text x="14" y="130" class="col">quantity : integer</text>
    <text x="14" y="156" class="col">price : decimal(12,2)</text>
    <text x="14" y="178" class="col">total : decimal(12,2)</text>
  </g>

  <!-- PURCHASE_RECEIPTS -->
  <g transform="translate(1030, 440)">
    <rect width="250" height="190" rx="8" fill="#FFFFFF" stroke="#3B82F6" stroke-width="2" />
    <rect width="250" height="30" rx="8" fill="#1E3A8A" />
    <text x="125" y="16" class="tbl-hdr">PURCHASE_RECEIPTS</text>
    <text x="14" y="52" class="pk">PK id : integer</text>
    <text x="14" y="75" class="col">UK code : varchar(50)</text>
    <text x="14" y="98" class="col">supplier : varchar(150)</text>
    <text x="14" y="121" class="fk">FK user_id : integer</text>
    <text x="14" y="144" class="col">total_amount : decimal(12,2)</text>
    <text x="14" y="167" class="col">status : varchar(20)</text>
    <text x="14" y="186" class="col">created_at : timestamp</text>
  </g>

  <!-- ================= RELATIONSHIPS & ARROWS ================= -->
  <!-- 1. CATEGORIES (1) ───► (1..N) PRODUCTS -->
  <line x1="590" y1="130" x2="670" y2="130" stroke="#2563EB" stroke-width="2" marker-end="url(#arr-blue)" />
  <text x="598" y="122" class="card">1</text>
  <text x="645" y="122" class="card">1..N</text>
  <text x="630" y="145" class="lbl" text-anchor="middle">phân loại</text>

  <!-- 2. PRODUCTS (1) ───► (1..1) INVENTORIES -->
  <line x1="940" y1="130" x2="1020" y2="130" stroke="#2563EB" stroke-width="2" marker-end="url(#arr-blue)" />
  <text x="948" y="122" class="card">1</text>
  <text x="995" y="122" class="card">1..1</text>
  <text x="980" y="145" class="lbl" text-anchor="middle">tồn kho</text>

  <!-- 3. CUSTOMERS (1) ───► (0..N) ORDERS -->
  <line x1="300" y1="520" x2="350" y2="520" stroke="#2563EB" stroke-width="2" marker-end="url(#arr-blue)" />
  <text x="308" y="510" class="card">1</text>
  <text x="330" y="510" class="card">0..N</text>
  <text x="325" y="540" class="lbl" text-anchor="middle">đặt mua</text>

  <!-- 4. ORDERS (1) ───► (1..N) ORDER_DETAILS -->
  <line x1="620" y1="520" x2="690" y2="520" stroke="#2563EB" stroke-width="2" marker-end="url(#arr-blue)" />
  <text x="628" y="510" class="card">1</text>
  <text x="665" y="510" class="card">1..N</text>
  <text x="655" y="540" class="lbl" text-anchor="middle">chi tiết</text>

  <!-- 5. PRODUCTS (1) ───► (0..N) ORDER_DETAILS -->
  <path d="M 810 325 L 810 430" fill="none" stroke="#2563EB" stroke-width="2" marker-end="url(#arr-blue)" />
  <text x="818" y="350" class="card">1</text>
  <text x="818" y="425" class="card">0..N</text>

  <!-- 6. USERS (1) ───► (0..N) ORDERS (Lập đơn) -->
  <path d="M 230 275 L 230 360 L 450 360 L 450 400" fill="none" stroke="#D97706" stroke-width="2" marker-end="url(#arr-orange)" />
  <text x="238" y="300" class="card-orange">1</text>
  <text x="458" y="395" class="card-orange">0..N</text>
  <text x="330" y="352" class="lbl" fill="#B45309" text-anchor="middle">lập đơn (FK user_id)</text>

  <!-- 7. USERS (1) ───► (0..N) PURCHASE_RECEIPTS (Nhập kho) -->
  <path d="M 120 275 L 120 380 L 1150 380 L 1150 430" fill="none" stroke="#D97706" stroke-width="2" marker-end="url(#arr-orange)" />
  <text x="128" y="300" class="card-orange">1</text>
  <text x="1158" y="425" class="card-orange">0..N</text>
  <text x="980" y="372" class="lbl" fill="#B45309" text-anchor="middle">nhập kho (FK user_id)</text>
</svg>"""

# ================= 4. SVG: ARCHITECTURE =================
def svg_architecture():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700">
  <defs>
    <style>
      .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }
      .layer-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 15px; font-weight: bold; }
      .box-title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #0F172A; text-anchor: middle; dominant-baseline: middle; }
      .box-sub { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #475569; text-anchor: middle; dominant-baseline: middle; }
      .conn-text { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #1E3A8A; }
    </style>
  </defs>

  <text x="600" y="35" class="title">SƠ ĐỒ KIẾN TRÚC HỆ THỐNG 3 TẦNG (SYSTEM ARCHITECTURE)</text>

  <!-- Layer 1: Client -->
  <g transform="translate(50, 60)">
    <rect width="1100" height="150" rx="12" fill="#F8FAFC" stroke="#3B82F6" stroke-width="2" />
    <text x="25" y="30" class="layer-title" fill="#1E3A8A">1. TẦNG GIAO DIỆN CLIENT (React 18 SPA + Vite + Tailwind/CSS)</text>
    
    <rect x="40" y="50" width="310" height="75" rx="8" fill="#EFF6FF" stroke="#60A5FA" stroke-width="1.5" />
    <text x="195" y="80" class="box-title">Màn hình Bán hàng POS</text>
    <text x="195" y="100" class="box-sub">Quét mã, giỏ hàng, in bill hóa đơn</text>

    <rect x="390" y="50" width="320" height="75" rx="8" fill="#EFF6FF" stroke="#60A5FA" stroke-width="1.5" />
    <text x="550" y="80" class="box-title">Dashboard &amp; Báo cáo Thống kê</text>
    <text x="550" y="100" class="box-sub">Biểu đồ doanh thu, top sản phẩm, kho</text>

    <rect x="750" y="50" width="310" height="75" rx="8" fill="#F0FDF4" stroke="#34D399" stroke-width="1.5" />
    <text x="905" y="80" class="box-title" fill="#065F46">Trợ lý AI Bán hàng &amp; Chat</text>
    <text x="905" y="100" class="box-sub">Tư vấn chọn SP, phân tích doanh thu</text>
  </g>

  <!-- Arrow Client -> Server -->
  <line x1="600" y1="210" x2="600" y2="265" stroke="#1E3A8A" stroke-width="2.5" />
  <text x="615" y="242" class="conn-text">RESTful API / JSON Web Token (Bearer Auth)</text>

  <!-- Layer 2: Server -->
  <g transform="translate(50, 265)">
    <rect width="1100" height="210" rx="12" fill="#F8FAFC" stroke="#10B981" stroke-width="2" />
    <text x="25" y="30" class="layer-title" fill="#065F46">2. TẦNG NGHIỆP VỤ &amp; DỊCH VỤ BACKEND (FastAPI - Python 3.12)</text>

    <!-- Routers -->
    <rect x="40" y="50" width="500" height="65" rx="8" fill="#F0FDF4" stroke="#6EE7B7" stroke-width="1.5" />
    <text x="290" y="75" class="box-title" fill="#065F46">Core API Routers</text>
    <text x="290" y="95" class="box-sub">/auth, /products, /categories, /orders, /customers, /reports</text>

    <rect x="570" y="50" width="490" height="65" rx="8" fill="#FEF3C7" stroke="#FCD34D" stroke-width="1.5" />
    <text x="815" y="75" class="box-title" fill="#92400E">AI Assistant Router</text>
    <text x="815" y="95" class="box-sub">/api/ai/consult (Tư vấn SP) &amp; /api/ai/report (Phân tích doanh thu)</text>

    <!-- Services -->
    <rect x="40" y="125" width="500" height="65" rx="8" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1.5" />
    <text x="290" y="150" class="box-title" fill="#065F46">Business Services &amp; Repository Layer</text>
    <text x="290" y="170" class="box-sub">OrderService, InventoryManager, ReportExporter, SQLAlchemy ORM</text>

    <rect x="570" y="125" width="490" height="65" rx="8" fill="#FEF3C7" stroke="#FCD34D" stroke-width="1.5" />
    <text x="815" y="150" class="box-title" fill="#92400E">AI Service Layer (Guardrails &amp; Masking)</text>
    <text x="815" y="170" class="box-sub">Prompt Engineering, Data Masking (ẩn giá vốn), Fallback Handler</text>
  </g>

  <!-- Arrow Server -> Data -->
  <line x1="290" y1="475" x2="290" y2="530" stroke="#1E3A8A" stroke-width="2.5" />
  <line x1="815" y1="475" x2="815" y2="530" stroke="#D97706" stroke-width="2.5" />

  <!-- Layer 3: Data & Cloud -->
  <g transform="translate(50, 530)">
    <rect width="1100" height="130" rx="12" fill="#F8FAFC" stroke="#6366F1" stroke-width="2" />
    <text x="25" y="30" class="layer-title" fill="#3730A3">3. TẦNG DỮ LIỆU &amp; DỊCH VỤ ĐIỆN TOÁN NGOẠI VI (Data &amp; Cloud Services)</text>

    <rect x="40" y="45" width="500" height="65" rx="8" fill="#EEF2FF" stroke="#A5B4FC" stroke-width="1.5" />
    <text x="290" y="70" class="box-title" fill="#312E81">📁 SQLite Database: sales.db</text>
    <text x="290" y="90" class="box-sub">7 Bảng cốt lõi: users, categories, products, orders, order_details, customers, receipts</text>

    <rect x="570" y="45" width="490" height="65" rx="8" fill="#FFFBEB" stroke="#FDE68A" stroke-width="1.5" />
    <text x="815" y="70" class="box-title" fill="#B45309">☁️ OpenAI Cloud API (GPT-4o-mini)</text>
    <text x="815" y="90" class="box-sub">Mô hình ngôn ngữ lớn xử lý NLP ngữ nghĩa &amp; gợi ý quyết định bán hàng</text>
  </g>
</svg>"""

# ================= 5. SVG: ACTIVITY POS =================
def svg_activity_pos():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="500" viewBox="0 0 1200 500">
  <defs>
    <style>
      .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }
      .box-t { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #0F172A; text-anchor: middle; dominant-baseline: middle; }
      .box-s { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #475569; text-anchor: middle; dominant-baseline: middle; }
      .cond { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #16A34A; }
      .err { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #DC2626; }
    </style>
  </defs>

  <text x="600" y="35" class="title">SƠ ĐỒ HOẠT ĐỘNG: QUY TRÌNH BÁN HÀNG TẠI QUẦY (POS) &amp; TRỪ TỒN KHO</text>

  <!-- Start -->
  <circle cx="80" cy="250" r="22" fill="#1E3A8A" />
  <circle cx="80" cy="250" r="16" fill="#FFFFFF" />
  <text x="80" y="295" class="box-s">Bắt đầu</text>

  <!-- Step 1 -->
  <rect x="150" y="215" width="150" height="70" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2" />
  <text x="225" y="242" class="box-t">1. Chọn sản phẩm</text>
  <text x="225" y="262" class="box-s">Tìm kiếm / Quét mã barcode</text>

  <!-- Step 2: Decision -->
  <polygon points="390,250 460,205 530,250 460,295" fill="#FEF3C7" stroke="#F59E0B" stroke-width="2" />
  <text x="460" y="245" class="box-t">2. Kiểm tra</text>
  <text x="460" y="260" class="box-s">stock &gt;= qty?</text>

  <!-- Step 3 -->
  <rect x="620" y="215" width="160" height="70" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2" />
  <text x="700" y="242" class="box-t">3. Nhập giảm giá</text>
  <text x="700" y="262" class="box-s">Chọn PT thanh toán</text>

  <!-- Step 4 -->
  <rect x="850" y="215" width="170" height="70" rx="8" fill="#F0FDF4" stroke="#10B981" stroke-width="2" />
  <text x="935" y="242" class="box-t">4. Commit Đơn hàng</text>
  <text x="935" y="262" class="box-s">Tự động trừ kho (stock -= qty)</text>

  <!-- End -->
  <circle cx="1120" cy="250" r="22" fill="#16A34A" />
  <circle cx="1120" cy="250" r="16" fill="#DCFCE7" />
  <circle cx="1120" cy="250" r="10" fill="#16A34A" />
  <text x="1120" y="295" class="box-s">In bill &amp; Xong</text>

  <!-- Arrows -->
  <line x1="102" y1="250" x2="150" y2="250" stroke="#1E3A8A" stroke-width="2" />
  <line x1="300" y1="250" x2="390" y2="250" stroke="#1E3A8A" stroke-width="2" />
  <line x1="530" y1="250" x2="620" y2="250" stroke="#1E3A8A" stroke-width="2" />
  <text x="560" y="240" class="cond">[Đủ hàng]</text>

  <line x1="780" y1="250" x2="850" y2="250" stroke="#1E3A8A" stroke-width="2" />
  <line x1="1020" y1="250" x2="1098" y2="250" stroke="#1E3A8A" stroke-width="2" />

  <!-- Reject Loop -->
  <path d="M 460 205 L 460 130 L 225 130 L 225 215" fill="none" stroke="#DC2626" stroke-width="2" />
  <text x="340" y="115" class="err">[Hết hàng / Thiếu tồn kho] Báo lỗi &amp; chọn lại</text>
</svg>"""

# ================= 6. SVG: ACTIVITY AI =================
def svg_activity_ai():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="520" viewBox="0 0 1200 520">
  <defs>
    <style>
      .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }
      .box-t { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #0F172A; text-anchor: middle; dominant-baseline: middle; }
      .box-s { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; fill: #475569; text-anchor: middle; dominant-baseline: middle; }
    </style>
  </defs>

  <text x="600" y="35" class="title">SƠ ĐỒ HOẠT ĐỘNG: TRỢ LÝ AI TƯ VẤN &amp; BẢO VỆ DỮ LIỆU NHẠY CẢM</text>

  <!-- Start -->
  <circle cx="70" cy="220" r="20" fill="#1E3A8A" />
  <text x="70" y="260" class="box-s">Nhận câu hỏi</text>

  <!-- Step 1 -->
  <rect x="140" y="185" width="150" height="70" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2" />
  <text x="215" y="212" class="box-t">1. Rate Limiting</text>
  <text x="215" y="232" class="box-s">Giới hạn tần suất gọi</text>

  <!-- Step 2 -->
  <rect x="330" y="185" width="170" height="70" rx="8" fill="#FEE2E2" stroke="#EF4444" stroke-width="2" />
  <text x="415" y="212" class="box-t" fill="#991B1B">2. Data Masking</text>
  <text x="415" y="232" class="box-s" fill="#7F1D1D">Ẩn giá vốn, số ĐT khách</text>

  <!-- Step 3 -->
  <rect x="540" y="185" width="160" height="70" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="2" />
  <text x="620" y="212" class="box-t">3. Lọc Kho hàng</text>
  <text x="620" y="232" class="box-s">Chỉ lấy SP stock &gt; 0</text>

  <!-- Step 4 -->
  <rect x="740" y="185" width="160" height="70" rx="8" fill="#FEF3C7" stroke="#F59E0B" stroke-width="2" />
  <text x="820" y="212" class="box-t" fill="#92400E">4. Gọi OpenAI API</text>
  <text x="820" y="232" class="box-s">GPT-4o-mini (Timeout 30s)</text>

  <!-- End -->
  <circle cx="1100" cy="220" r="22" fill="#16A34A" />
  <circle cx="1100" cy="220" r="16" fill="#DCFCE7" />
  <circle cx="1100" cy="220" r="10" fill="#16A34A" />
  <text x="1100" y="260" class="box-s">Trả lời người dùng</text>

  <!-- Connections -->
  <line x1="90" y1="220" x2="140" y2="220" stroke="#1E3A8A" stroke-width="2" />
  <line x1="290" y1="220" x2="330" y2="220" stroke="#1E3A8A" stroke-width="2" />
  <line x1="500" y1="220" x2="540" y2="220" stroke="#1E3A8A" stroke-width="2" />
  <line x1="700" y1="220" x2="740" y2="220" stroke="#1E3A8A" stroke-width="2" />
  <line x1="900" y1="220" x2="1078" y2="220" stroke="#1E3A8A" stroke-width="2" />

  <!-- Fallback Branch -->
  <rect x="740" y="340" width="160" height="70" rx="8" fill="#F1F5F9" stroke="#64748B" stroke-width="2" />
  <text x="820" y="367" class="box-t">Fallback Response</text>
  <text x="820" y="387" class="box-s">Gợi ý danh mục mặc định</text>

  <line x1="820" y1="255" x2="820" y2="340" stroke="#DC2626" stroke-width="2" />
  <text x="830" y="300" font-family="'Segoe UI', Arial" font-size="11" font-weight="bold" fill="#DC2626">Lỗi / Mất mạng</text>
  <path d="M 900 375 L 1100 375 L 1100 245" fill="none" stroke="#64748B" stroke-width="2" />
</svg>"""

# ================= 7. SVG: SEQUENCE POS =================
def svg_sequence_pos():
    return """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600">
  <defs>
    <style>
      .title { font-family: 'Segoe UI', Arial, sans-serif; font-size: 20px; font-weight: bold; fill: #1E3A8A; text-anchor: middle; }
      .actor-box { font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #FFFFFF; text-anchor: middle; dominant-baseline: middle; }
      .msg { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #1E3A8A; }
      .succ { font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px; font-weight: bold; fill: #16A34A; }
    </style>
  </defs>

  <text x="600" y="35" class="title">SƠ ĐỒ TUẦN TỰ: GIAO DỊCH BÁN HÀNG TẠI QUẦY (POS) &amp; LẬP HÓA ĐƠN</text>

  <!-- Lifelines -->
  <!-- Cashier / Owner -->
  <g transform="translate(100, 60)">
    <rect width="140" height="40" rx="6" fill="#1E3A8A" />
    <text x="70" y="20" class="actor-box">Người bán (Owner)</text>
    <line x1="70" y1="40" x2="70" y2="480" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="4,4" />
  </g>

  <!-- React POS UI -->
  <g transform="translate(380, 60)">
    <rect width="160" height="40" rx="6" fill="#2563EB" />
    <text x="80" y="20" class="actor-box">Giao diện POS (React)</text>
    <line x1="80" y1="40" x2="80" y2="480" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="4,4" />
  </g>

  <!-- Backend API -->
  <g transform="translate(680, 60)">
    <rect width="160" height="40" rx="6" fill="#059669" />
    <text x="80" y="20" class="actor-box">FastAPI Backend</text>
    <line x1="80" y1="40" x2="80" y2="480" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="4,4" />
  </g>

  <!-- SQLite DB -->
  <g transform="translate(970, 60)">
    <rect width="150" height="40" rx="6" fill="#D97706" />
    <text x="75" y="20" class="actor-box">SQLite (sales.db)</text>
    <line x1="75" y1="40" x2="75" y2="480" stroke="#94A3B8" stroke-width="1.5" stroke-dasharray="4,4" />
  </g>

  <!-- Messages -->
  <!-- 1 -->
  <line x1="170" y1="140" x2="460" y2="140" stroke="#1E3A8A" stroke-width="2" />
  <text x="210" y="132" class="msg">1. Chọn sản phẩm &amp; Bấm thanh toán</text>

  <!-- 2 -->
  <line x1="460" y1="190" x2="760" y2="190" stroke="#1E3A8A" stroke-width="2" />
  <text x="490" y="182" class="msg">2. POST /api/orders (kèm Bearer Token)</text>

  <!-- 3 -->
  <line x1="760" y1="240" x2="1045" y2="240" stroke="#1E3A8A" stroke-width="2" />
  <text x="810" y="232" class="msg">3. BEGIN TRANSACTION</text>

  <!-- 4 -->
  <line x1="760" y1="290" x2="1045" y2="290" stroke="#1E3A8A" stroke-width="2" />
  <text x="780" y="282" class="msg">4. Kiểm tra &amp; Trừ tồn kho (stock = stock - qty)</text>

  <!-- 5 -->
  <line x1="760" y1="340" x2="1045" y2="340" stroke="#1E3A8A" stroke-width="2" />
  <text x="800" y="332" class="msg">5. INSERT INTO orders &amp; order_details</text>

  <!-- 6 -->
  <line x1="760" y1="390" x2="1045" y2="390" stroke="#16A34A" stroke-width="2" />
  <text x="830" y="382" class="succ">6. COMMIT TRANSACTION</text>

  <!-- 7 -->
  <line x1="760" y1="440" x2="460" y2="440" stroke="#16A34A" stroke-width="2" stroke-dasharray="4,4" />
  <text x="500" y="432" class="succ">7. HTTP 201 Created (Chi tiết hóa đơn)</text>

  <!-- 8 -->
  <line x1="460" y1="480" x2="170" y2="480" stroke="#16A34A" stroke-width="2" stroke-dasharray="4,4" />
  <text x="210" y="472" class="succ">8. Hiển thị thông báo thành công &amp; In bill</text>
</svg>"""

# List of diagrams
diagrams = [
    ("01_use_case.html", "Sơ đồ Use Case Tổng quát", svg_usecase()),
    ("02_class_diagram.html", "Sơ đồ Lớp Lĩnh vực (Domain Class Diagram)", svg_class_diagram()),
    ("03_erd.html", "Sơ đồ Quan hệ Thực thể CSDL (ERD - 7 Bảng)", svg_erd()),
    ("04_architecture.html", "Sơ đồ Kiến trúc Hệ thống 3 Tầng", svg_architecture()),
    ("05_seq_pos.html", "Sơ đồ Hoạt động Bán hàng POS & Trừ Kho", svg_activity_pos()),
    ("06_seq_ai.html", "Sơ đồ Hoạt động Trợ lý AI & Data Masking", svg_activity_ai()),
    ("07_state_order.html", "Sơ đồ Tuần tự Giao dịch POS", svg_sequence_pos()),
]

print("Generating 7 standalone interactive HTML diagram viewers...")
for filename, title, svg in diagrams:
    html_content = wrap_viewer(title, svg)
    for target_dir in TARGET_DIRS:
        out_path = os.path.join(target_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Generated: {out_path}")

print("All 7 interactive HTML viewers generated successfully!")
