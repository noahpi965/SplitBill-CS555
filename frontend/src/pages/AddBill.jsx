import { useMemo, useState } from 'react'
import axios from '../api'

const EMPTY_FORM = {
  title: '', total_amount: '', paid_by: '', group_id: 1, participants: '', category: 'General', date: '',
}

function parseNames(value) {
  return value.split(',').map(p => p.trim()).filter(Boolean)
}

function equalPercents(names) {
  if (!names.length) return {}
  const base = Math.floor((10000 / names.length)) / 100
  const ratios = {}
  let used = 0
  names.forEach((name, i) => {
    const value = i === names.length - 1 ? round2(100 - used) : base
    ratios[name] = value
    used = round2(used + value)
  })
  return ratios
}

function round2(n) {
  return Math.round(n * 100) / 100
}

function previewShares(amount, names, splitType, ratios) {
  const total = Number(amount)
  if (!total || total <= 0 || names.length === 0) return []
  if (splitType === 'equal') {
    const cents = Math.round(total * 100)
    const base = Math.floor(cents / names.length)
    const rem = cents % names.length
    return names.map((name, i) => ({
      user_name: name,
      percent: round2(100 / names.length),
      share: (base + (i < rem ? 1 : 0)) / 100,
    }))
  }
  const percents = names.map(name => Number(ratios[name] || 0))
  const totalCents = Math.round(total * 100)
  let allocated = 0
  return names.map((name, i) => {
    const shareCents = i === names.length - 1
      ? totalCents - allocated
      : Math.round(totalCents * percents[i] / 100)
    if (i < names.length - 1) allocated += shareCents
    return { user_name: name, percent: round2(percents[i]), share: shareCents / 100 }
  })
}

// US01 + US02: Add a Shared Bill (equal or custom ratio)
export default function AddBill() {
  const [form, setForm] = useState(EMPTY_FORM)
  const [splitType, setSplitType] = useState('equal')
  const [ratios, setRatios] = useState({})
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState({})

  const names = parseNames(form.participants)
  const ratioSum = round2(names.reduce((sum, name) => sum + Number(ratios[name] || 0), 0))
  const ratioOk = splitType === 'equal' || Math.abs(ratioSum - 100) < 0.01
  const preview = useMemo(
    () => previewShares(form.total_amount, names, splitType, ratios),
    [form.total_amount, form.participants, splitType, ratios],
  )

  const setParticipants = (value) => {
    const nextNames = parseNames(value)
    setForm({ ...form, participants: value })
    setRatios((current) => {
      const next = {}
      nextNames.forEach((name) => { next[name] = current[name] })
      if (nextNames.some((name) => current[name] == null)) {
        return { ...equalPercents(nextNames), ...Object.fromEntries(
          nextNames.filter((n) => current[n] != null).map((n) => [n, current[n]]),
        )}
      }
      return next
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setMessage('')
    setErrors({})
    if (!ratioOk) {
      setErrors({ ratios: 'Ratios must sum to 100%.' })
      return
    }
    const payload = {
      ...form,
      participants: names,
      split_type: splitType,
      date: form.date || undefined,
    }
    if (splitType === 'custom') payload.ratios = Object.fromEntries(names.map((n) => [n, Number(ratios[n])]))
    try {
      const { data } = await axios.post('/api/bills', payload)
      setMessage(`Bill "${data.bill.title}" saved!`)
      setForm(EMPTY_FORM)
      setSplitType('equal')
      setRatios({})
    } catch (err) {
      setErrors(err.response?.data?.errors || { form: 'Could not save the bill.' })
    }
  }

  return (
    <div>
      <div className="page-header">
        <span className="tag">US01 · US02</span>
        <h2>Add a Shared Bill</h2>
        <p>Record an expense and split it evenly or by a custom ratio.</p>
      </div>
      <div className="card" style={{ maxWidth: 680 }}>
        <form onSubmit={handleSubmit} className="form-grid">
          <div className="field full">
            <label htmlFor="title">Bill title</label>
            <input id="title" placeholder="e.g. Dinner at Joe's" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
          </div>
          <div className="field">
            <label htmlFor="total_amount">Total amount ($)</label>
            <input id="total_amount" placeholder="0.00" value={form.total_amount} onChange={e => setForm({ ...form, total_amount: e.target.value })} type="number" step="0.01" />
          </div>
          <div className="field">
            <label htmlFor="paid_by">Paid by</label>
            <input id="paid_by" placeholder="e.g. Alice" value={form.paid_by} onChange={e => setForm({ ...form, paid_by: e.target.value })} />
          </div>
          <div className="field full">
            <label htmlFor="participants">Participants</label>
            <input id="participants" placeholder="Comma-separated, e.g. Alice, Bob, Carol" value={form.participants} onChange={e => setParticipants(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="category">Category</label>
            <input id="category" placeholder="General" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} />
          </div>
          <div className="field">
            <label htmlFor="date">Date</label>
            <input id="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} type="date" />
          </div>
          <div className="field full">
            <label>Split rule</label>
            <div className="choice-row">
              <label className={`choice ${splitType === 'equal' ? 'active' : ''}`}>
                <input type="radio" name="split" checked={splitType === 'equal'} onChange={() => setSplitType('equal')} />
                Equal split
              </label>
              <label className={`choice ${splitType === 'custom' ? 'active' : ''}`}>
                <input type="radio" name="split" checked={splitType === 'custom'} onChange={() => {
                  setSplitType('custom')
                  setRatios((current) => Object.keys(current).length ? current : equalPercents(names))
                }} />
                Custom ratio
              </label>
            </div>
          </div>
          {splitType === 'custom' && names.length > 0 && (
            <div className="field full">
              <label>Share % (must sum to 100 — a 3:7 split is 30 and 70)</label>
              <div className="ratio-grid">
                {names.map((name) => (
                  <label key={name} className="ratio-item">
                    <span>{name}</span>
                    <input
                      type="number"
                      step="0.01"
                      value={ratios[name] ?? ''}
                      onChange={e => setRatios({ ...ratios, [name]: e.target.value })}
                    />
                    <span className="muted">%</span>
                  </label>
                ))}
              </div>
              <div className={`ratio-sum ${ratioOk ? 'ok' : 'bad'}`}>Total: {ratioSum.toFixed(2)}%</div>
            </div>
          )}
          {preview.length > 0 && (
            <div className="field full">
              <div className="preview">
                <strong>Split preview</strong>
                <p className="muted">Review each share before confirming.</p>
                {preview.map((row) => (
                  <div key={row.user_name} className="preview-row">
                    <span>{row.user_name}</span>
                    <span>{row.percent.toFixed(2)}%</span>
                    <span className="amount">${row.share.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="form-actions">
            <button type="submit" className="btn" disabled={splitType === 'custom' && !ratioOk}>Confirm & save</button>
          </div>
        </form>
        {message && <div className="alert alert-success">✅ {message}</div>}
        {Object.entries(errors).map(([field, msg]) => (
          <div key={field} className="alert alert-error">{msg}</div>
        ))}
      </div>
    </div>
  )
}
