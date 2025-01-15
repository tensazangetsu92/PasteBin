import React, { useState } from 'react';
import axios from 'axios';

function HomePage() {
  const [postContent, setPostContent] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  const handleSubmit = async () => {
    if (!postContent.trim()) {
      setResponseMessage('Пост не может быть пустым.');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/api/posts', {
        content: postContent,
      });
      setResponseMessage('Пост успешно добавлен!');
      setPostContent(''); // Очистить поле после успешной отправки
    } catch (error) {
      setResponseMessage('Ошибка при добавлении поста.');
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Добавить новый пост</h1>
      <textarea
        placeholder="Введите текст поста..."
        value={postContent}
        onChange={(e) => setPostContent(e.target.value)}
        rows="5"
        style={{ width: '100%', marginBottom: '10px' }}
      />
      <button onClick={handleSubmit} style={{ padding: '10px 20px' }}>
        Добавить
      </button>
      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default HomePage;
