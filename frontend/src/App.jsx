import { useState } from 'react'
import { Routes, Route, Link, NavLink } from 'react-router-dom'
import AddBill        from './pages/AddBill'
import GroupBills     from './pages/GroupBills'
import EditBill       from './pages/EditBill'
import BalanceSummary from './pages/BalanceSummary'
import MonthlyReport  from './pages/MonthlyReport'
import Register       from './pages/Register'
import Login          from './pages/Login'
import { clearSession, getStoredUser } from './api'

const NAV_ITEMS = [
  { to: '/add-bill', label: 'Add Bill',       icon: '➕', desc: 'Record a new shared expense and split it.' },
  { to: '/bills',    label: 'Group Bills',    icon: '🧾', desc: 'See, edit, or delete bills in your group.' },
  { to: '/balance',  label: 'Balance',        icon: '⚖️', desc: 'Find out who owes whom, settle, or remind.' },
  { to: '/report',   label: 'Monthly Report', icon: '📊', desc: 'Review spending by month and category.' },
]

function Home({ user }) {
  return (
    <div>
      <section className="hero">
        <h1>{user ? `Welcome back, ${user.name} 👋` : 'Welcome to SplitBill 👋'}</h1>
        <p>{user
          ? 'Your dashboard is ready — split bills, check balances, and settle up.'
          : 'Split shared bills with your group — fair, simple, and transparent.'}</p>
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
  const [user, setUser] = useState(getStoredUser())

  const logout = () => {
    clearSession()
    setUser(null)
  }

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
          <div className="nav-auth">
            {user ? (
              <>
                <span className="nav-user">{user.name}</span>
                <button type="button" className="nav-link nav-button" onClick={logout}>Log out</button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="nav-link">Log in</NavLink>
                <NavLink to="/register" className="nav-link">Register</NavLink>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className="container">
        <Routes>
          <Route path="/"              element={<Home user={user} />} />
          <Route path="/add-bill"      element={<AddBill />} />
          <Route path="/bills"         element={<GroupBills />} />
          <Route path="/bills/:id/edit" element={<EditBill />} />
          <Route path="/balance"       element={<BalanceSummary />} />
          <Route path="/report"        element={<MonthlyReport />} />
          <Route path="/register"      element={<Register onAuth={setUser} />} />
          <Route path="/login"         element={<Login onAuth={setUser} />} />
        </Routes>
      </main>
    </div>
  )
}
