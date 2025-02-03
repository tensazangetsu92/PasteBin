import React, { useState, useEffect } from 'react';
import { addPost, getPopularPosts, getUserPosts } from '../api/posts';
import { Link, useNavigate } from 'react-router-dom';
import { getCurrentUser } from '../api/auth';

function HomePage() {
  const [postName, setPostName] = useState('');
  const [postContent, setPostContent] = useState('');
  const [expiresAt, setExpiresAt] = useState('never');
  const [responseMessage, setResponseMessage] = useState('');
  const [popularPosts, setPopularPosts] = useState([]);
  const [userPosts, setUserPosts] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const navigate = useNavigate();

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

  // Функция для получения данных о текущем пользователе
  const fetchCurrentUser = async () => {
  try {
    const userData = await getCurrentUser(); // Получаем данные пользователя
    setCurrentUser(userData);
  } catch (error) {
    console.error('Ошибка при получении пользователя:', error);
    setCurrentUser(null);
  }
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
    fetchCurrentUser(); // Получаем данные о текущем пользователе
  }, []);

  useEffect(() => {
    const fetchUserPosts = async () => {
  try {
    if (currentUser) {
      const posts = await getUserPosts();
      setUserPosts(posts);
    }
  } catch (error) {
    console.error('Ошибка при загрузке постов пользователя:', error);
  }
};

  if (currentUser) {
    fetchUserPosts(); // Загружаем посты после получения данных о пользователе
  }
}, [currentUser]);

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
    <>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          padding: '10px 20px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
        }}
      >
        <h1 style={{ margin: 0 }}>PasteBin</h1>
        <div>
          {currentUser ? (
            <div>
              <span>{currentUser.username}</span> {/* Отображаем имя пользователя */}
              <button
                onClick={() => {
                  localStorage.removeItem('access_token'); // Удаляем токен
                  setCurrentUser(null); // Сбрасываем состояние
                }}
                style={{ marginLeft: '10px', padding: '8px 16px' }}
              >
                Выйти
              </button>
            </div>
          ) : (
            <>
              <button
                onClick={() => navigate('/login')}
                style={{ marginRight: '10px', padding: '8px 16px' }}
              >
                Логин
              </button>
              <button onClick={() => navigate('/register')} style={{ padding: '8px 16px' }}>
                Регистрация
              </button>
            </>
          )}
        </div>
      </div>

      <div style={{ display: 'flex' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', margin: '20px', backgroundColor: '#f9f9f9', padding: '10px' }}>
          <textarea
            placeholder="Введите текст поста..."
            value={postContent}
            onChange={(e) => setPostContent(e.target.value)}
            rows="5"
            style={{ width: '1000px', height: '240px', marginBottom: '10px', padding: '8px' }}
          />
          <input
            type="text"
            placeholder="Введите название поста..."
            value={postName}
            onChange={(e) => setPostName(e.target.value)}
            style={{ width: '200px', marginBottom: '10px', padding: '8px' }}
          />
          <select
            value={expiresAt}
            onChange={(e) => setExpiresAt(e.target.value)}
            style={{ width: '200px', marginBottom: '10px', padding: '8px' }}
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
        </div>

        <div style={{ flex: 1, margin: '20px', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
          <h2>Популярные посты</h2>
          {popularPosts && popularPosts.posts ? (
            popularPosts.posts.length === 0 ? (
              <p>Загрузка популярных постов...</p>
            ) : (
              <ul>
                {popularPosts.posts.map((post, index) => (
                  <li key={index} style={{ marginBottom: '10px' }}>
                    <Link to={`/${post.short_key}`}>
                      <strong>{post.name}</strong>
                    </Link>
                    <br />
                    Размер текста: {post.text_size_kilobytes} KB
                    <br />
                    Создан: {post.created_at}
                  </li>
                ))}
              </ul>
            )
          ) : (
            <p>Загрузка популярных постов...</p>
          )}
        </div>
      </div>

      <div style={{ margin: '20px', padding: '10px', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
      <h2>Мои посты</h2>
      {userPosts.length === 0 ? (
        <p>У вас пока нет постов.</p>
      ) : (
        <ul>
          {userPosts.map((post) => (
            <li key={post.id} style={{ marginBottom: '10px' }}>
              <Link to={`/${post.short_key}`}>
                <strong>{post.name}</strong>
              </Link>
              <br />
              Просмотры: {post.views}
              <br />
              Создан: {post.created_at}
            </li>
          ))}
        </ul>
      )}
    </div>


    </>
  );
}

export default HomePage;
