import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// 自动重定向到管理员页面，除非已经设置了跳过重定向标志
if ((window.location.pathname === '/' || window.location.pathname === '/index.html') && 
    localStorage.getItem('skipRedirect') !== 'true') {
  window.location.href = '/admin.html';
} else {
  // 如果是从管理员页面跳转来的，清除标志以便下次访问时还是默认到管理员页面
  localStorage.removeItem('skipRedirect');
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);