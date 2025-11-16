import React from 'react';
import GraphVisualization from './components/GraphVisualization';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Quantum Network Knowledge Graph</h1>
      </header>
      <main className="App-main">
        <GraphVisualization />
      </main>
    </div>
  );
}

export default App;

