import { useEffect, useState } from 'react'
import axios from 'axios'

const currentMonth = () => new Date().toISOString().slice(0, 7)

// US06: View Monthly Report
export default function MonthlyReport() {
  const [period, setPeriod] = useState(currentMonth())
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const [year, month] = period.split('-').map(Number)
    if (!year || !month) return
    setError('')
    axios.get('/api/reports/monthly', { params: { group_id: 1, year, month } })
      .then(({ data }) => setReport(data))
      .catch(() => setError('Could not load the report.'))
  }, [period])

  return (
    <div>
      <h2>US06 — Monthly Report</h2>
      <input type="month" value={period} onChange={e => setPeriod(e.target.value)} />
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      {report && (report.bill_count === 0
        ? <p style={{ color: '#888' }}>No expenses recorded for this period</p>
        : (
          <div>
            <p>Total spent: ${report.total.toFixed(2)}</p>
            <p>Number of bills: {report.bill_count}</p>
            <h3>By category</h3>
            {report.categories.map(c => <div key={c.category}>{c.category}: ${c.amount.toFixed(2)}</div>)}
            <h3>Bills</h3>
            {report.items.map(item => <div key={item.id}>{item.date} — {item.title}: ${item.amount.toFixed(2)}</div>)}
          </div>
        )
      )}
    </div>
  )
}
