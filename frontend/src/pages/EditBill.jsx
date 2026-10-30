import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import axios from '../api'

// US07 + US10: Edit an existing bill and optionally remove a participant
export default function EditBill() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(null)
  const [message, setMessage] = useState('')
  const [warning, setWarning] = useState('')
  const [errors, setErrors] = useState({})
  const [pending, setPending] = useState(null)

  useEffect(() => {
    axios.get(`/api/bills/${id}`)
      .then(({ data }) => {
        const bill = data.bill
        setForm({
          title: bill.title,
          total_amount: bill.total_amount,
          paid_by: bill.paid_by,
          group_id: bill.group_id,
          category: bill.category,
          split_type: bill.split_type || 'equal',
          participants: bill.participants.map(p => p.user_name),
          settled: bill.participants.filter(p => p.settled).map(p => p.user_name),
        })
      })
      .catch(() => setErrors({ form: 'Could not load this bill.' }))
  }, [id])

  const save = async (payload, confirmed = false) => {
    setMessage('')
    setWarning('')
    setErrors({})
    try {
      const { data } = await axios.put(`/api/bills/${id}`, { ...payload, confirm: confirmed })
      setMessage('Bill updated. Balances have been recalculated.')
      if (data.warning) setWarning(data.warning)
      setForm({
        ...form,
        ...payload,
        settled: data.bill.participants.filter(p => p.settled).map(p => p.user_name),
      })
      setPending(null)
    } catch (err) {
      const body = err.response?.data || {}
      if (err.response?.status === 409 && body.requires_confirm) {
        setPending({ payload, warning: body.warning })
        return
      }
      setErrors(body.errors || { form: body.error || 'Could not update the bill.' })
    }
  }

  if (!form) {
    return <div className="card">{errors.form || 'Loading…'}</div>
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    save({
      title: form.title,
      total_amount: Number(form.total_amount),
      paid_by: form.paid_by,
      group_id: form.group_id,
      category: form.category,
      split_type: form.split_type,
      participants: form.participants,
    })
  }

  const removeParticipant = (name) => {
    const next = form.participants.filter(p => p !== name)
    save({
      title: form.title,
      total_amount: Number(form.total_amount),
      paid_by: form.paid_by,
      group_id: form.group_id,
      category: form.category,
      split_type: form.split_type,
      participants: next,
    })
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US07 · US10</span>
        <h2>Edit Bill</h2>
        <p>Correct the amount, details, or participants. Balances update immediately.</p>
      </div>
      <div className="card" style={{ maxWidth: 680 }}>
        <form onSubmit={handleSubmit} className="form-grid">
          <div className="field full">
            <label htmlFor="title">Bill title</label>
            <input id="title" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
          </div>
          <div className="field">
            <label htmlFor="total_amount">Total amount ($)</label>
            <input id="total_amount" type="number" step="0.01" value={form.total_amount} onChange={e => setForm({ ...form, total_amount: e.target.value })} />
          </div>
          <div className="field">
            <label htmlFor="paid_by">Paid by</label>
            <input id="paid_by" value={form.paid_by} onChange={e => setForm({ ...form, paid_by: e.target.value })} />
          </div>
          <div className="field full">
            <label>Participants</label>
            <div className="chip-list">
              {form.participants.map(name => (
                <span key={name} className="chip chip-action">
                  {name}{form.settled.includes(name) ? ' · paid' : ''}
                  <button type="button" className="chip-x" onClick={() => removeParticipant(name)} aria-label={`Remove ${name}`}>×</button>
                </span>
              ))}
            </div>
            <p className="muted">Removing someone redistributes the total among the remaining people.</p>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/bills')}>Back</button>
            <button type="submit" className="btn">Save changes</button>
          </div>
        </form>
        {message && <div className="alert alert-success">✅ {message}</div>}
        {warning && <div className="alert alert-warn">⚠️ {warning}</div>}
        {Object.entries(errors).map(([field, msg]) => (
          <div key={field} className="alert alert-error">{msg}</div>
        ))}
      </div>

      {pending && (
        <div className="modal-backdrop" onClick={() => setPending(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>Please confirm</h3>
            <p>{pending.warning}</p>
            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setPending(null)}>Cancel</button>
              <button type="button" className="btn" onClick={() => save(pending.payload, true)}>Confirm anyway</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
