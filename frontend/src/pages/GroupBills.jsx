import { useEffect, useState } from 'react'
import axios from 'axios'

// US04: View Group Bills
export default function GroupBills() {
  const [bills, setBills] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    axios.get('/api/bills', { params: { group_id: 1 } })
      .then(({ data }) => setBills(data.bills))
      .catch(() => setError('Could not load bills.'))
  }, [])

  return (
    <div>
      <h2>US04 — Group Bills</h2>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      {bills.length === 0
        ? <p style={{ color: '#888' }}>No bills yet. Add one!</p>
        : (
          <table cellPadding={6}>
            <thead>
              <tr><th>Date</th><th>Title</th><th>Amount</th><th>Paid by</th><th>Participants</th></tr>
            </thead>
            <tbody>
              {bills.map(b => (
                <tr key={b.id}>
                  <td>{b.created_at.slice(0, 10)}</td>
                  <td>{b.title}</td>
                  <td>${b.total_amount.toFixed(2)}</td>
                  <td>{b.paid_by}</td>
                  <td>{b.participants.map(p => `${p.user_name} ($${p.share.toFixed(2)})`).join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      }
    </div>
  )
}
