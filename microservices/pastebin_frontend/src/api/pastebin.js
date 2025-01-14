import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'; // Укажите URL вашего бэкенда

export const getTextByShortKey = async (shortKey) => {
  try {
    const response = await axios.get(`${API_URL}/${shortKey}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching text:', error);
    throw error;
  }
};

export const createText = async (textData) => {
  try {
    const response = await axios.post(`${API_URL}/`, textData);
    return response.data;
  } catch (error) {
    console.error('Error creating text:', error);
    throw error;
  }
};
