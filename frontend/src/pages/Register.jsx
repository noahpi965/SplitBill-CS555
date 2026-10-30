import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios, { storeSession } from '../api'

// US11: User Account Registration
export default function Register({ onAuth }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await axios.post('/api/auth/register', form)
      const session = storeSession(data)
      onAuth(session)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.error || 'Could not create the account.')
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US11</span>
        <h2>Create an account</h2>
        <p>Register with email and a strong password to manage shared expenses.</p>
      </div>
      <div className="card auth-card">
        <form onSubmit={handleSubmit} className="form-grid one-col">
          <div className="field full">
            <label htmlFor="name">Name</label>
            <input id="name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Alice" />
          </div>
          <div className="field full">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" />
          </div>
          <div className="field full">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} placeholder="At least 8 characters, letter + number" />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn">Register</button>
          </div>
        </form>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <p className="muted">Already have an account? <Link to="/login">Log in</Link></p>
      </div>
    </div>
  )
}
