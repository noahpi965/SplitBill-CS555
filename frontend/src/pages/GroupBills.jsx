import { useEffect, useState } from 'react'

// US04: View Group Bills
export default function GroupBills() {
  const [bills, setBills] = useState([])

  useEffect(() => {
    // TODO: fetch from GET /api/bills?group_id=1 in Sprint 1
    setBills([]) // stub
  }, [])

  return (
    <div>
      <h2>US04 — Group Bills</h2>
      {bills.length === 0
        ? <p style={{ color: '#888' }}>No bills yet. Add one!</p>
        : bills.map(b => <div key={b.id}>{b.title} — ${b.total_amount}</div>)
      }
    </div>
  )
}
