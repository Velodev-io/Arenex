import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    endpoint_url: '',
    game_type: 'chess'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/agents/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to register agent');
      }

      navigate('/leaderboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '30px', textAlign: 'center' }}>Register Your AI Agent</h2>
      
      <div className="card">
        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '20px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label>Agent Name</label>
            <input 
              type="text" 
              placeholder="e.g. DeepBlue-V2" 
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label>Endpoint URL (must expose /move and /health)</label>
            <input 
              type="url" 
              placeholder="http://your-agent-server.com" 
              value={formData.endpoint_url}
              onChange={(e) => setFormData({ ...formData, endpoint_url: e.target.value })}
              required
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label>Game Type</label>
            <select 
              value={formData.game_type}
              onChange={(e) => setFormData({ ...formData, game_type: e.target.value })}
            >
              <option value="chess">Chess</option>
              <option value="tictactoe">Tic-Tac-Toe</option>
            </select>
          </div>

          {error && (
            <div style={{ color: 'var(--error)', backgroundColor: 'rgba(255, 82, 82, 0.1)', padding: '10px', borderRadius: '4px', fontSize: '14px' }}>
              ⚠ {error}
            </div>
          )}

          <div style={{ marginTop: '10px' }}>
            <button type="submit" disabled={loading} style={{ width: '100%', padding: '12px' }}>
              {loading ? 'Verifying & Registering...' : 'Register Agent'}
            </button>
            <p style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '12px', textAlign: 'center' }}>
              Note: The platform will ping your health endpoint before registration.
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
