import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext.jsx'

const roleLabel = { admin: 'Quản trị viên', owner: 'Chủ cửa hàng' }

export default function Layout() {
  const { user, logout } = useAuth()
  const nav = useNavigate()

  const links = [
    { to: '/', label: '📊 Dashboard', end: true },
    { to: '/products', label: '📦 Sản phẩm' },
    { to: '/customers', label: '👥 Khách hàng' },
    { to: '/orders', label: '🧾 Hóa đơn' },
    { to: '/purchases', label: '🚚 Nhập hàng' },
    { to: '/reports', label: '📈 Báo cáo' },
    { to: '/ai', label: '🤖 Trợ lý AI' }
  ]

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <h2>🛒 SalesAI</h2>
          <small>Quản lý bán hàng</small>
        </div>
        <nav>
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => (isActive ? 'active' : '')}>
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="main">
        <header className="topbar">
          <div />
          <div className="userbox">
            <span className="username">{user?.full_name || user?.username}</span>
            <span className="badge">{roleLabel[user?.role] || user?.role}</span>
            <button
              className="btn ghost"
              onClick={() => {
                logout()
                nav('/login')
              }}
            >
              Đăng xuất
            </button>
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
