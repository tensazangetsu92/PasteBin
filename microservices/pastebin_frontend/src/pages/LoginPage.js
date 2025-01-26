import React, { useState } from 'react';
import { loginUser } from '../api/auth';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  const handleLogin = async () => {
    try {
      const userData = { email, password };
      await loginUser(userData);
      setResponseMessage('Вход выполнен успешно!');
    } catch (error) {
      setResponseMessage(error.message);
    }
  };

  return (
    <div>
      <h1>Вход</h1>
      <input
        type="email"
        placeholder="Введите email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
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
