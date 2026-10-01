import { useEffect, useState } from 'react'

// US05: View Balance Summary
export default function BalanceSummary() {
  const [balances, setBalances] = useState([])

  useEffect(() => {
    // TODO: fetch from GET /api/balance?group_id=1 in Sprint 1
    setBalances([]) // stub
  }, [])

  return (
    <div>
      <h2>US05 — Balance Summary</h2>
      {balances.length === 0
        ? <p style={{ color: '#888' }}>All settled up! 🎉</p>
        : balances.map((b, i) => (
            <div key={i}>{b.from} owes {b.to}: ${b.amount}</div>
          ))
      }
    </div>
  )
}
