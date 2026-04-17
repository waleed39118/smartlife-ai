import express from "express";
import { auth } from "../middleware/auth.js";

const router = express.Router();

router.post("/upgrade", auth, (req, res) => {
  res.json({ plan: "pro" });
});

router.get("/status", auth, (req, res) => {
  res.json({ plan: "free" });
});

export default router;