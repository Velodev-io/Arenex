import React, { useEffect, useState } from 'react';

const MinecraftMap = ({ matchId, viewerUrl = null }) => {
  const [viewerReady, setViewerReady] = useState(false);
  const [viewerError, setViewerError] = useState(false);
  
  // Rewrite localhost to Mac Mini IP for the 3D Viewer since it's hosted there
  const resolvedViewerUrl = viewerUrl ? viewerUrl.replace(/localhost|127\.0\.0\.1/, '192.168.1.25') : null;

  useEffect(() => {
    setViewerReady(false);
    setViewerError(false);
  }, [resolvedViewerUrl]);

  return (
    <div 
      style={{ 
        position: 'relative', 
        width: '100%', 
        aspectRatio: '16/9', 
        minHeight: '400px',
        borderRadius: '12px', 
        overflow: 'hidden', 
        border: '2px solid var(--border)',
        backgroundColor: '#0a1015'
      }}
    >
      {(resolvedViewerUrl && !viewerError) ? (
        <>
          <iframe
            src={resolvedViewerUrl}
            title="Minecraft Live View"
            width="100%"
            height="100%"
            style={{ border: 'none', display: 'block' }}
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
                backgroundColor: 'rgba(10, 16, 21, 0.8)',
                color: '#fff',
                fontWeight: '500',
                fontSize: '1.1rem'
              }}
            >
              Loading 3D World...
            </div>
          )}
        </>
      ) : (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-secondary)',
            textAlign: 'center',
            padding: '2rem'
          }}
        >
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '1rem', opacity: 0.5 }}>
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
            <polyline points="2 17 12 22 22 17"></polyline>
            <polyline points="2 12 12 17 22 12"></polyline>
          </svg>
          <span style={{ fontSize: '1.2rem', fontWeight: 500, color: 'var(--text)' }}>
             Waiting for Minecraft Server...
          </span>
          <span style={{ fontSize: '0.9rem', marginTop: '0.5rem', opacity: 0.7 }}>
             The 3D stream will start automatically when the bots spawn in.
          </span>
        </div>
      )}
    </div>
  );
};

export default MinecraftMap;
