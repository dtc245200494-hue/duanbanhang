import { useCallback, useEffect, useState } from 'react'
import api, { fmtMoney, errDetail } from '../services/api.js'

export default function Purchases() {
  const [receipts, setReceipts] = useState([])
  const [products, setProducts] = useState([])
  const [form, setForm] = useState({ product_id: '', quantity: 1, import_price: 0, supplier: '', note: '' })
  const [msg, setMsg] = useState('')

  const load = useCallback(() => {
    api.get('/purchases').then((r) => setReceipts(r.data)).catch((e) => setMsg(errDetail(e)))
  }, [])

  useEffect(() => { load() }, [load])
  useEffect(() => { api.get('/products').then((r) => setProducts(r.data)).catch(() => {}) }, [])

  const pickProduct = (id) => {
    const p = products.find((x) => x.id === +id)
    setForm({ ...form, product_id: id, import_price: p ? p.import_price : 0 })
  }

  const submit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/purchases', {
        product_id: +form.product_id,
        quantity: +form.quantity,
        import_price: +form.import_price,
        supplier: form.supplier,
        note: form.note
      })
      setForm({ product_id: '', quantity: 1, import_price: 0, supplier: '', note: '' })
      setMsg('')
      load()
    } catch (err) { setMsg(errDetail(err)) }
  }

  return (
    <div>
      <div className="page-head"><h1>Nhập hàng</h1></div>
      {msg && <div className="error">{msg}</div>}

      <form className="panel inline-form" onSubmit={submit}>
        <label>Sản phẩm
          <select value={form.product_id} required onChange={(e) => pickProduct(e.target.value)}>
            <option value="">— Chọn —</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.code} · {p.name}</option>)}
          </select>
        </label>
        <label>Số lượng<input type="number" min="1" value={form.quantity} required onChange={(e) => setForm({ ...form, quantity: e.target.value })} /></label>
        <label>Giá nhập<input type="number" min="0" value={form.import_price} required onChange={(e) => setForm({ ...form, import_price: e.target.value })} /></label>
        <label>Nhà cung cấp<input value={form.supplier} placeholder="NCC..." onChange={(e) => setForm({ ...form, supplier: e.target.value })} /></label>
        <button className="btn primary">Nhập hàng</button>
      </form>

      <table className="data">
        <thead>
          <tr><th>Mã PN</th><th>Sản phẩm</th><th>SL</th><th>Giá nhập</th><th>Tổng tiền</th><th>NCC</th><th>Thời gian</th></tr>
        </thead>
        <tbody>
          {receipts.map((r) => (
            <tr key={r.id}>
              <td><code>{r.code}</code></td>
              <td>{r.product_name}</td>
              <td>+{r.quantity}</td>
              <td>{fmtMoney(r.import_price)}</td>
              <td>{fmtMoney(r.total_amount)}</td>
              <td>{r.supplier}</td>
              <td>{r.received_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
