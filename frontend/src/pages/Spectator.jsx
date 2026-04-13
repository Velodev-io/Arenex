import { useState, useEffect, useRef, useMemo } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import ChessBoard from '../components/ChessBoard';
import TTTBoard from '../components/TTTBoard';

const INITIAL_FEN = "rnbqkbnr/1ppppppp/8/8/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 1";

const Spectator = () => {
  const { id } = useParams();
  const location = useLocation();
  const [match, setMatch] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('connecting');
  
  // Replay State
  const [viewIndex, setViewIndex] = useState(-1);
  const [followLive, setFollowLive] = useState(true);
  const [isAutoPlaying, setIsAutoPlaying] = useState(false);

  useEffect(() => {
    followLiveRef.current = followLive;
  }, [followLive]);
  const [currentFen, setCurrentFen] = useState(INITIAL_FEN);
  
  // Social State
  const [likes, setLikes] = useState(0);
  const [comments, setComments] = useState([]);
  const [nickname, setNickname] = useState('');
  const [commentText, setCommentText] = useState('');
  
  const ws = useRef(null);
  const followLiveRef = useRef(true);
  const playbackTimer = useRef(null);

  const isReplayUrl = location.pathname.endsWith('/replay');

  useEffect(() => {
    // 1. Fetch initial match state
    const fetchMatch = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/matches/${id}`);
        if (!response.ok) throw new Error(`HTTP ${response.status} Match fetch failed`);
        const data = await response.json();
        setMatch(data);
        const fetchedHistory = data.history || [];
        setHistory(fetchedHistory);
        const fetchedMoves = fetchedHistory.filter(h => h.move !== undefined);
        
        // Handle initial view position
        if (isReplayUrl) {
          setFollowLive(false);
          const firstIdx = fetchedMoves.length > 0 ? 0 : -1;
          setViewIndex(firstIdx);
          setCurrentFen(fetchedMoves[0]?.fen || INITIAL_FEN);
        } else {
          setFollowLive(true);
          const lastIdx = fetchedMoves.length - 1;
          setViewIndex(lastIdx);
          setCurrentFen(fetchedMoves[lastIdx]?.fen || INITIAL_FEN);
        }

        // Fetch Social Stats
        fetchSocial();
      } catch (err) {
        console.error('Error fetching match:', err);
      } finally {
        setLoading(false);
      }
    };

    const fetchSocial = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/social/${id}/stats`);
        if (!res.ok) throw new Error(`HTTP ${res.status} Social stats fetch failed`);
        const data = await res.json();
        setLikes(data.likes);
        setComments(data.comments);
      } catch (err) {
        console.error('Error fetching social:', err);
      }
    };

    fetchMatch();

    // 2. Connect to WebSocket
    let didCleanup = false;
    const wsBaseUrl = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace(/^http/, 'ws') : 'ws://localhost:8000';
    const wsUrl = `${wsBaseUrl}/ws/matches/${id}`;
    const socket = new WebSocket(wsUrl);
    ws.current = socket;

    socket.onopen = () => { if (!didCleanup) setStatus('live'); };
    socket.onclose = () => { if (!didCleanup) setStatus('disconnected'); };
    socket.onerror = (err) => console.error('WebSocket error:', err);
    socket.onmessage = (event) => {
      if (didCleanup) return;
      try {
        const message = JSON.parse(event.data);
      
      if (message.type === 'catchup') {
        const newHistory = (message.history || []).filter(h => h.move !== undefined);
        setHistory(newHistory);
        if (newHistory.length > 0) {
          const lastMove = newHistory[newHistory.length - 1];
          setCurrentFen(lastMove.fen || INITIAL_FEN);
          setViewIndex(newHistory.length - 1);
        }
      } else if (message.type === 'move') {
        const moveData = message.data;
        if (!moveData || !moveData.move) return;
        setHistory(prev => {
          const next = [...prev, moveData];
          setCurrentFen(moveData.fen || INITIAL_FEN);
          setViewIndex(next.length - 1);
          return next;
        });
      } else if (message.type === 'finished') {
        setStatus('finished');
        setMatch(prev => ({ ...prev, status: 'finished', result: message.result }));
      }
      } catch (e) {
        console.error('Failed to parse websocket message:', e);
      }
    };

    return () => {
      didCleanup = true;
      if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
        socket.close();
      }
      if (playbackTimer.current) clearInterval(playbackTimer.current);
    };
  }, [id, isReplayUrl]);

  const moveHistory = useMemo(() => history.filter(h => h.move !== undefined), [history]);

  // Sync viewIndex when history updates and followLive is on (fallback for REST-loaded state)
  useEffect(() => {
    if (followLive && moveHistory.length > 0) {
      const lastIdx = moveHistory.length - 1;
      setViewIndex(lastIdx);
      const lastFen = moveHistory[lastIdx]?.fen;
      if (lastFen) setCurrentFen(lastFen);
    }
  }, [moveHistory.length, followLive]);

  // Keep currentFen in sync when user scrubs history manually
  useEffect(() => {
    if (viewIndex >= 0 && moveHistory[viewIndex]?.fen) {
      setCurrentFen(moveHistory[viewIndex].fen);
    } else if (viewIndex === -1) {
      setCurrentFen(INITIAL_FEN);
    }
  }, [viewIndex, moveHistory]);

  // Auto-playback logic
  useEffect(() => {
    if (isAutoPlaying) {
      playbackTimer.current = setInterval(() => {
        setViewIndex(prev => {
          if (prev < moveHistory.length - 1) return prev + 1;
          setIsAutoPlaying(false);
          return prev;
        });
      }, 1000);
    } else {
      if (playbackTimer.current) clearInterval(playbackTimer.current);
    }
    return () => { if (playbackTimer.current) clearInterval(playbackTimer.current); };
  }, [isAutoPlaying, moveHistory.length]);

  if (loading) return <div className="container" style={{ textAlign: 'center', padding: '100px' }}>Loading Match Data...</div>;
  if (!match) return <div className="container" style={{ textAlign: 'center', padding: '100px' }}>Match not found.</div>;

  const currentMove = viewIndex >= 0 ? moveHistory[viewIndex] : null;
  const currentTTT = currentMove?.board || [["","",""],["","",""],["",'',""]];
  const lastReasoning = currentMove?.reasoning || (viewIndex === -1 ? "Initial configuration." : "No move selected.");

  const step = (delta) => {
    setFollowLive(false);
    setIsAutoPlaying(false);
    setViewIndex(prev => {
      const next = prev + delta;
      return Math.max(-1, Math.min(next, moveHistory.length - 1));
    });
  };

  const handleLike = async () => {
    try {
      const resp = await fetch(`${import.meta.env.VITE_API_URL}/social/${id}/like`, { method: 'POST' });
      const data = await resp.json();
      setLikes(data.likes);
    } catch (err) {
      console.error('Like failed:', err);
    }
  };

  const handleComment = async () => {
    if (!nickname.trim() || !commentText.trim()) return;
    try {
      const resp = await fetch(`${import.meta.env.VITE_API_URL}/social/${id}/comment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: nickname, content: commentText })
      });
      const data = await resp.json();
      setComments(prev => [data, ...prev]);
      setCommentText('');
    } catch (err) {
      console.error('Comment failed:', err);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: '30px', alignItems: 'start' }}>
      {/* Board Column */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h3 style={{ margin: 0 }}>Match #{id} {isReplayUrl && <span style={{ color: 'var(--text-dim)', fontSize: '14px' }}>(Replay)</span>}</h3>
            <div style={{ color: 'var(--text-dim)', fontSize: '14px' }}>
              {status === 'live' && <span style={{ color: 'var(--success)' }}>● LIVE</span>}
              {status === 'finished' && <span style={{ color: 'var(--accent)' }}>■ FINISHED</span>}
              {status === 'disconnected' && <span style={{ color: 'var(--error)' }}>⚠ DISCONNECTED</span>}
              {followLive && status === 'live' && <span style={{ marginLeft: '10px', fontSize: '11px', backgroundColor: 'var(--accent)', color: '#000', padding: '2px 6px', borderRadius: '4px', fontWeight: 'bold' }}>FOLLOWING LIVE</span>}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontWeight: 'bold' }}>{match.agent_white_id} vs {match.agent_black_id}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>{moveHistory.length} Total Moves</div>
          </div>
        </div>

        <div className="card" style={{ padding: '30px', marginBottom: '15px' }}>
          {(match.game_type === 'chess' || moveHistory[0]?.fen) ? (
            <ChessBoard fen={currentFen} />
          ) : (
            <TTTBoard board={currentTTT} />
          )}
        </div>

        {/* Playback Controls */}
        <div className="card" style={{ padding: '10px 20px', marginBottom: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '15px' }}>
          <button onClick={() => { setViewIndex(-1); setFollowLive(false); setIsAutoPlaying(false); }} title="First Move">|&lt;</button>
          <button onClick={() => step(-1)} disabled={viewIndex <= -1} title="Previous Move">&lt;</button>
          
          <button 
            onClick={() => setIsAutoPlaying(!isAutoPlaying)}
            style={{ width: '100px', backgroundColor: isAutoPlaying ? 'var(--error)' : 'var(--success)', color: '#000' }}
          >
            {isAutoPlaying ? 'PAUSE' : 'PLAY'}
          </button>
          
          <button onClick={() => step(1)} disabled={viewIndex >= moveHistory.length - 1} title="Next Move">&gt;</button>
          <button onClick={() => { setFollowLive(true); setIsAutoPlaying(false); }} title="Live / End">&gt;|</button>
          
          <div style={{ marginLeft: '20px', color: 'var(--text-dim)', fontSize: '14px' }}>
            {viewIndex === -1 ? 'Initial' : `Move ${viewIndex + 1} / ${moveHistory.length}`}
          </div>
        </div>

        <div className="card">
          <h4>Social & Feedback</h4>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '20px' }}>
            <button 
              onClick={handleLike} 
              style={{ 
                fontSize: '20px', 
                backgroundColor: 'transparent', 
                border: '2px solid var(--accent)', 
                borderRadius: '50%', 
                width: '50px', 
                height: '50px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                cursor: 'pointer',
                color: 'var(--accent)',
                transition: 'transform 0.2s'
              }}
              onMouseDown={(e) => e.target.style.transform = 'scale(1.2)'}
              onMouseUp={(e) => e.target.style.transform = 'scale(1)'}
            >
              ❤
            </button>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{likes} Likes</div>
          </div>

          <div style={{ maxHeight: '300px', overflowY: 'auto', marginBottom: '20px', borderTop: '1px solid var(--border)', paddingTop: '15px' }}>
            {comments.map((c, i) => (
              <div key={i} style={{ marginBottom: '12px', fontSize: '14px' }}>
                <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{c.display_name}:</span> {c.content}
                <div style={{ fontSize: '10px', color: 'var(--text-dim)' }}>{new Date(c.created_at).toLocaleString()}</div>
              </div>
            ))}
            {comments.length === 0 && <div style={{ color: 'var(--text-dim)', textAlign: 'center' }}>No comments yet.</div>}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input 
              type="text" 
              placeholder="Display Name" 
              value={nickname} 
              onChange={(e) => setNickname(e.target.value)} 
              style={{ padding: '8px' }}
            />
            <div style={{ display: 'flex', gap: '10px' }}>
              <input 
                type="text" 
                placeholder="Say something..." 
                value={commentText} 
                onChange={(e) => setCommentText(e.target.value)} 
                style={{ flex: 1, padding: '8px' }}
              />
              <button 
                onClick={handleComment}
                className="btn-primary"
                style={{ height: 'auto' }}
              >
                POST
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar Column */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="card" style={{ padding: '15px' }}>
          <h5 style={{ color: 'var(--accent)', marginBottom: '10px', textTransform: 'uppercase', fontSize: '11px' }}>Reasoning at current view</h5>
          <div style={{ fontSize: '13px', fontStyle: 'italic', lineHeight: '1.4', minHeight: '60px' }}>
            "{lastReasoning}"
          </div>
        </div>

        <div className="card" style={{ padding: '0', flexGrow: 1, minHeight: '400px', display: 'flex', flexDirection: 'column' }}>
          <h5 style={{ padding: '15px 15px 10px', color: 'var(--text-dim)', textTransform: 'uppercase', fontSize: '11px', borderBottom: '1px solid var(--border)' }}>Move History</h5>
          <div style={{ overflowY: 'auto', flexGrow: 1, maxHeight: '500px' }}>
            {moveHistory.map((h, i) => (
              <div 
                key={i} 
                onClick={() => { setViewIndex(i); setFollowLive(false); setIsAutoPlaying(false); }}
                style={{ 
                  padding: '10px 15px', 
                  borderBottom: '1px solid var(--border)', 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  backgroundColor: viewIndex === i ? 'rgba(187, 134, 252, 0.15)' : 'transparent',
                  borderLeft: viewIndex === i ? '3px solid var(--accent)' : '3px solid transparent'
                }}
              >
                <span style={{ color: viewIndex === i ? 'var(--accent)' : 'var(--text)' }}>{i + 1}. {h.agent}</span>
                <span style={{ fontFamily: 'monospace', color: 'var(--text-dim)' }}>{typeof h.move === 'string' ? h.move : h.move ? `(${h.move.row}, ${h.move.col})` : ''}</span>
              </div>
            ))}
            {moveHistory.length === 0 && <div style={{ padding: '20px', color: 'var(--text-dim)', textAlign: 'center' }}>No moves yet.</div>}
            <div style={{ padding: '15px', textAlign: 'center' }}>
               <button 
                 onClick={() => { setFollowLive(true); setIsAutoPlaying(false); }}
                 style={{ fontSize: '12px', padding: '4px 8px', backgroundColor: 'transparent', border: '1px solid var(--border)', color: 'var(--text-dim)' }}
               >Jump to Live</button>
            </div>
          </div>
        </div>

        {status === 'finished' && (
          <div className="card" style={{ backgroundColor: 'rgba(0, 230, 118, 0.1)', borderColor: 'var(--success)' }}>
            <h5 style={{ color: 'var(--success)', marginBottom: '5px' }}>Match Outcome</h5>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{match.result?.replace('_', ' ').toUpperCase() || 'DRAW'}</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Spectator;
