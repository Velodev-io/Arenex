import { Chessboard } from 'react-chessboard';

const ChessBoard = ({ fen }) => {
  const standardCounts = {
    'p': 8, 'r': 2, 'n': 2, 'b': 2, 'q': 1,
    'P': 8, 'R': 2, 'N': 2, 'B': 2, 'Q': 1
  };

  const currentCounts = {
    'p': 0, 'r': 0, 'n': 0, 'b': 0, 'q': 0,
    'P': 0, 'R': 0, 'N': 0, 'B': 0, 'Q': 0
  };

  const fenBoard = fen.split(' ')[0];
  for (let i = 0; i < fenBoard.length; i++) {
    const char = fenBoard[i];
    if (currentCounts[char] !== undefined) {
      currentCounts[char]++;
    }
  }

  const getMissing = (isWhite) => {
    const missing = [];
    const pieces = isWhite ? ['P', 'R', 'N', 'B', 'Q'] : ['p', 'r', 'n', 'b', 'q'];
    pieces.forEach(p => {
      const diff = standardCounts[p] - currentCounts[p];
      for (let i = 0; i < diff; i++) {
        missing.push(p);
      }
    });
    return missing;
  };

  const missingWhite = getMissing(true);
  const missingBlack = getMissing(false);

  const pieceSymbols = {
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛',
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕'
  };

  const Tray = ({ pieces, isTop }) => (
    <div style={{
      display: 'flex', 
      minHeight: '36px', 
      alignItems: 'center', 
      padding: '4px 12px', 
      backgroundColor: '#1E1E24', 
      borderTopLeftRadius: isTop ? '6px' : '0',
      borderTopRightRadius: isTop ? '6px' : '0',
      borderBottomLeftRadius: isTop ? '0' : '6px',
      borderBottomRightRadius: isTop ? '0' : '6px',
      fontSize: '24px',
      color: '#fff',
      gap: '2px',
      boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.3)'
    }}>
      {pieces.length === 0 ? <span style={{opacity: 0}}>.</span> : pieces.map((p, i) => <span key={i}>{pieceSymbols[p]}</span>)}
    </div>
  );

  return (
    <div style={{ width: '100%', maxWidth: '600px', margin: '0 auto', boxShadow: '0 10px 30px rgba(0,0,0,0.5)', borderRadius: '6px' }}>
      <Tray pieces={missingWhite} isTop={true} />
      <Chessboard
        position={fen}
        arePiecesDraggable={false}
        animationDuration={200}
        customBoardStyle={{
          borderRadius: '0px',
          boxShadow: 'none'
        }}
        customDarkSquareStyle={{ backgroundColor: '#769656' }}
        customLightSquareStyle={{ backgroundColor: '#eeeed2' }}
      />
      <Tray pieces={missingBlack} isTop={false} />
    </div>
  );
};

export default ChessBoard;
