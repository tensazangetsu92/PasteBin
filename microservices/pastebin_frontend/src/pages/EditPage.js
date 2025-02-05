import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPost, updatePost } from '../api/posts';

function EditPostPage() {
  const { shortKey } = useParams();
  const navigate = useNavigate();
  const [postName, setPostName] = useState('');
  const [postContent, setPostContent] = useState('');
  const [expiresAt, setExpiresAt] = useState('');
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

  const fetchPost = async () => {
    try {
      console.log(shortKey);
      const post = await getPost(shortKey);
      setPostName(post.name);
      setPostContent(post.text);
      setExpiresAt(post.expires_at || 'never');
    } catch (error) {
      console.log(error);
      setResponseMessage('Ошибка загрузки поста');
    }
  };

  useEffect(() => {
    fetchPost(); // Загружаем пост при монтировании компонента
  }, [shortKey]);

  const handleUpdate = async () => {
    if (!postContent.trim()) {
      setResponseMessage('Пост не может быть пустым.');
      return;
    }

    const selectedExpiration = expirationOptions[expiresAt];
    const expirationDate = selectedExpiration
      ? new Date(Date.now() + selectedExpiration * 1000).toISOString()
      : null;

    try {
      await updatePost(shortKey, {
        name: postName,
        text: postContent,
        expires_at: expiresAt
      });

      setResponseMessage('Пост успешно обновлен!');

      // После обновления поста вызываем fetchPost для обновления данных
      fetchPost();

      setTimeout(() => navigate('/'), 1000);
    } catch (error) {
      setResponseMessage(`Ошибка: ${error.message}`);
    }
  };

  return (
    <div style={{ width: '60%', margin: '20px', padding: '10px', display: 'flex', flexDirection: 'column', color: '#dddddd'}}>
      <h2>Редактирование поста</h2>
      <textarea
        value={postContent}
        onChange={(e) => setPostContent(e.target.value)}
        rows="5"
        style={{ width: '95%', height: '240px', marginBottom: '10px', padding: '8px', backgroundColor: '#2b2b2b', border: '1px solid #333333', color: '#dddddd' }}
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

      <input
        type="text"
        value={postName}
        onChange={(e) => setPostName(e.target.value)}
        style={{ width: '200px', marginBottom: '10px', padding: '8px', backgroundColor: '#2b2b2b', border: '1px solid #333333', color: '#dddddd' }}
      />
      <button onClick={handleUpdate} style={{ padding: '10px 20px', backgroundColor: '#2b2b2b', color: '#dddddd', cursor: 'pointer', border: '1px solid #333333' }}>
        Сохранить
      </button>
      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default EditPostPage;
