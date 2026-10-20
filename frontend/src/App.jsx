import { Routes, Route, Link, NavLink } from 'react-router-dom'
import AddBill        from './pages/AddBill'
import GroupBills     from './pages/GroupBills'
import BalanceSummary from './pages/BalanceSummary'
import MonthlyReport  from './pages/MonthlyReport'

const NAV_ITEMS = [
  { to: '/add-bill', label: 'Add Bill',       icon: '➕', desc: 'Record a new shared expense and split it.' },
  { to: '/bills',    label: 'Group Bills',    icon: '🧾', desc: 'See every bill in your group.' },
  { to: '/balance',  label: 'Balance',        icon: '⚖️', desc: 'Find out who owes whom.' },
  { to: '/report',   label: 'Monthly Report', icon: '📊', desc: 'Review spending by month and category.' },
]

function Home() {
  return (
    <div>
      <section className="hero">
        <h1>Welcome to SplitBill 👋</h1>
        <p>Split shared bills with your group — fair, simple, and transparent.</p>
      </section>
      <div className="feature-grid">
        {NAV_ITEMS.map(item => (
          <Link key={item.to} to={item.to} className="card feature">
            <span className="icon">{item.icon}</span>
            <h3>{item.label}</h3>
            <p>{item.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default function App() {
  return (
    <div>
      <nav className="navbar">
        <div className="navbar-inner">
          <Link to="/" className="brand">💸 SplitBill</Link>
          <div className="nav-links">
            {NAV_ITEMS.map(item => (
              <NavLink key={item.to} to={item.to} className="nav-link">{item.label}</NavLink>
            ))}
          </div>
        </div>
      </nav>

      <main className="container">
        <Routes>
          <Route path="/"          element={<Home />} />
          <Route path="/add-bill"  element={<AddBill />} />
          <Route path="/bills"     element={<GroupBills />} />
          <Route path="/balance"   element={<BalanceSummary />} />
          <Route path="/report"    element={<MonthlyReport />} />
        </Routes>
      </main>
    </div>
  )
}
