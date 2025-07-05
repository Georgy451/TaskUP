import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="home-container">
      <h1>Добро пожаловать в TaskUP!</h1>
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '2rem' }}>
        <Link to="/login">
          <button>Войти</button>
        </Link>
        <Link to="/register">
          <button>Зарегистрироваться</button>
        </Link>
      </div>
    </div>
  );
};

export default Home;
