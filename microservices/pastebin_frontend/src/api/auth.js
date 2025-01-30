// src/api/auth.js
import apiClient from './axiosConfig';

export const registerUser = async (userData) => {
  try {
    const response = await apiClient.post(`/register`, userData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Ошибка регистрации');
  }
};

export const loginUser = async (userData) => {
  try {
    const response = await apiClient.post(`/login`, userData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Ошибка входа');
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await apiClient.get('/get-current-user'); // Запрос на сервер для получения текущего пользователя
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Ошибка получения данных о пользователе');
  }
};
