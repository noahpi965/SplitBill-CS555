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
      <div className="page-header">
        <span className="tag">US06</span>
        <h2>Monthly Report</h2>
        <p>Spending breakdown for the selected month.</p>
      </div>
      <div className="toolbar">
        <label htmlFor="period">Month</label>
        <input id="period" type="month" value={period} onChange={e => setPeriod(e.target.value)} />
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      {report && (report.bill_count === 0
        ? <div className="card empty"><span className="emoji">📭</span>No expenses recorded for this period</div>
        : (
          <div>
            <div className="stats">
              <div className="card">
                <div className="stat-label">Total spent</div>
                <div className="stat-value">${report.total.toFixed(2)}</div>
              </div>
              <div className="card">
                <div className="stat-label">Number of bills</div>
                <div className="stat-value">{report.bill_count}</div>
              </div>
            </div>
            <div className="card">
              <h3>By category</h3>
              {report.categories.map(c => (
                <div key={c.category} className="category-row">
                  <div className="top">
                    <span>{c.category}</span>
                    <span className="amount">${c.amount.toFixed(2)}</span>
                  </div>
                  <div className="bar">
                    <div className="bar-fill" style={{ width: `${report.total ? (c.amount / report.total) * 100 : 0}%` }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="card">
              <h3>Bills</h3>
              {report.items.map(item => (
                <div key={item.id} className="item-row">
                  <span><span className="item-date">{item.date}</span>{item.title}</span>
                  <span className="amount">${item.amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )
      )}
    </div>
  )
}
