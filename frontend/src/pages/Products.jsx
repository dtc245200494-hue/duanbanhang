import { useCallback, useEffect, useState } from 'react'
import api, { fmtMoney, errDetail } from '../services/api.js'
import { useAuth } from '../components/AuthContext.jsx'

const empty = { code: '', name: '', category_id: '', import_price: 0, sell_price: 0, stock: 0, status: 'active', description: '' }

export default function Products() {
  const { user } = useAuth()
  const canManage = ['admin', 'owner'].includes(user?.role)
  const [items, setItems] = useState([])
  const [cats, setCats] = useState([])
  const [filters, setFilters] = useState({ keyword: '', category_id: '', status: '', low_stock: false })
  const [editing, setEditing] = useState(null)
  const [msg, setMsg] = useState('')

  const load = useCallback(() => {
    const params = {}
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.status) params.status = filters.status
    if (filters.low_stock) params.low_stock = true
    api.get('/products', { params }).then((r) => setItems(r.data)).catch((e) => setMsg(errDetail(e)))
  }, [filters])

  useEffect(() => { load() }, [load])
  useEffect(() => { api.get('/categories').then((r) => setCats(r.data)).catch(() => {}) }, [])

  const save = async (e) => {
    e.preventDefault()
    const body = { ...editing, category_id: editing.category_id || null }
    try {
      if (editing.id) await api.put(`/products/${editing.id}`, body)
      else await api.post('/products', body)
      setEditing(null)
      setMsg('')
      load()
    } catch (err) { setMsg(errDetail(err)) }
  }

  const remove = async (p) => {
    if (!confirm(`Xóa sản phẩm "${p.name}"?`)) return
    try { await api.delete(`/products/${p.id}`); load() } catch (err) { setMsg(errDetail(err)) }
  }

  return (
    <div>
      <div className="page-head">
        <h1>Sản phẩm</h1>
        {canManage && <button className="btn primary" onClick={() => setEditing({ ...empty })}>+ Thêm sản phẩm</button>}
      </div>

      <div className="filters">
        <input placeholder="Tìm mã/tên..." value={filters.keyword} onChange={(e) => setFilters({ ...filters, keyword: e.target.value })} />
        <select value={filters.category_id} onChange={(e) => setFilters({ ...filters, category_id: e.target.value })}>
          <option value="">Tất cả nhóm hàng</option>
          {cats.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">Mọi trạng thái</option>
          <option value="active">Đang bán</option>
          <option value="inactive">Ngừng KD</option>
        </select>
        <label className="check"><input type="checkbox" checked={filters.low_stock} onChange={(e) => setFilters({ ...filters, low_stock: e.target.checked })} /> Sắp hết</label>
      </div>

      {msg && <div className="error">{msg}</div>}

      <table className="data">
        <thead>
          <tr><th>Mã</th><th>Tên</th><th>Nhóm</th><th>Giá bán</th><th>Tồn</th><th>Trạng thái</th>{canManage && <th></th>}</tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.id}>
              <td><code>{p.code}</code></td>
              <td>{p.name}</td>
              <td>{p.category_name || '—'}</td>
              <td>{fmtMoney(p.sell_price)}</td>
              <td className={p.stock === 0 ? 'danger' : p.stock <= 5 ? 'warn' : ''}>{p.stock}</td>
              <td><span className={`tag ${p.status}`}>{p.status === 'active' ? 'Đang bán' : 'Ngừng KD'}</span></td>
              {canManage && (
                <td className="actions">
                  <button className="btn sm" onClick={() => setEditing({ ...p })}>Sửa</button>
                  <button className="btn sm danger" onClick={() => remove(p)}>Xóa</button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {editing && (
        <div className="modal" onClick={() => setEditing(null)}>
          <form className="modal-card" onClick={(e) => e.stopPropagation()} onSubmit={save}>
            <h3>{editing.id ? 'Sửa sản phẩm' : 'Thêm sản phẩm'}</h3>
            <div className="grid2">
              <label>Mã<input value={editing.code} disabled={!!editing.id} required onChange={(e) => setEditing({ ...editing, code: e.target.value })} /></label>
              <label>Tên<input value={editing.name} required onChange={(e) => setEditing({ ...editing, name: e.target.value })} /></label>
              <label>Nhóm hàng
                <select value={editing.category_id || ''} onChange={(e) => setEditing({ ...editing, category_id: e.target.value })}>
                  <option value="">—</option>
                  {cats.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </label>
              <label>Trạng thái
                <select value={editing.status} onChange={(e) => setEditing({ ...editing, status: e.target.value })}>
                  <option value="active">Đang bán</option>
                  <option value="inactive">Ngừng KD</option>
                </select>
              </label>
              <label>Giá nhập<input type="number" value={editing.import_price} onChange={(e) => setEditing({ ...editing, import_price: +e.target.value })} /></label>
              <label>Giá bán<input type="number" value={editing.sell_price} onChange={(e) => setEditing({ ...editing, sell_price: +e.target.value })} /></label>
              <label>Tồn kho<input type="number" value={editing.stock} onChange={(e) => setEditing({ ...editing, stock: +e.target.value })} /></label>
            </div>
            <label>Mô tả<textarea rows="2" value={editing.description} onChange={(e) => setEditing({ ...editing, description: e.target.value })} /></label>
            <div className="modal-actions">
              <button type="button" className="btn ghost" onClick={() => setEditing(null)}>Hủy</button>
              <button className="btn primary">Lưu</button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
