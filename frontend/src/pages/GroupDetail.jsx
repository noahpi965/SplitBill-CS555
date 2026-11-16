import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import axios, { setActiveGroupId } from '../api'
import Avatar from '../components/Avatar'

// US18: members tab with roles
export default function GroupDetail() {
  const { id } = useParams()
  const [group, setGroup] = useState(null)
  const [members, setMembers] = useState([])
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = () => {
    axios.get(`/api/groups/${id}`)
      .then(({ data }) => setGroup(data.group))
      .catch((err) => setError(err.response?.data?.error || 'Could not load this group.'))
    axios.get(`/api/groups/${id}/members`)
      .then(({ data }) => setMembers(data.members))
      .catch(() => {})
  }

  useEffect(load, [id])

  if (!group) return <div>{error ? <div className="alert alert-error">{error}</div> : 'Loading…'}</div>

  return (
    <div>
      <div className="page-header">
        <span className="tag">US18</span>
        <h2>{group.name}</h2>
        <p>{group.group_type} group · {group.member_count} member{group.member_count === 1 ? '' : 's'}</p>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => { setActiveGroupId(group.id); setMessage('This group is now used for bills and balances.') }}>Use for bills</button>
        {' '}<Link to="/groups" className="btn btn-secondary btn-sm">All groups</Link>
      </div>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {message && <div className="alert alert-success" role="status">{message}</div>}

      <div className="card">
        <h3>Members</h3>
        {members.map(m => (
          <div key={m.id} className="item-row">
            <span className="who">
              <Avatar name={m.name} src={m.avatar} /> <strong>{m.name}</strong>{' '}
              <span className={`role-badge${m.role === 'Admin' ? ' admin' : ''}`}>{m.role}</span>
            </span>
          </div>
        ))}
      </div>

    </div>
  )
}
