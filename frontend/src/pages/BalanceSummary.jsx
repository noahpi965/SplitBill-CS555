import { useEffect, useState } from 'react'
import axios from '../api'

// US05 / US08 / US03: balances, mark settled, send reminder
export default function BalanceSummary() {
  const [balances, setBalances] = useState([])
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = () => {
    axios.get('/api/balance', { params: { group_id: 1 } })
      .then(({ data }) => {
        setBalances(data.balances)
        setHistory(data.settled_history || [])
      })
      .catch(() => setError('Could not load balances.'))
  }

  useEffect(load, [])

  const markSettled = async (row) => {
    setError('')
    setMessage('')
    try {
      const { data } = await axios.post('/api/settlements', {
        group_id: 1,
        from: row.from,
        to: row.to,
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
        group_id: 1,
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
        <p>Who owes whom across all group bills. Settle a debt or send a reminder.</p>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {message && <div className="alert alert-success">{message}</div>}
      {balances.length === 0
        ? <div className="settled">🎉 All settled up! 🎉</div>
        : (
          <div className="balance-list">
            {balances.map((b, i) => (
              <div key={i} className="balance-row">
                <div className="who">
                  <span className="avatar">{b.from.charAt(0).toUpperCase()}</span>
                  <strong>{b.from}</strong>
                  <span className="arrow">owes →</span>
                  <span className="avatar">{b.to.charAt(0).toUpperCase()}</span>
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
