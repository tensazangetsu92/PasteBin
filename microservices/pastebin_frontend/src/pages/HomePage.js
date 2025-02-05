import React, { useState, useEffect } from 'react';
import { addPost, getPopularPosts, getUserPosts } from '../api/posts';
import { getCurrentUser } from '../api/auth';

function HomePage() {
  const [postName, setPostName] = useState('');
  const [postContent, setPostContent] = useState('');
  const [expiresAt, setExpiresAt] = useState('never');
  const [responseMessage, setResponseMessage] = useState('');
  const [currentUser, setCurrentUser] = useState(null);

  const expirationOptions = {
    never: null,
    'burn after read': 0,
    '10 minutes': 10 * 60,
    '1 hour': 60 * 60,
    '1 day': 24 * 60 * 60,
    '1 week': 7 * 24 * 60 * 60,
    '2 weeks': 14 * 24 * 60 * 60,
    '1 month': 30 * 24 * 60 * 60,
    '6 months': 180 * 24 * 60 * 60,
    '1 year': 365 * 24 * 60 * 60,
  };

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const user = await getCurrentUser();
        setCurrentUser(user);
      } catch {
        setCurrentUser(null);
      }
    };
    fetchUserData();
  }, []);

  const handleSubmit = async () => {
    if (!postContent.trim()) {
      setResponseMessage('Пост не может быть пустым.');
      return;
    }
    const selectedExpiration = expirationOptions[expiresAt];
    const expirationDate = selectedExpiration
      ? new Date(Date.now() + selectedExpiration * 1000).toISOString()
      : null;
    try {
      await addPost({
        name: postName || 'Untitled',
        text: postContent,
        expires_at: expirationDate,
      });
      setResponseMessage('Пост успешно добавлен!');
      setPostName('');
      setPostContent('');
      setExpiresAt('never');
    } catch (error) {
      setResponseMessage(`Ошибка: ${error.message}`);
    }
  };

  return (
    <div style={{ width: '60%', margin: '20px', padding: '10px', display: 'flex', flexDirection: 'column' }}>
      <textarea
        placeholder="Введите текст поста..."
        value={postContent}
        onChange={(e) => setPostContent(e.target.value)}
        rows="5"
        style={{ width: '95%', height: '240px', marginBottom: '10px', padding: '8px', resize: 'none', backgroundColor: '#2b2b2b', radiusColor: '#333333', outline: 'none',
         border: '1px solid #333333' }}
      />
      <input
        type="text"
        placeholder="Введите название поста..."
        value={postName}
        onChange={(e) => setPostName(e.target.value)}
        style={{ width: '200px', marginBottom: '10px', padding: '8px', backgroundColor: '#2b2b2b', outline: 'none', border: '1px solid #333333' }}
      />
      <select
        value={expiresAt}
        onChange={(e) => setExpiresAt(e.target.value)}
        style={{ width: '200px', marginBottom: '10px', padding: '8px', backgroundColor: '#2b2b2b', outline: 'none', border: '1px solid #333333', color: '#dddddd' }}
      >
        {Object.keys(expirationOptions).map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
      <button onClick={handleSubmit} style={{ padding: '10px 20px', backgroundColor: '#2b2b2b', color: '#f7f7ea',  cursor: 'pointer', border: '1px solid #333333' }}>
        Добавить
      </button>
      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default HomePage;
