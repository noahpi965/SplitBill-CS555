import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import axios from '../api'

// US04 / US09: View Group Bills + delete with confirmation
export default function GroupBills() {
  const [bills, setBills] = useState([])
  const [error, setError] = useState('')
  const [pendingDelete, setPendingDelete] = useState(null)
  const [message, setMessage] = useState('')

  const load = () => {
    axios.get('/api/bills', { params: { group_id: 1 } })
      .then(({ data }) => setBills(data.bills))
      .catch(() => setError('Could not load bills.'))
  }

  useEffect(load, [])

  const confirmDelete = async () => {
    if (!pendingDelete) return
    try {
      await axios.delete(`/api/bills/${pendingDelete.id}`)
      setMessage(`Deleted "${pendingDelete.title}".`)
      setPendingDelete(null)
      load()
    } catch {
      setError('Could not delete the bill.')
      setPendingDelete(null)
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US04 · US09</span>
        <h2>Group Bills</h2>
        <p>All shared expenses recorded for your group.</p>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {message && <div className="alert alert-success">{message}</div>}
      <div className="card">
        {bills.length === 0
          ? <div className="empty"><span className="emoji">🧾</span>No bills yet. Add one!</div>
          : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>Date</th><th>Title</th><th>Amount</th><th>Paid by</th><th>Participants</th><th>Actions</th></tr>
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
                          <span key={p.user_name} className="chip">
                            {p.user_name} · ${p.share.toFixed(2)}
                            {p.settled ? ' · settled' : ''}
                          </span>
                        ))}
                      </td>
                      <td>
                        <div className="row-actions">
                          <Link to={`/bills/${b.id}/edit`} className="btn btn-secondary btn-sm">Edit</Link>
                          <button type="button" className="btn btn-danger btn-sm" onClick={() => setPendingDelete(b)}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        }
      </div>

      {pendingDelete && (
        <div className="modal-backdrop" onClick={() => setPendingDelete(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>Delete this bill?</h3>
            <p>This permanently removes <strong>{pendingDelete.title}</strong> and recalculates balances.</p>
            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setPendingDelete(null)}>Cancel</button>
              <button type="button" className="btn btn-danger" onClick={confirmDelete}>Confirm delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
