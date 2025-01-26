import axios from 'axios';

const API_URL = 'http://localhost:8000/api'; // Адрес вашего API

// Регистрация пользователя
export const registerUser = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/register`, userData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Ошибка регистрации');
  }
};

// Логин пользователя
export const loginUser = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/login`, userData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Ошибка входа');
  }
};
