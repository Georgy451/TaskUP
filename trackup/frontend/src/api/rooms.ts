// API для создания комнаты
export async function createRoom(name: string, creator: string, mode: string) {
  const res = await fetch('/api/rooms', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, creator, mode }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Ошибка создания комнаты');
  }
  return res.json();
}
