import { useRef, useState } from 'react'
import api, { errDetail } from '../services/api.js'

export default function AIChat() {
  const [mode, setMode] = useState('consult')
  const [request, setRequest] = useState('')
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')
  const boxRef = useRef(null)

  const push = (role, text) => {
    setMessages((m) => [...m, { role, text }])
    setTimeout(() => boxRef.current?.scrollTo(0, boxRef.current.scrollHeight), 50)
  }

  const send = async (e) => {
    e.preventDefault()
    const input = mode === 'consult' ? request : question
    if (!input.trim() || loading) return
    setMsg('')
    push('user', input)
    setLoading(true)
    try {
      const url = mode === 'consult' ? '/ai/consult' : '/ai/qa'
      const body = mode === 'consult' ? { customer_request: input } : { question: input }
      const r = await api.post(url, body)
      push('ai', r.data.answer)
    } catch (err) {
      push('ai', `⚠️ ${errDetail(err)}`)
    } finally {
      setLoading(false)
      mode === 'consult' ? setRequest('') : setQuestion('')
    }
  }

  const placeholder =
    mode === 'consult'
      ? 'VD: Khách cần tai nghe dưới 500k, pin lâu, còn hàng...'
      : 'VD: Tháng này mặt hàng nào bán chậm nhất?'

  return (
    <div className="ai-page">
      <div className="page-head"><h1>🤖 Trợ lý AI</h1></div>

      <div className="tabs">
        <button className={`tab ${mode === 'consult' ? 'active' : ''}`} onClick={() => setMode('consult')}>
          💬 Tư vấn sản phẩm
        </button>
        <button className={`tab ${mode === 'qa' ? 'active' : ''}`} onClick={() => setMode('qa')}>
          ❓ Hỏi đáp dữ liệu
        </button>
      </div>

      {msg && <div className="error">{msg}</div>}

      <div className="chat-box" ref={boxRef}>
        {messages.length === 0 && (
          <div className="chat-empty">
            {mode === 'consult'
              ? 'Nhập nhu cầu của khách hàng, AI sẽ gợi ý sản phẩm còn hàng phù hợp nhất.'
              : 'Đặt câu hỏi về dữ liệu bán hàng (doanh thu, bán chạy, bán chậm, tồn kho...).'}
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            <div className="who">{m.role === 'user' ? '🧑 Bạn' : '🤖 AI'}</div>
            <pre>{m.text}</pre>
          </div>
        ))}
        {loading && <div className="bubble ai"><div className="who">🤖 AI</div><pre>Đang xử lý...</pre></div>}
      </div>

      <form className="chat-input" onSubmit={send}>
        <textarea
          rows="2"
          value={mode === 'consult' ? request : question}
          placeholder={placeholder}
          onChange={(e) => (mode === 'consult' ? setRequest(e.target.value) : setQuestion(e.target.value))}
          onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) send(e) }}
        />
        <button className="btn primary" disabled={loading}>Gửi</button>
      </form>
    </div>
  )
}
