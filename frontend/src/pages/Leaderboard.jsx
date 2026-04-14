import { useState, useEffect } from 'react';

const Leaderboard = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/agents/`);
        const data = await response.json();
        setAgents(data.sort((a, b) => b.elo - a.elo));
      } catch (error) {
        console.error('Error fetching agents:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
  }, []);

  const filteredAgents = filter === 'all' 
    ? agents 
    : agents.filter(a => a.game_type === filter);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2>Arena Leaderboard</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={() => setFilter('all')}
            style={{ backgroundColor: filter === 'all' ? 'var(--accent)' : 'var(--bg-card)', color: filter === 'all' ? '#000' : 'var(--text)' }}
          >All</button>
          <button 
            onClick={() => setFilter('chess')}
            style={{ backgroundColor: filter === 'chess' ? 'var(--accent)' : 'var(--bg-card)', color: filter === 'chess' ? '#000' : 'var(--text)' }}
          >Chess</button>
          <button 
            onClick={() => setFilter('tictactoe')}
            style={{ backgroundColor: filter === 'tictactoe' ? 'var(--accent)' : 'var(--bg-card)', color: filter === 'tictactoe' ? '#000' : 'var(--text)' }}
          >Tic-Tac-Toe</button>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>Loading rankings...</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', color: 'var(--text-dim)', borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '16px' }}>Rank</th>
                <th style={{ padding: '16px' }}>Agent Name</th>
                <th style={{ padding: '16px' }}>Game Type</th>
                <th style={{ padding: '16px' }}>ELO</th>
                <th style={{ padding: '16px' }}>Endpoint</th>
              </tr>
            </thead>
            <tbody>
              {filteredAgents.map((agent, index) => (
                <tr key={agent.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '16px', fontWeight: 'bold' }}>
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                  </td>
                  <td style={{ padding: '16px', fontWeight: 'bold', color: 'var(--accent)' }}>{agent.name}</td>
                  <td style={{ padding: '16px' }}>{agent.game_type.toUpperCase()}</td>
                  <td style={{ padding: '16px' }}>
                    <span style={{ backgroundColor: '#2a2a4a', padding: '4px 8px', borderRadius: '4px' }}>
                      {agent.elo}
                    </span>
                  </td>
                  <td style={{ padding: '16px', fontSize: '12px', color: 'var(--text-dim)' }}>{agent.endpoint_url}</td>
                </tr>
              ))}
              {filteredAgents.length === 0 && (
                <tr>
                  <td colSpan="5" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-dim)' }}>
                    No agents registered for this category yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;
