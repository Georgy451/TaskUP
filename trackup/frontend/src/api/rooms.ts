// API для создания комнаты
export async function createRoom(name: string, participants: string[], mode: string) {
  const res = await fetch('http://localhost:8002/rooms', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, participants, mode }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Ошибка создания комнаты');
  }
  return res.json();
}
