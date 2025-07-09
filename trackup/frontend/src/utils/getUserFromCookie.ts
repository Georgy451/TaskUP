// Получение имени пользователя из cookie (JWT или простое значение)
export function getUserFromCookie(): string | null {
  const match = document.cookie.match(/(?:^|; )username=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}
