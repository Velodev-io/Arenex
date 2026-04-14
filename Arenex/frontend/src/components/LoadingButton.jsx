import React from 'react';

const LoadingButton = ({ 
  children, 
  loading = false, 
  onClick, 
  disabled = false, 
  style = {},
  className = ""
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`loading-button ${loading ? 'loading' : ''} ${className}`}
      style={{ ...style }}
    >
      {loading && <div className="btn-spinner" />}
      <span>{loading ? 'PROCESSING...' : children}</span>
    </button>
  );
};

export const FullPageLoader = ({ message = "LOADING ARENA..." }) => (
  <div className="loader-container" style={{ minHeight: '60vh' }}>
    <div className="cyber-spinner" />
    <div className="glow-text">{message}</div>
  </div>
);

export default LoadingButton;
