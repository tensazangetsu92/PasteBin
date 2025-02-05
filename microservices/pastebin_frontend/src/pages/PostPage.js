import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPost, deletePost } from '../api/posts';

function PostPage() {
  const { shortKey } = useParams();
  const [post, setPost] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPost = async () => {
      try {
        console.log(shortKey);
        const postData = await getPost(shortKey);
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
    <div style={{ padding: '20px', fontSize: '20px', color: '#dddddd' }}>
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
        style={{ marginTop: '20px', padding: '30px', background: '#373737', color: 'white', borderRadius: '5px', cursor: 'pointer', border: '1px solid #333333'}}
      >
        <strong>Удалить пост</strong>
      </button>

    <button
      onClick={() => navigate(`/edit/${shortKey}`)}
      style={{ marginTop: '20px', padding: '30px', background: '#555555', color: 'white', borderRadius: '5px', cursor: 'pointer', border: '1px solid #333333', marginRight: '10px' }}
    >
      <strong >Редактировать пост</strong>
    </button>

    </div>
  );
}

export default PostPage;
