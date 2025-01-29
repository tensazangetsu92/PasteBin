// src/api/axiosConfig.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // Разрешаем отправку куков
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерсептор запроса
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Интерсептор ответа
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
