import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createRoom } from "../api/rooms";
import { getUserFromCookie } from "../utils/getUserFromCookie";

const MODES = [
  { value: "classic", label: "Классический" },
  { value: "fast", label: "Быстрый" },
  { value: "custom", label: "Пользовательский" },
];

const Features = () => {
  const [showModal, setShowModal] = useState(false);
  const [roomName, setRoomName] = useState("");
  const [mode, setMode] = useState(MODES[0].value);
  const [participants, setParticipants] = useState<string[]>([""]);
  const navigate = useNavigate();

  const handleCreate = () => {
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setRoomName("");
    setMode(MODES[0].value);
    setParticipants([""]);
  };

  const handleModalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const filtered = participants.map(p => p.trim()).filter(Boolean);
      if (filtered.length === 0) {
        alert("Добавьте хотя бы одного участника!");
        return;
      }
      await createRoom(roomName, filtered, mode);
      setShowModal(false);
      setRoomName("");
      setMode(MODES[0].value);
      setParticipants([""]);
      navigate("/game");
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleParticipantChange = (i: number, value: string) => {
    setParticipants(prev => {
      const arr = [...prev];
      arr[i] = value;
      return arr;
    });
  };

  const handleAddParticipant = () => {
    setParticipants(prev => [...prev, ""]);
  };

  const handleRemoveParticipant = (i: number) => {
    setParticipants(prev => prev.length > 1 ? prev.filter((_, idx) => idx !== i) : prev);
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
              <div style={{marginTop: 12}}>
                <label style={{fontWeight: 500}}>Участники:</label>
                {participants.map((p, i) => (
                  <div key={i} style={{display: 'flex', alignItems: 'center', marginBottom: 6}}>
                    <input
                      className="auth-input"
                      type="text"
                      placeholder={`Имя участника ${i+1}`}
                      value={p}
                      onChange={e => handleParticipantChange(i, e.target.value)}
                      required
                      style={{flex: 1}}
                    />
                    <button type="button" className="home-btn" style={{marginLeft: 8, padding: '2px 8px'}} onClick={() => handleRemoveParticipant(i)} disabled={participants.length === 1}>–</button>
                  </div>
                ))}
                <button type="button" className="home-btn" style={{marginTop: 4}} onClick={handleAddParticipant}>Добавить участника</button>
              </div>
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
