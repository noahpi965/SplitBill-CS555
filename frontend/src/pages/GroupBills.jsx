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
      <div className="page-header">
        <span className="tag">US04</span>
        <h2>Group Bills</h2>
        <p>All shared expenses recorded for your group.</p>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="card">
        {bills.length === 0
          ? <div className="empty"><span className="emoji">🧾</span>No bills yet. Add one!</div>
          : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>Date</th><th>Title</th><th>Amount</th><th>Paid by</th><th>Participants</th></tr>
                </thead>
                <tbody>
                  {bills.map(b => (
                    <tr key={b.id}>
                      <td>{b.created_at.slice(0, 10)}</td>
                      <td><strong>{b.title}</strong></td>
                      <td className="amount">${b.total_amount.toFixed(2)}</td>
                      <td>{b.paid_by}</td>
                      <td>
                        {b.participants.map(p => (
                          <span key={p.user_name} className="chip">{p.user_name} · ${p.share.toFixed(2)}</span>
                        ))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        }
      </div>
    </div>
  )
}
