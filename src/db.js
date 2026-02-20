const mysql = require('mysql2/promise');

const config = {
  host: process.env.DB_HOST || 'localhost',
  port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER || 'gallery_user',
  password: process.env.DB_PASSWORD || 'gallery_password',
  database: process.env.DB_NAME || 'gallery',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

let pool;

async function initializePool(retries = 20, delayMs = 2000) {
  for (let attempt = 1; attempt <= retries; attempt += 1) {
    try {
      pool = mysql.createPool(config);
      await pool.query('SELECT 1');
      return pool;
    } catch (error) {
      if (attempt === retries) {
        throw error;
      }
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
}

function getPool() {
  if (!pool) {
    throw new Error('Database pool is not initialized.');
  }
  return pool;
}

module.exports = {
  initializePool,
  getPool
};
