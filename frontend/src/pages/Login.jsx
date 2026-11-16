import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios, { storeSession } from '../api'

// US12: User Login
export default function Login({ onAuth }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await axios.post('/api/auth/login', form)
      const session = storeSession(data)
      onAuth(session)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid email or password')
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US12</span>
        <h2>Log in</h2>
        <p>Sign in to access your expense groups and dashboard.</p>
      </div>
      <div className="card auth-card">
        <form onSubmit={handleSubmit} className="form-grid one-col">
          <div className="field full">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" />
          </div>
          <div className="field full">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn">Log In</button>
          </div>
        </form>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <p className="muted">Need an account? <Link to="/register">Register</Link></p>
      </div>
    </div>
  )
}
