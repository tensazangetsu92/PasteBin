import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPostByShortKey, deletePost } from '../api/posts';

function PostPage() {
  const { shortKey } = useParams();
  const [post, setPost] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPost = async () => {
      try {
        console.log(shortKey);
        const postData = await getPostByShortKey(shortKey);
        setPost(postData);
      } catch (err) {
        setError(`Ошибка загрузки поста: ${err.message}`);
      }
    };

    fetchPost();
  }, [shortKey]);

  const handleDelete = async () => {
    try {
      await deletePost(shortKey);
      navigate('/'); // Перенос на главную страницу после удаления
    } catch (err) {
      setError(`Ошибка при удалении поста: ${err.message}`);
    }
  };

  if (error) return <p>{error}</p>;
  if (!post) return <p>Загрузка...</p>;

  return (
    <div style={{ padding: '20px', fontSize: '20px' }}>
      <h1>{post.name}</h1>
      <p><strong>Дата создания:</strong> {new Date(post.created_at).toLocaleString()}</p>
      {post.expires_at && (
        <p><strong>Истекает:</strong> {new Date(post.expires_at).toLocaleString()}</p>
      )}
      <p><strong>Просмотров:</strong> {post.views}</p>
      <div style={{ marginTop: '20px', whiteSpace: 'pre-wrap', fontSize: '40px' }}>
        {post.text}
      </div>
      <button
        onClick={handleDelete}
        style={{ marginTop: '20px', padding: '30px', background: '#373737', color: 'white', borderRadius: '5px', cursor: 'pointer' }}
      >
        <strong>Удалить пост</strong>
      </button>
    </div>
  );
}

export default PostPage;
