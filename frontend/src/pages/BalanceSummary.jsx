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
      <h2>US05 — Balance Summary</h2>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      {balances.length === 0
        ? <p style={{ color: 'green', fontWeight: 'bold' }}>● All settled up! 🎉</p>
        : balances.map((b, i) => (
            <div key={i}>{b.from} owes {b.to}: ${b.amount.toFixed(2)}</div>
          ))
      }
    </div>
  )
}
