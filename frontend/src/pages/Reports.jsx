import { useEffect, useState } from 'react'
import api, { fmtMoney, errDetail } from '../services/api.js'

const monthStart = () => {
  const d = new Date()
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10)
}
const today = () => new Date().toISOString().slice(0, 10)

export default function Reports() {
  const [range, setRange] = useState({ date_from: monthStart(), date_to: today() })
  const [tab, setTab] = useState('revenue')
  const [rows, setRows] = useState([])
  const [msg, setMsg] = useState('')
  const [aiReport, setAiReport] = useState('')
  const [aiLoading, setAiLoading] = useState(false)

  const load = () => {
    setMsg('')
    const url = {
      revenue: '/reports/revenue?group_by=day',
      category: '/reports/by-category',
      top: '/reports/top-products?limit=10',
      slow: '/reports/slow-products?limit=10'
    }[tab]
    api.get(url, { params: range }).then((r) => setRows(r.data)).catch((e) => setMsg(errDetail(e)))
  }

  useEffect(() => { load() }, [tab])

  const exportFile = async (format) => {
    try {
      const r = await api.get('/reports/export', {
        params: { ...range, type: 'sales', format },
        responseType: 'blob'
      })
      const url = URL.createObjectURL(r.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `report_sales_${today()}.${format === 'excel' ? 'xlsx' : format}`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) { setMsg(errDetail(e)) }
  }

  const runAi = async () => {
    setAiLoading(true); setAiReport(''); setMsg('')
    try {
      const r = await api.post('/ai/report', range)
      setAiReport(r.data.answer)
    } catch (e) { setMsg(errDetail(e)) } finally { setAiLoading(false) }
  }

  const cols = {
    revenue: [['label', 'Ngày'], ['orders', 'Số HĐ'], ['revenue', 'Doanh thu']],
    category: [['category', 'Nhóm hàng'], ['quantity', 'SL bán'], ['revenue', 'Doanh thu']],
    top: [['code', 'Mã'], ['name', 'Sản phẩm'], ['quantity', 'SL bán'], ['revenue', 'Doanh thu']],
    slow: [['code', 'Mã'], ['name', 'Sản phẩm'], ['quantity', 'SL bán']]
  }[tab]

  return (
    <div>
      <div className="page-head"><h1>Báo cáo</h1></div>

      <div className="filters">
        <label>Từ <input type="date" value={range.date_from} onChange={(e) => setRange({ ...range, date_from: e.target.value })} /></label>
        <label>Đến <input type="date" value={range.date_to} onChange={(e) => setRange({ ...range, date_to: e.target.value })} /></label>
        <button className="btn" onClick={load}>Xem</button>
        <span className="spacer" />
        <button className="btn" onClick={() => exportFile('csv')}>⬇ CSV</button>
        <button className="btn" onClick={() => exportFile('excel')}>⬇ Excel</button>
        <button className="btn" onClick={() => exportFile('pdf')}>⬇ PDF</button>
      </div>

      <div className="tabs">
        {[['revenue', 'Doanh thu ngày'], ['category', 'Theo nhóm hàng'], ['top', 'Top bán chạy'], ['slow', 'Bán chậm']].map(([k, label]) => (
          <button key={k} className={`tab ${tab === k ? 'active' : ''}`} onClick={() => setTab(k)}>{label}</button>
        ))}
      </div>

      {msg && <div className="error">{msg}</div>}

      <table className="data">
        <thead><tr>{cols.map(([k, l]) => <th key={k}>{l}</th>)}</tr></thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {cols.map(([k]) => <td key={k}>{k.includes('revenue') ? fmtMoney(r[k]) : r[k]}</td>)}
            </tr>
          ))}
          {rows.length === 0 && <tr><td colSpan={cols.length}>Không có dữ liệu</td></tr>}
        </tbody>
      </table>

      <section className="panel mt">
        <div className="page-head">
          <h3>🤖 AI sinh báo cáo doanh thu</h3>
          <button className="btn primary" onClick={runAi} disabled={aiLoading}>
            {aiLoading ? 'Đang phân tích...' : 'Tạo báo cáo AI'}
          </button>
        </div>
        {aiReport && <pre className="ai-report">{aiReport}</pre>}
      </section>
    </div>
  )
}
