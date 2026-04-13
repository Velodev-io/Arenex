import { Link, NavLink } from 'react-router-dom';

const Layout = ({ children }) => {
  return (
    <div>
      <header>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Link to="/" style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--accent)' }}>
            ARENEX
          </Link>
          <nav>
            <ul className="nav-links">
              <li>
                <NavLink to="/" end>Home</NavLink>
              </li>
              <li>
                <NavLink to="/leaderboard">Leaderboard</NavLink>
              </li>
              <li>
                <NavLink to="/register">Register Agent</NavLink>
              </li>
              <li>
                <NavLink to="/start-match">Start Match</NavLink>
              </li>
            </ul>
          </nav>
        </div>
      </header>
      <main className="container">
        {children}
      </main>
      <footer className="container" style={{ marginTop: '60px', padding: '40px 0', borderTop: '1px solid var(--border)', color: 'var(--text-dim)', fontSize: '14px', textAlign: 'center' }}>
        &copy; 2026 Arenex Platform - AI Agent Gaming Ecosystem
      </footer>
    </div>
  );
};

export default Layout;
