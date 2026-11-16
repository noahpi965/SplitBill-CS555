import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { QRCodeSVG } from 'qrcode.react'
import axios, { setActiveGroupId } from '../api'
import Avatar from '../components/Avatar'

// US18: members tab with roles · US19: remove member · US17: invite link / QR · US27: simplify toggle
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

  const isAdmin = group?.role === 'Admin'
  const inviteLink = group ? `${window.location.origin}/join/${group.invite_code}` : ''

  const remove = async (m) => {
    setError('')
    setMessage('')
    try {
      await axios.delete(`/api/groups/${id}/members/${m.id}`)
      setMessage(`${m.name} was removed from the group.`)
      load()
    } catch (err) {
      setError(err.response?.data?.error || 'Could not remove this member.')
    }
  }

  const toggleSimplify = async (checked) => {
    setError('')
    try {
      const { data } = await axios.put(`/api/groups/${id}`, { simplify_debts: checked })
      setGroup({ ...group, ...data.group })
    } catch (err) {
      setError(err.response?.data?.error || 'Could not update the setting.')
    }
  }

  if (!group) return <div>{error ? <div className="alert alert-error">{error}</div> : 'Loading…'}</div>

  return (
    <div>
      <div className="page-header">
        <span className="tag">US17 · US18 · US19</span>
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
            {isAdmin && (
              <button type="button" className="btn btn-danger btn-sm" onClick={() => remove(m)}>Remove Member</button>
            )}
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: 24 }}>
        <h3>Invite friends</h3>
        <div className="invite-box">
          <QRCodeSVG value={inviteLink} size={128} />
          <div style={{ flex: 1 }}>
            <input readOnly value={inviteLink} onFocus={e => e.target.select()} aria-label="Invite link" />
            <p className="muted">Share this link or let a friend scan the QR code. Invite code: <code>{group.invite_code}</code></p>
          </div>
        </div>
      </div>

      {isAdmin && (
        <div className="card" style={{ marginTop: 24 }}>
          <h3>Settings</h3>
          <label className="toggle-row">
            <input type="checkbox" checked={group.simplify_debts} onChange={e => toggleSimplify(e.target.checked)} />
            Simplify Debts (minimise the number of payments)
          </label>
        </div>
      )}
    </div>
  )
}
