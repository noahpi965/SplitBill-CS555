import { useState } from 'react'
import axios from 'axios'

// US01: Add a Shared Bill
export default function AddBill() {
  const [form, setForm] = useState({
    title: '', total_amount: '', paid_by: '', group_id: 1, participants: '',
  })
  const [message, setMessage] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    // TODO: wire up real API call in Sprint 1
    setMessage('(stub) Bill submitted successfully!')
  }

  return (
    <div>
      <h2>US01 — Add a Shared Bill</h2>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 400 }}>
        <input placeholder="Bill title"    value={form.title}        onChange={e => setForm({ ...form, title: e.target.value })} />
        <input placeholder="Total amount"  value={form.total_amount} onChange={e => setForm({ ...form, total_amount: e.target.value })} type="number" />
        <input placeholder="Paid by"       value={form.paid_by}      onChange={e => setForm({ ...form, paid_by: e.target.value })} />
        <input placeholder="Participants (comma-separated)" value={form.participants} onChange={e => setForm({ ...form, participants: e.target.value })} />
        <button type="submit">Add Bill</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
    </div>
  )
}
