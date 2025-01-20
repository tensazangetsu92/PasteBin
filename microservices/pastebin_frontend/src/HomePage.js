// src/components/HomePage.js
import React, { useState, useEffect } from 'react';
import { addPost, getPopularPosts } from './api/pastebin'; // Импортируем функции

function HomePage() {
  const [postName, setPostName] = useState('');
  const [postContent, setPostContent] = useState('');
  const [expiresAt, setExpiresAt] = useState('never');
  const [responseMessage, setResponseMessage] = useState('');
  const [popularPosts, setPopularPosts] = useState([]); // Для популярных постов

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
    const fetchPopularPosts = async () => {
      try {
        const posts = await getPopularPosts();
        setPopularPosts(posts);
      } catch (error) {
        setResponseMessage(`Ошибка при получении популярных постов: ${error.message}`);
      }
    };
    fetchPopularPosts();
  }, []); // Вызываем один раз при монтировании компонента

  const handleSubmit = async () => {
    if (!postContent.trim()) {
      setResponseMessage('Пост не может быть пустым.');
      return;
    }

    const selectedExpiration = expirationOptions[expiresAt];
    const expirationDate =
      selectedExpiration === null
        ? null
        : new Date(Date.now() + selectedExpiration * 1000).toISOString();

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
    <div style={{ padding: '20px' }}>
      <h1>Добавить новый пост</h1>
      <input
        type="text"
        placeholder="Введите название поста..."
        value={postName}
        onChange={(e) => setPostName(e.target.value)}
        style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
      />
      <textarea
        placeholder="Введите текст поста..."
        value={postContent}
        onChange={(e) => setPostContent(e.target.value)}
        rows="5"
        style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
      />
      <select
        value={expiresAt}
        onChange={(e) => setExpiresAt(e.target.value)}
        style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
      >
        {Object.keys(expirationOptions).map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
      <button onClick={handleSubmit} style={{ padding: '10px 20px' }}>
        Добавить
      </button>
      {responseMessage && <p>{responseMessage}</p>}

      <h2>Популярные посты</h2>
      {popularPosts.length === 0 ? (
        <p>Загрузка популярных постов...</p>
      ) : (
        <ul>
          {popularPosts.map((post, index) => (
            <li key={index}>
              <strong>{post.name}</strong> - {post.creation_date}
              <br />
              Размер текста: {post.text_size_kilobytes} KB
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default HomePage;
