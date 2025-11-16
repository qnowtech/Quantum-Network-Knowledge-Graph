import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import '@neo4j-ndl/base/lib/neo4j-ds-styles.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

