import { useEffect, useState } from "react";
import { getParticipants } from "../api/participants";

const mockTruth = [
  "Расскажи свой секрет!",
  "Кого ты считаешь своим лучшим другом?",
  "Чего ты боишься больше всего?",
  "Кто тебе нравится?",
  "Самый неловкий момент в твоей жизни?"
];
const mockDare = [
  "Сделай 10 приседаний!",
  "Изобрази животное!",
  "Станцуй под воображаемую музыку!",
  "Покажи фокус!",
  "Сделай комплимент соседу!"
];

const confettiColors = ["#646cff", "#61dafb", "#fff", "#232526"];

function Confetti({show}:{show:boolean}) {
  if (!show) return null;
  return (
    <div style={{position:'fixed',left:0,top:0,width:'100vw',height:'100vh',pointerEvents:'none',zIndex:999}}>
      {Array.from({length: 24}).map((_,i)=>(
        <div key={i} style={{
          position:'absolute',
          left: Math.random()*100+'vw',
          top: Math.random()*40+'vh',
          width: 12+Math.random()*8,
          height: 12+Math.random()*8,
          borderRadius: '50%',
          background: confettiColors[Math.floor(Math.random()*confettiColors.length)],
          opacity: 0.7+Math.random()*0.3,
          animation: `fall 1.7s ${Math.random()}s cubic-bezier(.4,0,.2,1) forwards`
        }} />
      ))}
      <style>{`@keyframes fall {0%{transform:translateY(0);}100%{transform:translateY(60vh) scale(0.7);opacity:0;}}`}</style>
    </div>
  );
}

const GameProcess = () => {
  const [participants, setParticipants] = useState<string[]>([]);
  const [current, setCurrent] = useState(0);
  const [task, setTask] = useState("");
  const [mode, setMode] = useState<"truth"|"dare"|null>(null);
  const [showConfetti, setShowConfetti] = useState(false);

  // Получаем room_id из localStorage или query-параметра (добавь свою логику)
  const room_id = localStorage.getItem("room_id") || "";

  useEffect(() => {
    if (room_id) {
      getParticipants(room_id).then(setParticipants);
    }
  }, [room_id]);

  const nextTurn = () => {
    setMode(null);
    setTask("");
    setCurrent((current + 1) % participants.length);
    setShowConfetti(false);
  };

  const chooseTruth = () => {
    setMode("truth");
    setTask(mockTruth[Math.floor(Math.random() * mockTruth.length)]);
    setShowConfetti(true);
    setTimeout(()=>setShowConfetti(false), 1700);
  };
  const chooseDare = () => {
    setMode("dare");
    setTask(mockDare[Math.floor(Math.random() * mockDare.length)]);
    setShowConfetti(true);
    setTimeout(()=>setShowConfetti(false), 1700);
  };

  // Заглушка для завершения игры
  const finishGame = () => {
    alert('Игра завершена!');
    // Здесь можно добавить вызов API для завершения игры
  };

  return (
    <div className="game-list-bg">
      <Confetti show={showConfetti} />
      {/* Кнопка завершения игры */}
      <button className="home-btn" style={{position:'absolute',top:24,right:24,zIndex:1000}} onClick={finishGame}>
        Завершить игру
      </button>
      <div className="game-list-container">
        <div className="game-players-row">
          {participants.map((name, i) => (
            <div
              key={name}
              className={`game-player-card${i === current ? " active" : ""}`}
            >
              {name}
            </div>
          ))}
        </div>
        <div className="game-task-list" style={{minHeight:220, minWidth:1100, maxWidth:'98vw'}}>
          {mode === null ? (
            <div className="game-choice-btns-row">
              <button className="home-btn game-choice-btn" onClick={chooseTruth} style={{order:1}}>Правда</button>
              <button className="home-btn game-choice-btn" onClick={chooseDare} style={{order:2}}>Действие</button>
            </div>
          ) : (
            <>
              <div className="game-task-text" style={{animation:'task-fade-in 0.7s'}}>{task}</div>
              <button className="home-btn" onClick={nextTurn} style={{marginTop: 64,animation:'btn-pop 0.7s'}}>Следующий ход</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameProcess;
