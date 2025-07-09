import { useState } from "react";
import { Link } from "react-router-dom";
import { registerUser } from "../api/user";

const Register = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (password !== repeatPassword) {
      setError("Пароли не совпадают");
      return;
    }
    try {
      await registerUser(username, email, password);
      setSuccess("Регистрация успешна! Теперь войдите.");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="home-animated-bg">
      <div className="home-glass">
        <h2 className="home-title">Регистрация</h2>
        <form className="auth-form" onSubmit={handleSubmit}>
          <input type="text" placeholder="Имя пользователя" required className="auth-input" value={username} onChange={e => setUsername(e.target.value)} />
          <input type="email" placeholder="Email" required className="auth-input" value={email} onChange={e => setEmail(e.target.value)} />
          <input type="password" placeholder="Пароль" required className="auth-input" value={password} onChange={e => setPassword(e.target.value)} />
          <input type="password" placeholder="Повторите пароль" required className="auth-input" value={repeatPassword} onChange={e => setRepeatPassword(e.target.value)} />
          <button type="submit" className="home-btn">Зарегистрироваться</button>
        </form>
        {error && <div style={{color: 'red', marginTop: 8}}>{error}</div>}
        {success && <div style={{color: 'green', marginTop: 8}}>{success}</div>}
        <p className="auth-link">Уже есть аккаунт? <Link to="/login">Войти</Link></p>
      </div>
      <ul className="bg-bubbles">
        {Array.from({ length: 10 }).map((_, i) => (
          <li key={i}></li>
        ))}
      </ul>
    </div>
  );
};

export default Register;
