import axios from 'axios';

const API_URL = 'http://localhost:8000/api'; // Адрес вашего API

const apiClient = axios.create({
  baseURL: API_URL,
});

// Интерсептор для добавления токена
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const getPostByShortKey = async (shortKey) => {
  try {
    const response = await apiClient.get(`get-post/${shortKey}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Не удалось получить пост');
  }
};

export const addPost = async (postData) => {
  try {
    const response = await apiClient.post(`/add-post`, postData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Неизвестная ошибка');
  }
};

export const getPopularPosts = async () => {
  try {
    const response = await apiClient.post(`/get-popular-posts`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Неизвестная ошибка');
  }
};
