import express from "express";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

const router = express.Router();

const users = [];

router.post("/register", async (req, res) => {
  const { email, password } = req.body;

  const hash = await bcrypt.hash(password, 10);

  users.push({ email, password: hash });

  res.json({ success: true });
});

router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  const user = users.find(u => u.email === email);
  if (!user) return res.status(400).json({ error: "User not found" });

  const ok = await bcrypt.compare(password, user.password);
  if (!ok) return res.status(400).json({ error: "Wrong password" });

  const token = jwt.sign({ email }, process.env.JWT_SECRET);

  res.json({ token });
});

export default router;