import { useState } from 'react'
import { Link } from 'react-router-dom'
import axios from '../api'

// US14: Password Reset via Email
export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      const { data } = await axios.post('/api/auth/forgot-password', { email })
      setMessage(data.message)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not send the reset link.')
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US14</span>
        <h2>Forgot password</h2>
        <p>Enter your registered email and we'll send you a reset link.</p>
      </div>
      <div className="card auth-card">
        <form onSubmit={handleSubmit} className="form-grid one-col">
          <div className="field full">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn">Send Reset Link</button>
          </div>
        </form>
        {message && <div className="alert alert-success" role="status">{message}</div>}
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <p className="muted"><Link to="/login">Back to log in</Link></p>
      </div>
    </div>
  )
}
