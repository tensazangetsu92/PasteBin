import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { loginUser } from '../api/auth';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const navigate = useNavigate();

  const { loginWithRedirect, isAuthenticated, user } = useAuth0(); // Доступ к Auth0

  const handleLogin = async () => {
    try {
      const userData = { username, password };
      await loginUser(userData);
      setResponseMessage('Вход выполнен успешно!');

      // Получаем сохранённый маршрут
      const redirectPath = localStorage.getItem('redirect_after_login') || '/';
      localStorage.removeItem('redirect_after_login'); // Удаляем его, чтобы не было повторных редиректов
      navigate(redirectPath); // Перенаправляем пользователя
    } catch (error) {
      setResponseMessage(error.message);
    }
  };

  const handleAuth0Login = () => {
    loginWithRedirect();
  };

  return (
    <div>
      <h1 style={{color: '#dddddd'}}>Вход</h1>
      <input
        type="text"
        placeholder="Введите имя пользователя"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Введите пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>Войти</button>

      {/* Кнопка для входа через Auth0 */}
      <button onClick={handleAuth0Login}>Войти через Auth0</button>

      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default LoginPage;
