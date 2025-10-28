// api/api.js - Vercel serverless function
export default function handler(req, res) {
const telegram_id = req.query.telegram_id;
const access_key = req.query.access_key;

const users = [ { telegram_id: "6784382795", balance: 5000, access_key: "Cris-user1-2025" }, { telegram_id: "987654", balance: 10000, access_key: "key-user2-2025" }, { telegram_id: "123456", balance: "unlimited", access_key: "key-user3-2025" } ]; const user = users.find(u => u.telegram_id === telegram_id); if (!user) { return res.status(404).json({ error: "User not found" }); } if (user.access_key !== access_key) { return res.status(403).json({ error: "Invalid access key" }); } res.status(200).json({ telegram_id: user.telegram_id, balance: user.balance });

}



