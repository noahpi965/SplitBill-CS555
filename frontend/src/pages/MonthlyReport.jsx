import { useEffect, useState } from 'react'

// US06: View Monthly Report
export default function MonthlyReport() {
  const [report, setReport] = useState(null)

  useEffect(() => {
    // TODO: fetch from GET /api/reports/monthly?group_id=1&year=2026&month=10 in Sprint 1
    setReport(null) // stub
  }, [])

  return (
    <div>
      <h2>US06 — Monthly Report</h2>
      {!report
        ? <p style={{ color: '#888' }}>No report data yet.</p>
        : (
          <div>
            <p>Total spent: ${report.total}</p>
            {report.items.map((item, i) => <div key={i}>{item.title}: ${item.amount}</div>)}
          </div>
        )
      }
    </div>
  )
}
