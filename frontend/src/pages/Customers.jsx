import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api, { errDetail } from '../services/api.js'
import { useAuth } from '../components/AuthContext.jsx'

const empty = { name: '', phone: '', email: '', address: '', customer_group: 'normal' }
const groups = { normal: 'Thường', vip: 'VIP', wholesale: 'Sỉ' }

export default function Customers() {
  const { user } = useAuth()
  const canDelete = ['admin', 'owner'].includes(user?.role)
  const nav = useNavigate()
  const [items, setItems] = useState([])
  const [filters, setFilters] = useState({ keyword: '', customer_group: '' })
  const [editing, setEditing] = useState(null)
  const [msg, setMsg] = useState('')

  const load = useCallback(() => {
    const params = {}
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.customer_group) params.customer_group = filters.customer_group
    api.get('/customers', { params }).then((r) => setItems(r.data)).catch((e) => setMsg(errDetail(e)))
  }, [filters])

  useEffect(() => { load() }, [load])

  const save = async (e) => {
    e.preventDefault()
    try {
      if (editing.id) await api.put(`/customers/${editing.id}`, editing)
      else await api.post('/customers', editing)
      setEditing(null); setMsg(''); load()
    } catch (err) { setMsg(errDetail(err)) }
  }

  const remove = async (c) => {
    if (!confirm(`Xóa khách hàng "${c.name}"?`)) return
    try { await api.delete(`/customers/${c.id}`); load() } catch (err) { setMsg(errDetail(err)) }
  }

  return (
    <div>
      <div className="page-head">
        <h1>Khách hàng</h1>
        <button className="btn primary" onClick={() => setEditing({ ...empty })}>+ Thêm khách hàng</button>
      </div>

      <div className="filters">
        <input placeholder="Tìm tên/SĐT/email..." value={filters.keyword} onChange={(e) => setFilters({ ...filters, keyword: e.target.value })} />
        <select value={filters.customer_group} onChange={(e) => setFilters({ ...filters, customer_group: e.target.value })}>
          <option value="">Mọi nhóm</option>
          <option value="normal">Thường</option>
          <option value="vip">VIP</option>
          <option value="wholesale">Sỉ</option>
        </select>
      </div>

      {msg && <div className="error">{msg}</div>}

      <table className="data">
        <thead>
          <tr><th>Tên</th><th>SĐT</th><th>Email</th><th>Nhóm</th><th></th></tr>
        </thead>
        <tbody>
          {items.map((c) => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.phone}</td>
              <td>{c.email}</td>
              <td><span className={`tag g-${c.customer_group}`}>{groups[c.customer_group]}</span></td>
              <td className="actions">
                <button className="btn sm" onClick={() => nav(`/orders?customer_id=${c.id}`)}>Lịch sử</button>
                <button className="btn sm" onClick={() => setEditing({ ...c })}>Sửa</button>
                {canDelete && <button className="btn sm danger" onClick={() => remove(c)}>Xóa</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {editing && (
        <div className="modal" onClick={() => setEditing(null)}>
          <form className="modal-card" onClick={(e) => e.stopPropagation()} onSubmit={save}>
            <h3>{editing.id ? 'Sửa khách hàng' : 'Thêm khách hàng'}</h3>
            <div className="grid2">
              <label>Tên<input value={editing.name} required onChange={(e) => setEditing({ ...editing, name: e.target.value })} /></label>
              <label>SĐT<input value={editing.phone} onChange={(e) => setEditing({ ...editing, phone: e.target.value })} /></label>
              <label>Email<input value={editing.email} onChange={(e) => setEditing({ ...editing, email: e.target.value })} /></label>
              <label>Nhóm
                <select value={editing.customer_group} onChange={(e) => setEditing({ ...editing, customer_group: e.target.value })}>
                  <option value="normal">Thường</option>
                  <option value="vip">VIP</option>
                  <option value="wholesale">Sỉ</option>
                </select>
              </label>
            </div>
            <label>Địa chỉ<input value={editing.address} onChange={(e) => setEditing({ ...editing, address: e.target.value })} /></label>
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
