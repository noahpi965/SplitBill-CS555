import { useEffect, useState } from 'react'
import axios, { getActiveGroupId } from '../api'
import Avatar from '../components/Avatar'

// US05 / US08 / US03 / US27: balances, mark settled, send reminder, simplify debts
export default function BalanceSummary() {
  const [balances, setBalances] = useState([])
  const [history, setHistory] = useState([])
  const [avatars, setAvatars] = useState({})
  const [simplify, setSimplify] = useState(null)
  const [info, setInfo] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = () => {
    const params = { group_id: getActiveGroupId() }
    if (simplify !== null) params.simplify = simplify
    axios.get('/api/balance', { params })
      .then(({ data }) => {
        setBalances(data.balances)
        setHistory(data.settled_history || [])
        setAvatars(data.avatars || {})
        setInfo({ simplified: data.simplified, original: data.original_transfer_count })
      })
      .catch(() => setError('Could not load balances.'))
  }

  useEffect(load, [simplify])

  const markSettled = async (row) => {
    setError('')
    setMessage('')
    try {
      const { data } = await axios.post('/api/settlements', {
        group_id: getActiveGroupId(),
        from: row.from,
        to: row.to,
        simplify: !!info?.simplified,
      })
      setBalances(data.balances)
      setHistory(data.settled_history || [])
      setMessage(`${row.from} → ${row.to} moved to settled history.`)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not mark this debt as settled.')
    }
  }

  const remind = async (row) => {
    setError('')
    setMessage('')
    try {
      const { data } = await axios.post('/api/reminders', {
        group_id: getActiveGroupId(),
        from: row.to,
        to: row.from,
      })
      setMessage(`${data.notification.to} was notified: ${data.notification.details}`)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not send the reminder.')
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US05 · US08 · US03</span>
        <h2>Balance Summary</h2>
        <p>Tracks who owes whom across all group bills. Settle a debt or send a reminder.</p>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {message && <div className="alert alert-success">{message}</div>}
      <label className="toggle-row">
        <input
          type="checkbox"
          checked={!!info?.simplified}
          onChange={e => setSimplify(e.target.checked)}
        />
        Simplify Debts
        {info?.simplified && info.original > balances.length &&
          <span className="muted">— {info.original} payments reduced to {balances.length}</span>}
      </label>
      {balances.length === 0
        ? <div className="settled">🎉 All settled up! 🎉</div>
        : (
          <div className="balance-list">
            {balances.map((b, i) => (
              <div key={i} className="balance-row">
                <div className="who">
                  <Avatar name={b.from} src={avatars[b.from]} />
                  <strong>{b.from}</strong>
                  <span className="arrow">owes →</span>
                  <Avatar name={b.to} src={avatars[b.to]} />
                  <strong>{b.to}</strong>
                </div>
                <div className="row-actions">
                  <span className="amount">${b.amount.toFixed(2)}</span>
                  <button type="button" className="btn btn-sm" onClick={() => markSettled(b)}>Mark as Settled</button>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => remind(b)}>Remind</button>
                </div>
              </div>
            ))}
          </div>
        )
      }
      <div className="card" style={{ marginTop: 24 }}>
        <h3>Settled history</h3>
        {history.length === 0
          ? <div className="empty">No settled debts yet.</div>
          : history.map((row) => (
            <div key={row.id} className="item-row">
              <span>{row.from} paid {row.to}</span>
              <span className="amount">${row.amount.toFixed(2)}</span>
            </div>
          ))
        }
      </div>
    </div>
  )
}
