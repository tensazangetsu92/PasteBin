import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getPostByShortKey } from '../api/pastebin'; // Предполагается, что эта функция уже есть

function PostPage() {
  const { shortKey } = useParams();
  const [post, setPost] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const postData = await getPostByShortKey(shortKey);
        setPost(postData);
      } catch (err) {
        setError(`Ошибка загрузки поста: ${err.message}`);
      }
    };

    fetchPost();
  }, [shortKey]);

  if (error) return <p>{error}</p>;
  if (!post) return <p>Загрузка...</p>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>{post.name}</h1>
      <p><strong>Дата создания:</strong> {new Date(post.created_at).toLocaleString()}</p>
      {post.expires_at && (
        <p><strong>Истекает:</strong> {new Date(post.expires_at).toLocaleString()}</p>
      )}
      <div style={{ marginTop: '20px', whiteSpace: 'pre-wrap' }}>
        {post.text}
      </div>
    </div>
  );
}

export default PostPage;
