import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import axios from '../api'

// US14: choose a new password from the emailed link
export default function ResetPassword() {
  const [params] = useSearchParams()
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await axios.post('/api/auth/reset-password', {
        token: params.get('token') || '',
        password,
      })
      setMessage(data.message)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not reset the password.')
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US14</span>
        <h2>Choose a new password</h2>
      </div>
      <div className="card auth-card">
        <form onSubmit={handleSubmit} className="form-grid one-col">
          <div className="field full">
            <label htmlFor="password">New password</label>
            <input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 8 characters, letter + number" />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn">Update Password</button>
          </div>
        </form>
        {message && <div className="alert alert-success" role="status">{message} <Link to="/login">Log in</Link></div>}
        {error && <div className="alert alert-error" role="alert">{error}</div>}
      </div>
    </div>
  )
}
