import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getCurrentUser, logoutUser } from '../api/auth';

function Layout({ children }) {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = React.useState(null);

  React.useEffect(() => {
    const fetchUser = async () => {
      try {
        const user = await getCurrentUser();
        setCurrentUser(user);
      } catch {
        setCurrentUser(null);
      }
    };
    fetchUser();
  }, []);

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
      {/* Верхняя панель */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px 20px',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
      }}>
        <h1 style={{ margin: 0 }}>
          <Link to={`/`} style={{ color: 'black', textDecoration: 'none' }}>
            <strong>PasteBin</strong>
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
      <div style={{ padding: '20px', marginRight: '10%', marginLeft: '10%'  }}>
        {children}
      </div>
    </>
  );
}

export default Layout;
