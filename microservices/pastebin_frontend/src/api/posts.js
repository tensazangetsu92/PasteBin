import apiClient from './axiosConfig';

export const getPostByShortKey = async (shortKey) => {
  try {
    const response = await apiClient.get(`/get-post/${shortKey}`);
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

export const getUserPosts = async () => {
  try {
    const response = await apiClient.post(`/get-user-posts`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Не удалось получить посты пользователя');
  }
};