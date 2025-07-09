// API для подключения к комнате по коду
export async function joinRoom(room_id: string, username: string) {
  const res = await fetch('/api/game/join', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ room_id, username }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Ошибка подключения к комнате');
  }
  return res.json();
}
