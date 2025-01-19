import React, { useState } from 'react';
import axios from 'axios';

function HomePage() {
  const [postName, setPostName] = useState(''); // Для названия поста
  const [postContent, setPostContent] = useState(''); // Для текста поста
  const [expiresAt, setExpiresAt] = useState('never'); // Для времени истечения
  const [responseMessage, setResponseMessage] = useState('');

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
      await axios.post('http://localhost:8000/api/add_post', {
        name: postName || 'Untitled', // Если название пустое, использовать "Untitled"
        text: postContent,
        expires_at: expirationDate, // Преобразовать время истечения в ISO формат
      });
      setResponseMessage('Пост успешно добавлен!');
      setPostName('');
      setPostContent('');
      setExpiresAt('never');
    } catch (error) {
      const errorMessage = error.response
    ? JSON.stringify(error.response.data, null, 2)
    : 'Неизвестная ошибка';
  console.error('Ошибка:', errorMessage);
  setResponseMessage(`Ошибка: ${errorMessage}`);
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
    </div>
  );
}

export default HomePage;
