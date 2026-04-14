import React, { useEffect, useRef, useState } from 'react';

const SCALE = 4; // 1 minecraft unit = 4 canvas pixels
const WIDTH = 600;
const HEIGHT = 400;

const MinecraftMap = ({ matchId, viewerUrl = null, bot1, bot2 }) => {
  const canvasRef = useRef(null);
  const requestRef = useRef();
  const [viewerReady, setViewerReady] = useState(false);
  const [viewerError, setViewerError] = useState(false);
  
  // Interpolation state
  const bot1Pos = useRef({ x: 0, z: 0 });
  const bot2Pos = useRef({ x: 0, z: 0 });
  const target1Pos = useRef({ x: 0, z: 0 });
  const target2Pos = useRef({ x: 0, z: 0 });

  // Update targets when props change
  useEffect(() => {
    if (bot1?.position) target1Pos.current = { x: bot1.position.x, z: bot1.position.z };
    if (bot2?.position) target2Pos.current = { x: bot2.position.x, z: bot2.position.z };
  }, [bot1, bot2]);

  // Seeded Random for trees
  const trees = React.useMemo(() => {
    const seed = matchId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const treeList = [];
    let s = seed;
    for (let i = 0; i < 15; i++) {
        s = (s * 9301 + 49297) % 233280;
        const x = (s % WIDTH);
        s = (s * 9301 + 49297) % 233280;
        const z = (s % HEIGHT);
        treeList.push({ x, z });
    }
    return treeList;
  }, [matchId]);

  const animate = (time) => {
    if (!canvasRef.current) return;
    const ctx = canvasRef.current.getContext('2d');
    
    // Interpolate
    const lerp = (start, end) => start + (end - start) * 0.1;
    bot1Pos.current.x = lerp(bot1Pos.current.x, target1Pos.current.x);
    bot1Pos.current.z = lerp(bot1Pos.current.z, target1Pos.current.z);
    bot2Pos.current.x = lerp(bot2Pos.current.x, target2Pos.current.x);
    bot2Pos.current.z = lerp(bot2Pos.current.z, target2Pos.current.z);

    // Render
    ctx.clearRect(0, 0, WIDTH, HEIGHT);
    
    // Grass
    ctx.fillStyle = '#1a472a';
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    // Grid
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.beginPath();
    for(let i=0; i<WIDTH; i+=20) { ctx.moveTo(i,0); ctx.lineTo(i,HEIGHT); }
    for(let i=0; i<HEIGHT; i+=20) { ctx.moveTo(0,i); ctx.lineTo(WIDTH,i); }
    ctx.stroke();

    // Trees
    ctx.fillStyle = '#0a2e18';
    trees.forEach(t => {
        ctx.beginPath();
        ctx.arc(t.x, t.z, 8, 0, Math.PI * 2);
        ctx.fill();
    });

    // Translate and center Minecraft (0,0) to center of canvas (approx)
    const renderBot = (pos, color, label) => {
        const rx = WIDTH/2 + pos.x * SCALE;
        const rz = HEIGHT/2 + pos.z * SCALE;
        
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(rx, rz, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(label, rx, rz - 15);
    };

    renderBot(bot1Pos.current, '#4a9eff', 'B1');
    renderBot(bot2Pos.current, '#ff6b6b', 'B2');

    requestRef.current = requestAnimationFrame(animate);
  };

  const shouldUseViewer = Boolean(viewerUrl) && !viewerError;
  
  useEffect(() => {
    if (shouldUseViewer) return undefined;
    requestRef.current = requestAnimationFrame(animate);
    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [trees, shouldUseViewer]);

  useEffect(() => {
    setViewerReady(false);
    setViewerError(false);
  }, [viewerUrl]);

  return (
    <div style={{ position: 'relative', width: WIDTH, height: HEIGHT, borderRadius: '12px', overflow: 'hidden', border: '2px solid var(--border)' }}>
      {shouldUseViewer ? (
        <>
          <iframe
            src={viewerUrl}
            title="Minecraft Live View"
            width="100%"
            height="100%"
            style={{ border: 'none' }}
            onLoad={() => setViewerReady(true)}
            onError={() => setViewerError(true)}
          />
          {!viewerReady && (
            <div
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(10, 20, 10, 0.7)',
                color: '#fff',
                fontWeight: 'bold',
              }}
            >
              Loading Minecraft world...
            </div>
          )}
        </>
      ) : (
        <canvas ref={canvasRef} width={WIDTH} height={HEIGHT} />
      )}
    </div>
  );
};

export default MinecraftMap;
