import React, { useState, useEffect } from 'react';
import { getPopularPosts, getUserPosts } from '../api/posts';
import { Link, useNavigate } from 'react-router-dom';
import { getCurrentUser, logoutUser } from '../api/auth';

function Layout({ children }) {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);
  const [popularPosts, setPopularPosts] = useState([]);
  const [userPosts, setUserPosts] = useState([]);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const user = await getCurrentUser();
        setCurrentUser(user);
      } catch {
        setCurrentUser(null);
      }
    };

    const fetchPopularPosts = async () => {
      try {
        const posts = await getPopularPosts();
        console.log(posts);
        setPopularPosts(posts);
      } catch (error) {
        console.error('Ошибка при получении популярных постов:', error);
      }
    };

    fetchUserData();
    fetchPopularPosts();
  }, []);

  useEffect(() => {
    const fetchUserPosts = async () => {
      if (currentUser) {
        try {
          const posts = await getUserPosts();
          console.log(posts);
          setUserPosts(posts);
        } catch (error) {
          console.error('Ошибка загрузки постов пользователя:', error);
        }
      }
    };

    fetchUserPosts();
  }, [currentUser]);

  const handleLogout = async () => {
    try {
      await logoutUser();
      setCurrentUser(null);
      window.location.reload();
    } catch (error) {
      console.error('Ошибка при выходе:', error);
    }
  };

  return (
    <>
      <div style={{ backgroundColor: '#2b2b2b'}}>

      {/* Верхняя панель */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 20px', backgroundColor: '#2a2a2a', borderRadius: '8px' }}>
        <h1 style={{ margin: 0 }}>
          <Link to="/" style={{ color: 'black', textDecoration: 'none' }}>
            <strong style={{ color: '#ffffff'}}>PasteBin</strong>
          </Link>
        </h1>
        <div>
          {currentUser ? (
            <div>
              <span>{currentUser.username}</span>
              <button onClick={handleLogout} style={{ marginLeft: '10px', padding: '8px 16px' }}>
                Выйти
              </button>
            </div>
          ) : (
            <>
              <button onClick={() => navigate('/login')} style={{ marginRight: '10px', padding: '8px 16px' }}>
                Логин
              </button>
              <button onClick={() => navigate('/register')} style={{ padding: '8px 16px' }}>
                Регистрация
              </button>
            </>
          )}
        </div>
      </div>

      {/* Контент страницы */}
      <div style={{ padding: '20px', marginRight: '10%', marginLeft: '10%', display: 'flex' , backgroundColor: '#252525'}}>
        <div style={{ width: '70%' }}>{children}</div>
        <div style={{ width: '30%' }}>
          {/* Популярные посты */}
          <div style={{ flex: 1, margin: '20px', padding: '10px'}}>
            <h2 style={{ color: '#dddddd' }}>Популярные посты</h2>
            {popularPosts && popularPosts.posts ? (
              popularPosts.posts.length === 0 ? (
                <p>Загрузка популярных постов...</p>
              ) : (
                <ul>
                  {popularPosts.posts.map((post, index) => (
                    <li key={index} style={{ marginBottom: '10px', color: '#999999' }}>
                      <Link to={`/${post.short_key}`} style={{textDecoration: 'none'}}>
                        <strong style={{color: '#3a83d2'}}>{post.name}</strong>
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

          {/* Мои посты */}
          {currentUser && userPosts.posts && (
            <div style={{ margin: '20px', padding: '10px'}}>
              <h2 style = {{color: '#dddddd'}}>Мои посты</h2>
              <ul>
                {userPosts.posts.map((post) => (
                  <li key={post.id} style={{ marginBottom: '10px', color: '#999999' }}>
                    <Link to={`/${post.short_key}`} style={{textDecoration: 'none'}}>
                      <strong style={{ color: '#3a83d2'}}>{post.name}</strong>
                    </Link>
                    <br />
                    Просмотры: {post.views}
                    <br />
                    Создан: {post.created_at}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      </div>
    </>
  );
}

export default Layout;
