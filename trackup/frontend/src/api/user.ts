// API-модуль для работы с пользователями
export async function registerUser(username: string, email: string, password: string) {
  const res = await fetch('http://localhost:8001/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Ошибка регистрации');
  }
  return res.json();
}

export async function loginUser(username: string, password: string) {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  // OAuth2PasswordRequestForm требует Content-Type: application/x-www-form-urlencoded
  const res = await fetch('http://localhost:8001/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Ошибка входа');
  }
  return res.json();
}
