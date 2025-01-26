import axios from 'axios';

const API_URL = 'http://localhost:8000/api'; // Адрес вашего API


export const getPostByShortKey = async (shortKey) => {
  try {
    const response = await axios.get(`${API_URL}/${shortKey}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Не удалось получить пост');
  }
};
// Функция для добавления нового поста
export const addPost = async (postData) => {
  try {
    const response = await axios.post(`${API_URL}/add_post`, postData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Неизвестная ошибка');
  }
};
// Функция для получения популярных постов
export const getPopularPosts = async () => {
  try {
    const response = await axios.post(`${API_URL}/get_popular_posts`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Неизвестная ошибка');
  }
};
