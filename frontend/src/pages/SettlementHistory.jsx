import { useEffect, useState } from 'react'
import axios, { getActiveGroupId } from '../api'
import Avatar from '../components/Avatar'

// US31: View Settlement Transaction History
export default function SettlementHistory() {
  const [rows, setRows] = useState([])
  const [avatars, setAvatars] = useState({})
  const [total, setTotal] = useState(0)
  const [order, setOrder] = useState('asc')
  const [error, setError] = useState('')

  useEffect(() => {
    axios.get('/api/settlements', { params: { group_id: getActiveGroupId(), order } })
      .then(({ data }) => {
        setRows(data.settlements)
        setAvatars(data.avatars || {})
        setTotal(data.total_amount)
      })
      .catch(() => setError('Could not load settlement history.'))
  }, [order])

  return (
    <div>
      <div className="page-header">
        <span className="tag">US31</span>
        <h2>Settlement History</h2>
        <p>Every completed payment in your group, with timestamps.</p>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="card">
        <div className="toggle-row">
          <label htmlFor="order">Order</label>
          <select id="order" value={order} onChange={e => setOrder(e.target.value)}>
            <option value="asc">Oldest first</option>
            <option value="desc">Newest first</option>
          </select>
          <span className="muted" style={{ marginLeft: 'auto' }}>Total settled: ${total.toFixed(2)}</span>
        </div>
        {rows.length === 0
          ? <div className="empty"><span className="emoji">🧾</span>No payments have been settled yet.</div>
          : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Date &amp; time</th><th>Payer</th><th>Received by</th><th>Amount</th></tr></thead>
                <tbody>
                  {rows.map(r => (
                    <tr key={r.id}>
                      <td>{new Date(r.settled_at + 'Z').toLocaleString()}</td>
                      <td><Avatar name={r.from} src={avatars[r.from]} /> {r.from}</td>
                      <td><Avatar name={r.to} src={avatars[r.to]} /> {r.to}</td>
                      <td className="amount">${r.amount.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </div>
    </div>
  )
}
