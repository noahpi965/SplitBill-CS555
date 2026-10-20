import { useEffect, useState } from 'react'
import axios from 'axios'

// US05: View Balance Summary
export default function BalanceSummary() {
  const [balances, setBalances] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    axios.get('/api/balance', { params: { group_id: 1 } })
      .then(({ data }) => setBalances(data.balances))
      .catch(() => setError('Could not load balances.'))
  }, [])

  return (
    <div>
      <div className="page-header">
        <span className="tag">US05</span>
        <h2>Balance Summary</h2>
        <p>Who owes whom across all group bills.</p>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
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
                <span className="amount">${b.amount.toFixed(2)}</span>
              </div>
            ))}
          </div>
        )
      }
    </div>
  )
}
