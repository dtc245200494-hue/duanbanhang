import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api, { fmtMoney } from '../services/api.js'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [err, setErr] = useState('')

  useEffect(() => {
    api.get('/dashboard')
      .then((r) => setData(r.data))
      .catch((e) => setErr(e?.response?.data?.detail || 'Lỗi tải dashboard'))
  }, [])

  if (err) return <div className="error">{err}</div>
  if (!data) return <div className="loading">Đang tải...</div>

  const cards = [
    { label: 'Tổng doanh thu', value: fmtMoney(data.total_revenue), cls: 'green' },
    { label: 'Doanh thu hôm nay', value: fmtMoney(data.today_revenue), cls: 'blue' },
    { label: 'Doanh thu tháng này', value: fmtMoney(data.month_revenue), cls: 'blue' },
    { label: 'Số hóa đơn (tháng)', value: data.month_orders, cls: 'gray' },
    { label: 'Sản phẩm đang bán', value: `${data.active_products}/${data.total_products}`, cls: 'gray' },
    { label: 'Khách hàng', value: data.total_customers, cls: 'gray' },
    { label: '⚠️ Sắp hết hàng', value: data.low_stock_count, cls: 'red' }
  ]

  return (
    <div>
      <h1>Dashboard</h1>
      <div className="cards">
        {cards.map((c) => (
          <div key={c.label} className={`card ${c.cls}`}>
            <div className="card-label">{c.label}</div>
            <div className="card-value">{c.value}</div>
          </div>
        ))}
      </div>

      <div className="two-col">
        <section className="panel">
          <h3>🏆 Sản phẩm bán chạy (tháng này)</h3>
          <table>
            <thead>
              <tr><th>Sản phẩm</th><th>SL</th><th>Doanh thu</th></tr>
            </thead>
            <tbody>
              {data.top_products.map((t) => (
                <tr key={t.product_id}>
                  <td>{t.name}</td>
                  <td>{t.quantity}</td>
                  <td>{fmtMoney(t.revenue)}</td>
                </tr>
              ))}
              {data.top_products.length === 0 && <tr><td colSpan="3">Chưa có dữ liệu</td></tr>}
            </tbody>
          </table>
        </section>

        <section className="panel">
          <h3>⚠️ Sản phẩm sắp hết hàng</h3>
          <table>
            <thead>
              <tr><th>Sản phẩm</th><th>Tồn kho</th><th></th></tr>
            </thead>
            <tbody>
              {data.low_stock_products.map((p) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td className={p.stock <= 2 ? 'danger' : 'warn'}>{p.stock}</td>
                  <td><Link to="/purchases" className="link">Nhập thêm</Link></td>
                </tr>
              ))}
              {data.low_stock_products.length === 0 && <tr><td colSpan="3">Tồn kho ổn định ✅</td></tr>}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  )
}
