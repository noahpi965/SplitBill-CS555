import { useState } from 'react'
import axios from 'axios'

const EMPTY_FORM = {
  title: '', total_amount: '', paid_by: '', group_id: 1, participants: '', category: 'General', date: '',
}

// US01: Add a Shared Bill
export default function AddBill() {
  const [form, setForm] = useState(EMPTY_FORM)
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState({})

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage('')
    setErrors({})
    const payload = {
      ...form,
      participants: form.participants.split(',').map(p => p.trim()).filter(Boolean),
      date: form.date || undefined,
    }
    try {
      const { data } = await axios.post('/api/bills', payload)
      setMessage(`Bill "${data.bill.title}" saved!`)
      setForm(EMPTY_FORM)
    } catch (err) {
      setErrors(err.response?.data?.errors || { form: 'Could not save the bill.' })
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US01</span>
        <h2>Add a Shared Bill</h2>
        <p>Record an expense and split it evenly among participants.</p>
      </div>
      <div className="card" style={{ maxWidth: 680 }}>
        <form onSubmit={handleSubmit} className="form-grid">
          <div className="field full">
            <label htmlFor="title">Bill title</label>
            <input id="title" placeholder="e.g. Dinner at Joe's" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
          </div>
          <div className="field">
            <label htmlFor="total_amount">Total amount ($)</label>
            <input id="total_amount" placeholder="0.00" value={form.total_amount} onChange={e => setForm({ ...form, total_amount: e.target.value })} type="number" step="0.01" />
          </div>
          <div className="field">
            <label htmlFor="paid_by">Paid by</label>
            <input id="paid_by" placeholder="e.g. Alice" value={form.paid_by} onChange={e => setForm({ ...form, paid_by: e.target.value })} />
          </div>
          <div className="field full">
            <label htmlFor="participants">Participants</label>
            <input id="participants" placeholder="Comma-separated, e.g. Alice, Bob, Carol" value={form.participants} onChange={e => setForm({ ...form, participants: e.target.value })} />
          </div>
          <div className="field">
            <label htmlFor="category">Category</label>
            <input id="category" placeholder="General" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} />
          </div>
          <div className="field">
            <label htmlFor="date">Date</label>
            <input id="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} type="date" />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn">Add Bill</button>
          </div>
        </form>
        {message && <div className="alert alert-success">✅ {message}</div>}
        {Object.entries(errors).map(([field, msg]) => (
          <div key={field} className="alert alert-error">{msg}</div>
        ))}
      </div>
    </div>
  )
}
