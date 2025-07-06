import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="home-animated-bg">
      <div className="home-glass">
        <h1 className="home-title">
          Добро пожаловать в <span className="brand">TaskUP</span>!
        </h1>
        <p className="home-subtitle">Управляйте задачами легко и современно</p>
        <div className="home-btns">
          <Link to="/login">
            <button className="home-btn">Войти</button>
          </Link>
          <Link to="/register">
            <button className="home-btn">Зарегистрироваться</button>
          </Link>
        </div>
      </div>
      <ul className="bg-bubbles">
        {Array.from({ length: 10 }).map((_, i) => (
          <li key={i}></li>
        ))}
      </ul>
    </div>
  );
};

export default Home;
