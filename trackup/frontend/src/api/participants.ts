// Получить список участников комнаты
export async function getParticipants(room_id: string): Promise<string[]> {
  const res = await fetch(`/api/game/participants?room_id=${encodeURIComponent(room_id)}`);
  if (!res.ok) {
    return [];
  }
  return res.json();
}
