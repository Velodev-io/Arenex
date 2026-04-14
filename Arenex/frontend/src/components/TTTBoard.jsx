const TTTBoard = ({ board }) => {
  // board is a 2D array [["", "", ""], ...]
  return (
    <div style={{ 
      display: 'grid', 
      gridTemplateColumns: 'repeat(3, 1fr)', 
      gridTemplateRows: 'repeat(3, 1fr)',
      gap: '10px',
      width: '100%',
      maxWidth: '400px',
      aspectRatio: '1/1',
      margin: '0 auto',
      backgroundColor: 'var(--border)',
      padding: '10px',
      borderRadius: '8px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
    }}>
      {board.map((row, r) => (
        row.map((cell, c) => (
          <div 
            key={`${r}-${c}`}
            style={{
              backgroundColor: 'var(--bg-card)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '48px',
              fontWeight: 'bold',
              borderRadius: '4px'
            }}
          >
            {cell === 'X' && <span style={{ color: 'var(--accent)' }}>X</span>}
            {cell === 'O' && <span style={{ color: '#ffffff' }}>O</span>}
          </div>
        ))
      ))}
    </div>
  );
};

export default TTTBoard;
