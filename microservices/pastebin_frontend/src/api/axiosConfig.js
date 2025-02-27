// src/api/axiosConfig.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/',
  withCredentials: true, // Разрешаем отправку куков
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const currentPath = window.location.pathname + window.location.search; // Сохраняем текущий URL
      localStorage.setItem('redirect_after_login', currentPath);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);


export default apiClient;
