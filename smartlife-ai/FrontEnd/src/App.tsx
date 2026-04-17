import { useState } from "react";
import { login } from "./api";

export default function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");

  async function handleLogin() {
    const res = await login(email, password);
    setToken(res.token);
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>SmartLife</h1>

      {!token ? (
        <>
          <input placeholder="email" onChange={e => setEmail(e.target.value)} />
          <input placeholder="password" type="password" onChange={e => setPassword(e.target.value)} />
          <button onClick={handleLogin}>Login</button>
        </>
      ) : (
        <h2>Logged in</h2>
      )}
    </div>
  );
}