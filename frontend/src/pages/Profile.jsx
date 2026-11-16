import { useState } from 'react'
import { Link } from 'react-router-dom'
import axios, { getStoredUser, updateStoredUser } from '../api'
import Avatar from '../components/Avatar'

const MAX_BYTES = 500 * 1024

// US15: Update Profile & Avatar
export default function Profile({ onAuth }) {
  const stored = getStoredUser()
  const [name, setName] = useState(stored?.name || '')
  const [avatar, setAvatar] = useState(stored?.avatar || null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  if (!stored) {
    return <div className="card">Please <Link to="/login">log in</Link> to edit your profile.</div>
  }

  const pickFile = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) { setError('Please choose an image file.'); return }
    if (file.size > MAX_BYTES) { setError('Image is too large (max 500 KB).'); return }
    setError('')
    const reader = new FileReader()
    reader.onload = () => setAvatar(reader.result)
    reader.readAsDataURL(file)
  }

  const save = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      const { data } = await axios.put('/api/auth/profile', { name, avatar })
      onAuth(updateStoredUser(data.user))
      setMessage('Profile saved.')
    } catch (err) {
      setError(err.response?.data?.error || 'Could not save your profile.')
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US15</span>
        <h2>Your profile</h2>
        <p>Your name and photo appear next to your bills and balances.</p>
      </div>
      <div className="card auth-card">
        <form onSubmit={save} className="form-grid one-col">
          <div className="field full">
            <Avatar name={name} src={avatar} large />
          </div>
          <div className="field full">
            <label htmlFor="avatar">Avatar photo</label>
            <input id="avatar" type="file" accept="image/*" onChange={pickFile} />
            {avatar && <button type="button" className="btn btn-secondary btn-sm" onClick={() => setAvatar(null)}>Remove photo</button>}
          </div>
          <div className="field full">
            <label htmlFor="name">Display name</label>
            <input id="name" value={name} onChange={e => setName(e.target.value)} />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn">Save changes</button>
          </div>
        </form>
        {message && <div className="alert alert-success" role="status">{message}</div>}
        {error && <div className="alert alert-error" role="alert">{error}</div>}
      </div>
    </div>
  )
}
