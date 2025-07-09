import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser } from "../api/user";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      const data = await loginUser(username, password);
      setSuccess("Вход выполнен! Токен: " + data.access_token);
      // Можно сохранить токен в localStorage, если нужно
      setTimeout(() => navigate("/features"), 500); // редирект через 0.5 сек
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="home-animated-bg">
      <div className="home-glass">
        <h2 className="home-title">Вход</h2>
        <form className="auth-form" onSubmit={handleSubmit}>
          <input type="text" placeholder="Имя пользователя" required className="auth-input" value={username} onChange={e => setUsername(e.target.value)} />
          <input type="password" placeholder="Пароль" required className="auth-input" value={password} onChange={e => setPassword(e.target.value)} />
          <button type="submit" className="home-btn">Войти</button>
        </form>
        {error && <div style={{color: 'red', marginTop: 8}}>{error}</div>}
        {success && <div style={{color: 'green', marginTop: 8}}>{success}</div>}
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
