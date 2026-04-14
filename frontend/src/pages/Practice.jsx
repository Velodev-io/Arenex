import { useState, useEffect, useRef } from 'react';
import ChessBoard from '../components/ChessBoard';
import TTTBoard from '../components/TTTBoard';
import { Chess } from 'chess.js';

const Practice = () => {
  const [gameType, setGameType] = useState('chess');
  const [difficulty, setDifficulty] = useState(10);
  const [matchId, setMatchId] = useState(null);
  const [history, setHistory] = useState([]);
  const [status, setStatus] = useState('setup'); // setup, playing, finished
  const [game, setGame] = useState(new Chess());
  const [tttBoard, setTttBoard] = useState([["","",""],["","",""],["","",""]]);
  const [isThinking, setIsThinking] = useState(false);
  
  const ws = useRef(null);

  const startPractice = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/matches/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          is_practice: true,
          game_type: gameType,
          difficulty: parseInt(difficulty)
        })
      });
      const data = await response.json();
      setMatchId(data.id);
      setHistory([]);
      setStatus('playing');
      if (gameType === 'chess') setGame(new Chess());
      else setTttBoard([["","",""],["","",""],["","",""]]);
      
      // Setup WS connection for bot moves
      connectWs(data.id);
    } catch (err) {
      console.error('Failed to start practice:', err);
    }
  };

  const connectWs = (id) => {
    if (ws.current) ws.current.close();
    ws.current = new WebSocket(`${import.meta.env.VITE_WS_URL}/ws/matches/${id}`);
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'move') {
        const move = message.data;
        setHistory(prev => [...prev, move]);
        
        if (move.agent === 'bot') {
          setIsThinking(false);
          if (gameType === 'chess' && move.move) {
            const gameCopy = new Chess(game.fen());
            gameCopy.move(move.move);
            setGame(gameCopy);
          } else if (gameType === 'tictactoe' && move.move) {
            const newBoard = [...tttBoard];
            newBoard[move.move.row][move.move.col] = 'O';
            setTttBoard(newBoard);
          }
        }
      }
    };
  };

  const handleUserMove = async (moveUCI) => {
    if (status !== 'playing' || isThinking) return;

    // Local update
    const gameCopy = new Chess(game.fen());
    try {
      const result = gameCopy.move(moveUCI);
      if (!result) return;
      setGame(gameCopy);
      setIsThinking(true);

      // Send to backend
      await fetch(`${import.meta.env.VITE_API_URL}/matches/${matchId}/user-move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          move: moveUCI,
          fen: gameCopy.fen()
        })
      });
    } catch (e) {
      console.error('Illegal move:', e);
    }
  };

  const handleTTTClick = async (r, c) => {
    if (status !== 'playing' || isThinking || tttBoard[r][c] !== '') return;

    const newBoard = [...tttBoard];
    newBoard[r][c] = 'X';
    setTttBoard(newBoard);
    setIsThinking(true);

    await fetch(`${import.meta.env.VITE_API_URL}/matches/${matchId}/user-move`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        move: `${r},${c}`,
        board: newBoard
      })
    });
  };

  return (
    <div className="container">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '40px' }}>
        {/* Settings Column */}
        <div>
          <h2 style={{ color: 'var(--accent)' }}>Practice Mode</h2>
          <p style={{ color: 'var(--text-dim)', fontSize: '14px' }}>
            Hone your skills against the Arenex house agents before deploying your own.
          </p>

          <div className="card" style={{ padding: '20px', marginTop: '30px' }}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px', fontWeight: 'bold', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Game Type</label>
              <select 
                value={gameType} 
                onChange={(e) => setGameType(e.target.value)}
                disabled={status === 'playing'}
                style={{ width: '100%' }}
              >
                <option value="chess">Chess (Stockfish)</option>
                <option value="tictactoe">Tic-Tac-Toe (Rule-based)</option>
              </select>
            </div>

            <div style={{ marginBottom: '30px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px', fontWeight: 'bold', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Difficulty</label>
              <div style={{ display: 'flex', gap: '10px' }}>
                {[
                  { label: 'Easy', val: 5 },
                  { label: 'Medium', val: 10 },
                  { label: 'Hard', val: 15 }
                ].map(d => (
                  <button 
                    key={d.val}
                    onClick={() => setDifficulty(d.val)}
                    style={{ 
                      flex: 1, 
                      fontSize: '12px',
                      backgroundColor: difficulty === d.val ? 'var(--accent)' : 'transparent',
                      color: difficulty === d.val ? '#000' : 'var(--text)',
                      border: '1px solid var(--border)'
                    }}
                    disabled={status === 'playing'}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>

            <button 
              className="btn-primary" 
              style={{ width: '100%' }} 
              onClick={startPractice}
              disabled={status === 'playing'}
            >
              {status === 'playing' ? 'MATCH IN PROGRESS' : 'START PRACTICE'}
            </button>
            
            {status === 'playing' && (
              <button 
                onClick={() => setStatus('setup')}
                style={{ width: '100%', marginTop: '10px', backgroundColor: 'transparent', border: '1px solid var(--error)', color: 'var(--error)' }}
              >
                QUIT MATCH
              </button>
            )}
          </div>
          
          {history.length > 0 && (
            <div className="card" style={{ marginTop: '20px', padding: '15px', maxHeight: '300px', overflowY: 'auto' }}>
              <h5 style={{ margin: '0 0 10px 0', fontSize: '11px', color: 'var(--text-dim)' }}>LIVE HISTORY</h5>
              {history.slice().reverse().map((h, i) => (
                <div key={i} style={{ fontSize: '13px', padding: '4px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--accent)' }}>{h.agent}:</span> {typeof h.move === 'string' ? h.move : `(${h.move.row}, ${h.move.col})`}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Board Column */}
        <div style={{ position: 'relative' }}>
          {status === 'setup' ? (
            <div className="card" style={{ height: '500px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', borderStyle: 'dashed' }}>
              <div style={{ fontSize: '40px', marginBottom: '10px' }}>♟️</div>
              <h3>Select your options to begin</h3>
              <p style={{ color: 'var(--text-dim)' }}>The board will appear here once the match starts.</p>
            </div>
          ) : (
            <>
              <div className="card" style={{ padding: '40px' }}>
                {gameType === 'chess' ? (
                  <ChessBoard 
                    fen={game.fen()} 
                    onMove={handleUserMove} 
                    draggable={status === 'playing' && !isThinking}
                  />
                ) : (
                  <div style={{ maxWidth: '400px', margin: '0 auto' }}>
                    <TTTBoard board={tttBoard} onCellClick={handleTTTClick} />
                  </div>
                )}
              </div>
              
              {isThinking && (
                <div style={{ 
                  position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, 
                  backgroundColor: 'rgba(26, 26, 46, 0.6)', 
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  borderRadius: '12px', zIndex: 10
                }}>
                  <div className="card" style={{ padding: '20px 40px', backgroundColor: 'var(--card-bg)', border: '1px solid var(--accent)' }}>
                    <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>AGENT IS THINKING...</span>
                  </div>
                </div>
              )}
            </>
          )}

          {status === 'playing' && (
            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '30px', color: 'var(--text-dim)', fontSize: '14px' }}>
               <div>YOU: <span style={{ color: 'var(--text)', fontWeight: 'bold' }}>WHITE/X</span></div>
               <div>BOT: <span style={{ color: 'var(--text)', fontWeight: 'bold' }}>BLACK/O (Skill {difficulty})</span></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Practice;
