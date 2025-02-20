import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Auth0Provider } from '@auth0/auth0-react';

import HomePage from './pages/HomePage'; // Указан новый путь
import PostPage from './pages/PostPage'; // Путь к компоненту PostPage
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import EditPage from './pages/EditPage'
import Layout from './components/Layout';



function App() {
  return (
    <Auth0Provider
      domain={"dev-0yikj7u0gbje0gor.us.auth0.com"}
      clientId={"k32VuREqw6RlMXsOgMK1EJwZ6T3rZkjW"}
      authorizationParams={{ redirect_uri: window.location.origin }}
    >
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/:shortKey" element={<PostPage />} />
            <Route path="/edit/:shortKey" element={<EditPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/login" element={<LoginPage />} />
          </Routes>
        </Layout>
      </Router>
    </Auth0Provider>
  );
}

export default App;
