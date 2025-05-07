import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');

  const handleQuery = async () => {
    setError('');
    setAnswer('');
    try {
      const response = await axios.post('http://localhost:5000/query', { query: `${query}的宿舍费用` });
      setAnswer(response.data.answer);
    } catch (err) {
      setError('查询失败，请稍后重试');
      console.error(err);
    }
  };

  const goToAdmin = () => {
    window.location.href = '/admin.html';
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '20px' }}>宿舍费用查询</h1>
      <div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="请输入您的名字"
          style={{ width: '100%', padding: '10px', marginBottom: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <button
          onClick={handleQuery}
          style={{ width: '100%', padding: '10px', backgroundColor: '#4299E1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          查询
        </button>
        {answer && (
          <div style={{ marginTop: '20px', padding: '15px', backgroundColor: 'white', borderRadius: '4px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <p>{answer}</p>
          </div>
        )}
        {error && (
          <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#FED7D7', color: '#9B2C2C', borderRadius: '4px' }}>
            <p>{error}</p>
          </div>
        )}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <a 
            href="#" 
            onClick={goToAdmin}
            style={{ color: '#4299E1', textDecoration: 'none' }}
          >
            切换到管理员界面
          </a>
        </div>
      </div>
    </div>
  );
};

export default App;