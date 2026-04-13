import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const StartMatch = () => {
  const navigate = useNavigate();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [gameType, setGameType] = useState('chess');
  const [agentW, setAgentW] = useState('');
  const [agentB, setAgentB] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/agents/`);
        const data = await response.json();
        setAgents(data);
      } catch (err) {
        console.error('Error fetching agents:', err);
        setError('Failed to fetch agents. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
  }, []);

  const filteredAgents = agents.filter(a => a.game_type === gameType);

  const handleStart = async (e) => {
    e.preventDefault();
    if (!agentW || !agentB) return;
    
    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/matches/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_white_id: parseInt(agentW),
          agent_black_id: parseInt(agentB)
        })
      });

      if (!response.ok) {
        let errorMsg = 'Failed to start match';
        try {
          const data = await response.json();
          errorMsg = data.detail || errorMsg;
        } catch (_) {}
        throw new Error(errorMsg);
      }

      const match = await response.json();
      navigate(`/match/${match.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '30px', textAlign: 'center' }}>Initiate New Match</h2>

      <div className="card">
        <form onSubmit={handleStart} style={{ display: 'grid', gap: '25px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label>1. Select Game Type</label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                type="button"
                onClick={() => { setGameType('chess'); setAgentW(''); setAgentB(''); }}
                style={{ flex: 1, backgroundColor: gameType === 'chess' ? 'var(--accent)' : 'var(--bg)', color: gameType === 'chess' ? '#000' : 'var(--text)', border: '1px solid var(--border)' }}
              >Chess</button>
              <button 
                type="button"
                onClick={() => { setGameType('tictactoe'); setAgentW(''); setAgentB(''); }}
                style={{ flex: 1, backgroundColor: gameType === 'tictactoe' ? 'var(--accent)' : 'var(--bg)', color: gameType === 'tictactoe' ? '#000' : 'var(--text)', border: '1px solid var(--border)' }}
              >Tic-Tac-Toe</button>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label>Agent White (X)</label>
              <select 
                value={agentW} 
                onChange={(e) => setAgentW(e.target.value)} 
                required
                style={{ width: '100%' }}
              >
                <option value="">Select Agent...</option>
                {filteredAgents.map(a => (
                  <option key={a.id} value={a.id}>{a.name} (ELO: {a.elo})</option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <label>Agent Black (O)</label>
              <select 
                value={agentB} 
                onChange={(e) => setAgentB(e.target.value)} 
                required
                style={{ width: '100%' }}
              >
                <option value="">Select Agent...</option>
                {filteredAgents.map(a => (
                  <option key={a.id} value={a.id}>{a.name} (ELO: {a.elo})</option>
                ))}
              </select>
            </div>
          </div>

          {error && (
            <div style={{ color: 'var(--error)', backgroundColor: 'rgba(255, 82, 82, 0.1)', padding: '10px', borderRadius: '4px', fontSize: '14px' }}>
              ⚠ {error}
            </div>
          )}

          <button 
            type="submit" 
            disabled={submitting || !agentW || !agentB || agentW === agentB}
            style={{ width: '100%', padding: '15px', fontSize: '16px' }}
          >
            {submitting ? 'Creating Match...' : 'Start Battle'}
          </button>
          
          {agentW && agentB && agentW === agentB && (
            <p style={{ color: 'var(--error)', fontSize: '12px', textAlign: 'center' }}>
              Agents cannot play against themselves in V1.
            </p>
          )}
        </form>
      </div>
    </div>
  );
};

export default StartMatch;
