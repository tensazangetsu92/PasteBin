import React, { useState } from 'react';
import axios from 'axios';

function HomePage() {
  const [postName, setPostName] = useState(''); // Для названия поста
  const [postContent, setPostContent] = useState(''); // Для текста поста
  const [expiresAt, setExpiresAt] = useState(''); // Для даты истечения
  const [responseMessage, setResponseMessage] = useState('');

  const handleSubmit = async () => {
    if (!postContent.trim()) {
      setResponseMessage('Пост не может быть пустым.');
      return;
    }

    try {
      await axios.post('http://localhost:8000/api/', {
        name: postName || 'Untitled', // Если название пустое, использовать "Untitled"
        text: postContent,
        expires_at: expiresAt || null, // Если дата не указана, оставить null
      });
      setResponseMessage('Пост успешно добавлен!');
      setPostName('');
      setPostContent('');
      setExpiresAt('');
    } catch (error) {
      setResponseMessage(`Ошибка: ${error.response?.data?.detail || 'Неизвестная ошибка'}`);
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
      <input
        type="datetime-local"
        value={expiresAt}
        onChange={(e) => setExpiresAt(e.target.value)}
        style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
      />
      <button onClick={handleSubmit} style={{ padding: '10px 20px' }}>
        Добавить
      </button>
      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default HomePage;
