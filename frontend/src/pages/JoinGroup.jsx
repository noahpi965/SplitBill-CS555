import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import axios, { getStoredUser, setActiveGroupId } from '../api'

// US17: Join Group via Invite Link or QR Code
export default function JoinGroup() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [group, setGroup] = useState(null)
  const [error, setError] = useState('')
  const user = getStoredUser()

  useEffect(() => {
    axios.get(`/api/invites/${code}`)
      .then(({ data }) => setGroup(data.group))
      .catch((err) => setError(err.response?.data?.error || 'This invite link is invalid.'))
  }, [code])

  const join = async () => {
    setError('')
    try {
      const { data } = await axios.post(`/api/invites/${code}/join`)
      setActiveGroupId(data.group.id)
      navigate(`/groups/${data.group.id}`)
    } catch (err) {
      setError(err.response?.data?.error || 'Could not join the group.')
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US17</span>
        <h2>Join a group</h2>
      </div>
      <div className="card auth-card">
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        {group && (
          <>
            <p>You've been invited to <strong>{group.name}</strong> ({group.group_type}, {group.member_count} member{group.member_count === 1 ? '' : 's'}).</p>
            {user
              ? <button type="button" className="btn" onClick={join}>Join Group</button>
              : <p>Please <Link to="/login">log in</Link> or <Link to="/register">register</Link>, then open this link again.</p>}
          </>
        )}
      </div>
    </div>
  )
}
