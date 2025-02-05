import apiClient from './axiosConfig';

export const addPost = async (postData) => {
  try {
    const response = await apiClient.post(`/add-post`, postData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Неизвестная ошибка');
  }
};


export const getPost = async (shortKey) => {
  try {
    const response = await apiClient.get(`/get-post/${shortKey}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Не удалось получить пост');
  }
};

export const updatePost = async (shortKey, postData) => {
  try {
    const response = await apiClient.patch(`/update-post/${shortKey}`, postData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Не удалось обновить пост');
  }
}



export const deletePost = async (shortKey) => {
  try {
    const response = await apiClient.delete(`/delete-post/${shortKey}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Ошибка при удалении поста');
  }
};

export const getPopularPosts = async () => {
  try {
    const response = await apiClient.get(`/get-popular-posts`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Неизвестная ошибка');
  }
};

export const getUserPosts = async () => {
  try {
    const response = await apiClient.get(`/get-user-posts`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Не удалось получить посты пользователя');
  }
};