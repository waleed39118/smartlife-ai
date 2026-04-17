import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import authRoutes from "./routes/auth.js";
import billingRoutes from "./routes/billing.js";

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
  res.send("SmartLife API Running");
});

app.use("/auth", authRoutes);
app.use("/billing", billingRoutes);

app.listen(3001, () => {
  console.log("Server running on port 3001");
});