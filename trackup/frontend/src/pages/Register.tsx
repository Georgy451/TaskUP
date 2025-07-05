import React from "react";
import { Link } from "react-router-dom";

const Register = () => {
  return (
    <div className="auth-container">
      <h2>Регистрация</h2>
      <form>
        <input type="text" placeholder="Имя пользователя" required />
        <input type="password" placeholder="Пароль" required />
        <input type="password" placeholder="Повторите пароль" required />
        <button type="submit">Зарегистрироваться</button>
      </form>
      <p>Уже есть аккаунт? <Link to="/login">Войти</Link></p>
    </div>
  );
};

export default Register;
