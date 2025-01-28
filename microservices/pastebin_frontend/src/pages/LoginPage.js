import React, { useState } from 'react';
import { loginUser } from '../api/auth';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  const handleLogin = async () => {
    try {
      const userData = { username, password };
      const response = await loginUser(userData);
      localStorage.setItem('access_token', response.access_token)
      setResponseMessage('Вход выполнен успешно!');
    } catch (error) {
      setResponseMessage(error.message);
    }
  };

  return (
    <div>
      <h1>Вход</h1>
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
      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default LoginPage;
