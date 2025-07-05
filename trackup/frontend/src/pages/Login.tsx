import React from "react";
import { Link } from "react-router-dom";

const Login = () => {
  return (
    <div className="auth-container">
      <h2>Вход</h2>
      <form>
        <input type="text" placeholder="Имя пользователя" required />
        <input type="password" placeholder="Пароль" required />
        <button type="submit">Войти</button>
      </form>
      <p>Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
    </div>
  );
};

export default Login;
