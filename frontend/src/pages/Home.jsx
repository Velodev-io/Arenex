import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/matches`);
        const data = await response.json();
        setMatches(data);
      } catch (error) {
        console.error('Error fetching matches:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchMatches();
  }, []);

  const liveMatches = matches.filter(m => m.status === 'live');
  const finishedMatches = matches.filter(m => m.status === 'finished').slice(0, 5);

  return (
    <div>
      <section style={{ marginBottom: '40px' }}>
        <h2 style={{ marginBottom: '20px' }}>Live Matches</h2>
        {loading ? (
          <div>Loading matches...</div>
        ) : liveMatches.length > 0 ? (
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
            {liveMatches.map(match => (
              <Link key={match.id} to={`/match/${match.id}`}>
                <div className="card" style={{ borderLeft: '4px solid var(--accent)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <span style={{ color: 'var(--text-dim)', fontSize: '12px' }}>ID: {match.id}</span>
                    <span style={{ color: 'var(--accent)', fontSize: '12px', fontWeight: 'bold' }}>LIVE</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '15px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontWeight: 'bold' }}>Agent White</div>
                      <div style={{ fontSize: '14px', color: 'var(--text-dim)' }}>ID: {match.agent_white_id}</div>
                    </div>
                    <div style={{ fontWeight: 'bold', fontSize: '20px' }}>VS</div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontWeight: 'bold' }}>Agent Black</div>
                      <div style={{ fontSize: '14px', color: 'var(--text-dim)' }}>ID: {match.agent_black_id}</div>
                    </div>
                  </div>
                  <button style={{ width: '100%' }}>Spectate</button>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-dim)' }}>
            No matches currently in progress.
          </div>
        )}
      </section>

      <section>
        <h2 style={{ marginBottom: '20px' }}>Recent Replays</h2>
        <div className="card">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: 'var(--text-dim)', borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px' }}>ID</th>
                <th style={{ padding: '12px' }}>Players</th>
                <th style={{ padding: '12px' }}>Result</th>
                <th style={{ padding: '12px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {finishedMatches.map(match => (
                <tr key={match.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px' }}>{match.id}</td>
                  <td style={{ padding: '12px' }}>{match.agent_white_id} vs {match.agent_black_id}</td>
                  <td style={{ padding: '12px' }}>{match.result || 'Draw'}</td>
                  <td style={{ padding: '12px' }}>
                    <Link to={`/match/${match.id}`} style={{ fontSize: '14px' }}>View Replay</Link>
                  </td>
                </tr>
              ))}
              {finishedMatches.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ padding: '20px', textAlign: 'center', color: 'var(--text-dim)' }}>No completed matches yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default Home;
