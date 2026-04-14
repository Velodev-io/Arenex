import React from 'react';

const MinecraftMatchStats = ({ bot1, bot2, timeRemaining, matchId }) => {
  const formatTime = (seconds) => {
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min}:${sec.toString().padStart(2, '0')}`;
  };

  const ProgressBar = ({ current, max, color }) => {
    const pct = Math.min(100, (current / max) * 100);
    let barColor = '#ff6b6b'; // red
    if (current >= 30) barColor = '#feca57'; // yellow
    if (current >= 50) barColor = '#1dd1a1'; // green
    
    return (
      <div style={{ width: '100%', height: '10px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '5px', marginTop: '8px' }}>
        <div style={{ width: `${pct}%`, height: '100%', backgroundColor: barColor, borderRadius: '5px', transition: 'width 0.5s ease-out' }} />
      </div>
    );
  };

  const HeartDisplay = ({ health }) => {
    const hearts = [];
    for(let i=0; i<5; i++) {
        hearts.push(
            <span key={i} style={{ color: health > i*4 ? '#ff6b6b' : 'rgba(255,255,255,0.1)', fontSize: '14px', marginRight: '2px' }}>
                ❤
            </span>
        );
    }
    return <div>{hearts}</div>;
  };

  const StatPanel = ({ bot, color, initial }) => (
    <div className="card" style={{ flex: 1, borderTop: `4px solid ${color}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h4 style={{ margin: 0 }}>{bot?.name || initial}</h4>
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: color }} />
      </div>
      
      <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginBottom: '4px' }}>Wood Collected</div>
      <div style={{ fontWeight: 'bold' }}>{bot?.wood_count || 0} / 64</div>
      <ProgressBar current={bot?.wood_count || 0} max={64} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '15px' }}>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Health</div>
          <HeartDisplay health={bot?.health || 0} />
        </div>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Action</div>
          <div style={{ fontSize: '12px', fontWeight: 'bold', textTransform: 'capitalize' }}>{bot?.current_action || 'idle'}</div>
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ width: '100%' }}>
      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
        <StatPanel bot={bot1} color="#4a9eff" initial="Bot 1" />
        <StatPanel bot={bot2} color="#ff6b6b" initial="Bot 2" />
      </div>
      
      <div className="card" style={{ textAlign: 'center', padding: '15px' }}>
        <div style={{ fontSize: '14px', color: 'var(--text-dim)', marginBottom: '5px' }}>Time Remaining</div>
        <div style={{ fontSize: '32px', fontWeight: 'bold', color: timeRemaining < 60 ? 'var(--error)' : 'var(--text)' }}>
          {formatTime(Math.max(0, timeRemaining))}
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '8px' }}>
          Match ID: <span style={{ fontFamily: 'monospace' }}>{matchId}</span>
        </div>
      </div>
    </div>
  );
};

export default MinecraftMatchStats;
