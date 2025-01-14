import React, { useState, useEffect } from 'react';
import { getTextByShortKey, createText } from './api/pastebin'; // Сервис для API

const App = () => {
  const [text, setText] = useState('');
  const [shortKey, setShortKey] = useState('exampleKey');

  useEffect(() => {
    // Получить текст по ключу
    const fetchText = async () => {
      try {
        const data = await getTextByShortKey(shortKey);
        setText(data.text);
      } catch (error) {
        console.error('Error fetching text:', error);
      }
    };

    fetchText();
  }, [shortKey]);

  const handleCreateText = async () => {
    try {
      const newText = { text: 'Hello, Pastebin!', name: 'Example', expires_at: new Date() };
      const response = await createText(newText);
      console.log('Text created:', response);
    } catch (error) {
      console.error('Error creating text:', error);
    }
  };

  return (
    <div>
      <h1>Pastebin</h1>
      <p>Text: {text}</p>
      <button onClick={handleCreateText}>Create Text</button>
    </div>
  );
};

export default App;
