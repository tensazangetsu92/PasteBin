import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage'; // Указан новый путь
import PostPage from './pages/PostPage'; // Путь к компоненту PostPage

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/:shortKey" element={<PostPage />} />
      </Routes>
    </Router>
  );
}

export default App;
