import React, { useState } from 'react';
import { registerUser } from '../api/auth';

function RegisterPage() {
  const [username, setUsername] = useState('');  // Изменено с name на username
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  const handleRegister = async () => {
    try {
      const userData = { username, email, password };  // Используем username вместо name
      await registerUser(userData);
      setResponseMessage('Регистрация прошла успешно!');
    } catch (error) {
      setResponseMessage(error.message);
    }
  };

  return (
    <div>
      <h1>Регистрация</h1>
      <input
        type="text"
        placeholder="Введите имя пользователя"
        value={username}
        onChange={(e) => setUsername(e.target.value)}  // Обработчик для username
      />
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
      <button onClick={handleRegister}>Зарегистрироваться</button>
      {responseMessage && <p>{responseMessage}</p>}
    </div>
  );
}

export default RegisterPage;
