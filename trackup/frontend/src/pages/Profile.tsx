import React, { useRef, useState } from "react";
import { getUserFromCookie } from "../utils/getUserFromCookie";

const Profile = () => {
  // Здесь можно получить данные пользователя из стора/контекста
  const user = {
    name: "Георгий",
    email: "georgiy@example.com",
    avatar: "https://ui-avatars.com/api/?name=Георгий&background=6c63ff&color=fff&size=128"
  };

  const [avatar, setAvatar] = useState("https://ui-avatars.com/api/?name=Георгий&background=6c63ff&color=fff&size=128");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const username = getUserFromCookie() || "Гость";

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        if (ev.target?.result) {
          setAvatar(ev.target.result as string);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="profile-page-bg">
      <div className="profile-page-glass">
        <div className="profile-page-info-name">{username}</div>
        <img src={avatar} alt="avatar" className="profile-avatar-large" />
        <input
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          ref={fileInputRef}
          onChange={handleAvatarChange}
        />
        <button
          className="home-btn"
          style={{ marginTop: 12, marginBottom: 12 }}
          onClick={() => fileInputRef.current?.click()}
        >
          Загрузить аватар
        </button>
        <button className="home-btn" style={{marginTop: 12}} onClick={() => window.location.href = '/features'}>Назад</button>
      </div>
    </div>
  );
};

export default Profile;
