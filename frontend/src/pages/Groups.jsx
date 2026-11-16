import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios, { getActiveGroupId, getStoredUser, setActiveGroupId } from '../api'

const GROUP_TYPES = ['Home', 'Trip', 'Couple', 'Event', 'Other']

// US16: Create Expense Group (+ list of my groups)
export default function Groups() {
  const navigate = useNavigate()
  const user = getStoredUser()
  const [groups, setGroups] = useState([])
  const [form, setForm] = useState({ name: '', group_type: 'Home' })
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = () => {
    axios.get('/api/groups')
      .then(({ data }) => setGroups(data.groups))
      .catch(() => setError('Could not load your groups.'))
  }

  useEffect(() => { if (user) load() }, [])

  if (!user) {
    return <div className="card">Please <Link to="/login">log in</Link> to manage groups.</div>
  }

  const create = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      const { data } = await axios.post('/api/groups', form)
      setActiveGroupId(data.group.id)
      setMessage(`Created "${data.group.name}". Invite members from the group page.`)
      setForm({ name: '', group_type: form.group_type })
      load()
      navigate(`/groups/${data.group.id}`)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not create the group.')
    }
  }

  const activeId = getActiveGroupId()

  return (
    <div>
      <div className="page-header">
        <span className="tag">US16</span>
        <h2>Groups</h2>
        <p>Create a group for the people you share expenses with.</p>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {message && <div className="alert alert-success" role="status">{message}</div>}

      <div className="card">
        <h3>Create group</h3>
        <form onSubmit={create} className="inline-form">
          <div className="field">
            <label htmlFor="gname">Group name</label>
            <input id="gname" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Apartment 3B" />
          </div>
          <div className="field">
            <label htmlFor="gtype">Type</label>
            <select id="gtype" value={form.group_type} onChange={e => setForm({ ...form, group_type: e.target.value })}>
              {GROUP_TYPES.map(t => <option key={t}>{t}</option>)}
            </select>
          </div>
          <button type="submit" className="btn">Create Group</button>
        </form>
      </div>

      <div className="card" style={{ marginTop: 24 }}>
        <h3>My groups</h3>
        {groups.length === 0
          ? <div className="empty">You are not in any groups yet.</div>
          : groups.map(g => (
            <div key={g.id} className="item-row">
              <span>
                <strong>{g.name}</strong> · {g.group_type} · {g.member_count} member{g.member_count === 1 ? '' : 's'}
                {g.id === activeId && <span className="chip">active</span>}
              </span>
              <span className="row-actions">
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => { setActiveGroupId(g.id); load() }}>Use for bills</button>
                <Link to={`/groups/${g.id}`} className="btn btn-sm">Open</Link>
              </span>
            </div>
          ))
        }
      </div>
    </div>
  )
}
