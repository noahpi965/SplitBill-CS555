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
      <h2>US01 — Add a Shared Bill</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 400 }}>
        <input placeholder="Bill title"    value={form.title}        onChange={e => setForm({ ...form, title: e.target.value })} />
        <input placeholder="Total amount"  value={form.total_amount} onChange={e => setForm({ ...form, total_amount: e.target.value })} type="number" step="0.01" />
        <input placeholder="Paid by"       value={form.paid_by}      onChange={e => setForm({ ...form, paid_by: e.target.value })} />
        <input placeholder="Participants (comma-separated)" value={form.participants} onChange={e => setForm({ ...form, participants: e.target.value })} />
        <input placeholder="Category"      value={form.category}     onChange={e => setForm({ ...form, category: e.target.value })} />
        <input value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} type="date" />
        <button type="submit">Add Bill</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {Object.entries(errors).map(([field, msg]) => (
        <p key={field} style={{ color: 'crimson' }}>{msg}</p>
      ))}
    </div>
  )
}
