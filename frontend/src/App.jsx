import { Routes, Route, Link } from 'react-router-dom'
import AddBill        from './pages/AddBill'
import GroupBills     from './pages/GroupBills'
import BalanceSummary from './pages/BalanceSummary'
import MonthlyReport  from './pages/MonthlyReport'

export default function App() {
  return (
    <div>
      <nav style={{ padding: '12px', background: '#2A1F14', color: '#fff', display: 'flex', gap: '20px' }}>
        <strong>💸 SplitBill</strong>
        <Link to="/add-bill"   style={{ color: '#F0DFC4' }}>Add Bill</Link>
        <Link to="/bills"      style={{ color: '#F0DFC4' }}>Group Bills</Link>
        <Link to="/balance"    style={{ color: '#F0DFC4' }}>Balance</Link>
        <Link to="/report"     style={{ color: '#F0DFC4' }}>Monthly Report</Link>
      </nav>

      <main style={{ padding: '24px' }}>
        <Routes>
          <Route path="/"          element={<h2>Welcome to SplitBill 👋</h2>} />
          <Route path="/add-bill"  element={<AddBill />} />
          <Route path="/bills"     element={<GroupBills />} />
          <Route path="/balance"   element={<BalanceSummary />} />
          <Route path="/report"    element={<MonthlyReport />} />
        </Routes>
      </main>
    </div>
  )
}
