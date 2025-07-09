import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createRoom } from "../api/rooms";

const MODES = [
  { value: "classic", label: "Классический" },
  { value: "fast", label: "Быстрый" },
  { value: "custom", label: "Пользовательский" },
];

const Features = () => {
  const [showModal, setShowModal] = useState(false);
  const [roomName, setRoomName] = useState("");
  const [mode, setMode] = useState(MODES[0].value);
  const [roomCode, setRoomCode] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const navigate = useNavigate();

  const handleCreate = () => {
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setRoomName("");
    setMode(MODES[0].value);
    setRoomCode("");
  };

  const handleModalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // creator можно заменить на имя пользователя из auth, если есть
      await createRoom(roomName, "creator", mode);
      setShowModal(false);
      setRoomName("");
      setMode(MODES[0].value);
      setRoomCode("");
      navigate("/game");
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleJoin = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`Подключиться к комнате: ${joinCode} (реализуйте API-запрос)`);
  };

  return (
    <div className="features-bg">
      <div className="features-glass">
        <h2 className="features-title">Игровые комнаты</h2>
        <button className="home-btn create-room-animated" onClick={handleCreate}>
          <span style={{ display: "inline-block", transition: "transform 0.2s" }}>
            &#10010;
          </span>{" "}
          Создать комнату
        </button>
        <form className="auth-form join-room-animated" onSubmit={handleJoin}>
          <input
            className="auth-input"
            type="text"
            placeholder="Код комнаты"
            value={joinCode}
            onChange={e => setJoinCode(e.target.value)}
            required
          />
          <button className="home-btn" type="submit">
            <span style={{ display: "inline-block", transition: "transform 0.2s" }}>
              &#128273;
            </span>{" "}
            Подключиться к комнате
          </button>
        </form>
        <div className="profile-link-bar-bottom">
          <button className="profile-link-btn" onClick={() => window.location.href = '/profile'}>
            <span role="img" aria-label="profile" style={{fontSize: '1.3em', marginRight: 6}}>&#128100;</span>
            Профиль
          </button>
        </div>
      </div>
      {showModal && (
        <div className="modal-bg" onClick={handleModalClose}>
          <div className="modal-window" onClick={e => e.stopPropagation()}>
            <h3 className="modal-title">Создать комнату</h3>
            <form className="modal-form" onSubmit={handleModalSubmit}>
              <input
                className="auth-input"
                type="text"
                placeholder="Название комнаты"
                value={roomName}
                onChange={e => setRoomName(e.target.value)}
                required
              />
              <select
                className="auth-input"
                value={mode}
                onChange={e => setMode(e.target.value)}
                required
              >
                {MODES.map(m => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
              <input
                className="auth-input"
                type="text"
                placeholder="Код комнаты"
                value={roomCode}
                onChange={e => setRoomCode(e.target.value)}
                required
              />
              <div className="modal-btns">
                <button className="home-btn" type="submit">Создать</button>
                <button className="home-btn" type="button" onClick={handleModalClose} style={{background: '#888', marginLeft: 12}}>Отмена</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Features;
