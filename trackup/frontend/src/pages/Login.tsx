import { Link } from "react-router-dom";

const Login = () => {
  return (
    <div className="home-animated-bg">
      <div className="home-glass">
        <h2 className="home-title">Вход</h2>
        <form className="auth-form">
          <input type="text" placeholder="Имя пользователя" required className="auth-input" />
          <input type="password" placeholder="Пароль" required className="auth-input" />
          <button type="submit" className="home-btn">Войти</button>
        </form>
        <p className="auth-link">Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
      </div>
      <ul className="bg-bubbles">
        {Array.from({ length: 10 }).map((_, i) => (
          <li key={i}></li>
        ))}
      </ul>
    </div>
  );
};

export default Login;
