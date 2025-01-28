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


export const getCurrentUser = async () => {
  try {
    const response = await axios.get(`${API_URL}/get-current-user`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    });
    return response.data; // Например: { name: "User", id: 1 }
  } catch {
    return null;
  }
};
