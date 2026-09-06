import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import api, { fmtMoney, errDetail } from '../services/api.js'

const payLabel = { cash: 'Tiền mặt', card: 'Thẻ', banking: 'CK' }
const today = () => new Date().toISOString().slice(0, 10)

export default function Orders() {
  const [params] = useSearchParams()
  const [items, setItems] = useState([])
  const [products, setProducts] = useState([])
  const [customers, setCustomers] = useState([])
  const [detail, setDetail] = useState(null)
  const [msg, setMsg] = useState('')
  const [creating, setCreating] = useState(false)
  const [form, setForm] = useState({ customer_id: '', discount: 0, payment_method: 'cash', note: '', lines: [] })

  const load = useCallback(() => {
    const p = {}
    if (params.get('customer_id')) p.customer_id = params.get('customer_id')
    api.get('/orders', { params: p }).then((r) => setItems(r.data)).catch((e) => setMsg(errDetail(e)))
  }, [params])

  useEffect(() => { load() }, [load])
  useEffect(() => {
    api.get('/products', { params: { status: 'active' } }).then((r) => setProducts(r.data)).catch(() => {})
    api.get('/customers').then((r) => setCustomers(r.data)).catch(() => {})
  }, [])

  const total = form.lines.reduce((s, l) => {
    const p = products.find((x) => x.id === +l.product_id)
    return s + (p ? p.sell_price * l.quantity : 0)
  }, 0)
  const final = Math.max(total - (+form.discount || 0), 0)

  const addLine = () => setForm({ ...form, lines: [...form.lines, { product_id: '', quantity: 1 }] })
  const setLine = (i, field, val) => {
    const lines = form.lines.map((l, idx) => (idx === i ? { ...l, [field]: val } : l))
    setForm({ ...form, lines })
  }

  const submitOrder = async (e) => {
    e.preventDefault()
    try {
      await api.post('/orders', {
        customer_id: form.customer_id || null,
        items: form.lines.filter((l) => l.product_id).map((l) => ({ product_id: +l.product_id, quantity: +l.quantity })),
        discount: +form.discount || 0,
        payment_method: form.payment_method,
        note: form.note
      })
      setCreating(false)
      setForm({ customer_id: '', discount: 0, payment_method: 'cash', note: '', lines: [] })
      setMsg('')
      load()
    } catch (err) { setMsg(errDetail(err)) }
  }

  const cancelOrder = async (o) => {
    if (!confirm(`Hủy hóa đơn ${o.code}? Tồn kho sẽ được hoàn lại.`)) return
    try { await api.post(`/orders/${o.id}/cancel`); load() } catch (err) { setMsg(errDetail(err)) }
  }

  const openDetail = async (o) => {
    try { const r = await api.get(`/orders/${o.id}`); setDetail(r.data) } catch (err) { setMsg(errDetail(err)) }
  }

  return (
    <div>
      <div className="page-head">
        <h1>Hóa đơn {params.get('customer_id') ? `(khách #${params.get('customer_id')})` : ''}</h1>
        <button className="btn primary" onClick={() => { setCreating(true); setMsg('') }}>+ Lập hóa đơn</button>
      </div>

      {msg && <div className="error">{msg}</div>}

      <table className="data">
        <thead>
          <tr><th>Mã HĐ</th><th>Khách hàng</th><th>Thời gian</th><th>Thành tiền</th><th>Thanh toán</th><th>Trạng thái</th><th></th></tr>
        </thead>
        <tbody>
          {items.map((o) => (
            <tr key={o.id} className={o.status === 'cancelled' ? 'row-cancel' : ''}>
              <td><code>{o.code}</code></td>
              <td>{o.customer_name || 'Khách lẻ'}</td>
              <td>{o.created_at}</td>
              <td><b>{fmtMoney(o.final_amount)}</b></td>
              <td>{payLabel[o.payment_method]}</td>
              <td><span className={`tag ${o.status}`}>{o.status === 'completed' ? 'Hoàn thành' : 'Đã hủy'}</span></td>
              <td className="actions">
                <button className="btn sm" onClick={() => openDetail(o)}>Chi tiết</button>
                {o.status === 'completed' && <button className="btn sm danger" onClick={() => cancelOrder(o)}>Hủy</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {creating && (
        <div className="modal" onClick={() => setCreating(false)}>
          <form className="modal-card wide" onClick={(e) => e.stopPropagation()} onSubmit={submitOrder}>
            <h3>Lập hóa đơn bán hàng</h3>
            <div className="grid2">
              <label>Khách hàng
                <select value={form.customer_id} onChange={(e) => setForm({ ...form, customer_id: e.target.value })}>
                  <option value="">Khách lẻ</option>
                  {customers.map((c) => <option key={c.id} value={c.id}>{c.name} — {c.phone}</option>)}
                </select>
              </label>
              <label>Thanh toán
                <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
                  <option value="cash">Tiền mặt</option>
                  <option value="card">Thẻ</option>
                  <option value="banking">Chuyển khoản</option>
                </select>
              </label>
            </div>

            <h4>Sản phẩm</h4>
            {form.lines.map((l, i) => (
              <div className="line" key={i}>
                <select value={l.product_id} required onChange={(e) => setLine(i, 'product_id', e.target.value)}>
                  <option value="">— Chọn sản phẩm —</option>
                  {products.map((p) => <option key={p.id} value={p.id}>{p.name} (còn {p.stock}) — {fmtMoney(p.sell_price)}</option>)}
                </select>
                <input type="number" min="1" value={l.quantity} onChange={(e) => setLine(i, 'quantity', e.target.value)} />
                <button type="button" className="btn sm danger" onClick={() => setForm({ ...form, lines: form.lines.filter((_, idx) => idx !== i) })}>✕</button>
              </div>
            ))}
            <button type="button" className="btn sm" onClick={addLine}>+ Thêm dòng</button>

            <div className="grid2 mt">
              <label>Giảm giá (₫)<input type="number" min="0" value={form.discount} onChange={(e) => setForm({ ...form, discount: e.target.value })} /></label>
              <div className="totals">
                <div>Tạm tính: <b>{fmtMoney(total)}</b></div>
                <div className="final">Thành tiền: <b>{fmtMoney(final)}</b></div>
              </div>
            </div>

            <div className="modal-actions">
              <button type="button" className="btn ghost" onClick={() => setCreating(false)}>Hủy</button>
              <button className="btn primary">Tạo hóa đơn</button>
            </div>
          </form>
        </div>
      )}

      {detail && (
        <div className="modal" onClick={() => setDetail(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h3>Hóa đơn {detail.code}</h3>
            <p>{detail.customer_name || 'Khách lẻ'} · {detail.created_at} · NV: {detail.created_by}</p>
            <table className="data">
              <thead><tr><th>Sản phẩm</th><th>SL</th><th>Đơn giá</th><th>Thành tiền</th></tr></thead>
              <tbody>
                {detail.items.map((it) => (
                  <tr key={it.id}><td>{it.product_name}</td><td>{it.quantity}</td><td>{fmtMoney(it.unit_price)}</td><td>{fmtMoney(it.subtotal)}</td></tr>
                ))}
              </tbody>
            </table>
            <p className="totals">
              Tổng: {fmtMoney(detail.total_amount)} · Giảm: {fmtMoney(detail.discount)} ·
              <b> Còn lại: {fmtMoney(detail.final_amount)}</b>
            </p>
            <div className="modal-actions"><button className="btn" onClick={() => setDetail(null)}>Đóng</button></div>
          </div>
        </div>
      )}
    </div>
  )
}
