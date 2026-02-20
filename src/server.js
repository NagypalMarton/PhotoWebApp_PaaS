const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { initializePool, getPool } = require('./db');

const app = express();
const port = Number(process.env.PORT || 3000);
const uploadsDir = path.resolve(process.cwd(), 'uploads');
const defaultPageSize = 10;

if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadsDir),
  filename: (_req, file, cb) => {
    const extension = path.extname(file.originalname || '').toLowerCase();
    const safeExt = extension || '.jpg';
    cb(null, `${Date.now()}-${Math.round(Math.random() * 1e9)}${safeExt}`);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }
});

app.use(express.json());
app.use('/uploads', express.static(uploadsDir));
app.use(express.static(path.resolve(process.cwd(), 'public')));

app.get('/api/health', async (_req, res) => {
  try {
    const pool = getPool();
    await pool.query('SELECT 1');
    res.json({ status: 'ok' });
  } catch (error) {
    res.status(500).json({ status: 'error', message: error.message });
  }
});

app.get('/api/photos', async (req, res) => {
  try {
    const sortParam = (req.query.sort || 'date').toString();
    const sortColumn = sortParam === 'name' ? 'name' : 'upload_datetime';
    const orderParam = (req.query.order || 'desc').toString().toLowerCase();
    const order = orderParam === 'asc' ? 'ASC' : 'DESC';
    const search = (req.query.search || '').toString().trim();
    const page = Math.max(1, Number.parseInt(req.query.page, 10) || 1);
    const pageSizeRaw = Number.parseInt(req.query.pageSize, 10) || defaultPageSize;
    const pageSize = Math.min(Math.max(1, pageSizeRaw), 50);
    const offset = (page - 1) * pageSize;

    const whereClause = search ? 'WHERE name LIKE ?' : '';
    const whereParams = search ? [`%${search}%`] : [];

    const pool = getPool();
    const [countRows] = await pool.query(
      `SELECT COUNT(*) AS total
       FROM photos
       ${whereClause}`,
      whereParams
    );

    const [rows] = await pool.query(
      `SELECT id, name, tags, upload_datetime, file_path_or_url
       FROM photos
       ${whereClause}
       ORDER BY ${sortColumn} ${order}, id DESC
       LIMIT ? OFFSET ?`,
      [...whereParams, pageSize, offset]
    );

    res.json({
      items: rows.map((row) => ({
        id: row.id,
        name: row.name,
        tags: row.tags ? row.tags.split(',').map((item) => item.trim()).filter(Boolean) : [],
        upload_datetime: row.upload_datetime,
        image_url: row.file_path_or_url
      })),
      total: countRows[0].total,
      page,
      pageSize
    });
  } catch (error) {
    res.status(500).json({ message: 'Hiba a képek lekérdezése közben.' });
  }
});

app.post('/api/photos', upload.single('photo'), async (req, res) => {
  try {
    const name = (req.body.name || '').trim();
    const tags = (req.body.tags || '')
      .toString()
      .split(',')
      .map((tag) => tag.trim())
      .filter(Boolean)
      .slice(0, 10);
    const tagsDbValue = tags.length > 0 ? tags.join(', ') : null;

    if (!name || name.length > 40) {
      if (req.file?.path && fs.existsSync(req.file.path)) {
        fs.unlinkSync(req.file.path);
      }
      return res.status(400).json({ message: 'A név kötelező és max. 40 karakter lehet.' });
    }

    if (!req.file) {
      return res.status(400).json({ message: 'A képfájl kötelező.' });
    }

    const relativePath = `/uploads/${req.file.filename}`;
    const pool = getPool();
    const [result] = await pool.query(
      'INSERT INTO photos (name, tags, upload_datetime, file_path_or_url) VALUES (?, ?, NOW(), ?)',
      [name, tagsDbValue, relativePath]
    );

    return res.status(201).json({
      id: result.insertId,
      name,
      tags,
      image_url: relativePath
    });
  } catch (error) {
    if (req.file?.path && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    return res.status(500).json({ message: 'Hiba a feltöltés közben.' });
  }
});

app.delete('/api/photos/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    if (!Number.isInteger(id) || id <= 0) {
      return res.status(400).json({ message: 'Érvénytelen azonosító.' });
    }

    const pool = getPool();
    const [rows] = await pool.query('SELECT file_path_or_url FROM photos WHERE id = ?', [id]);
    if (rows.length === 0) {
      return res.status(404).json({ message: 'A kép nem található.' });
    }

    await pool.query('DELETE FROM photos WHERE id = ?', [id]);

    const diskPath = path.resolve(process.cwd(), rows[0].file_path_or_url.replace(/^\//, ''));
    if (fs.existsSync(diskPath)) {
      fs.unlinkSync(diskPath);
    }

    return res.status(204).send();
  } catch (error) {
    return res.status(500).json({ message: 'Hiba a törlés közben.' });
  }
});

app.get('*', (_req, res) => {
  res.sendFile(path.resolve(process.cwd(), 'public', 'index.html'));
});

async function start() {
  try {
    await initializePool();
    const pool = getPool();
    const [columns] = await pool.query(
      `SELECT COLUMN_NAME
       FROM information_schema.COLUMNS
       WHERE TABLE_SCHEMA = ? AND TABLE_NAME = 'photos' AND COLUMN_NAME = 'tags'`,
      [process.env.DB_NAME || 'gallery']
    );

    if (columns.length === 0) {
      await pool.query('ALTER TABLE photos ADD COLUMN tags VARCHAR(255) NULL');
    }

    app.listen(port, () => {
      console.log(`PhotoWebApp MVP listening on port ${port}`);
    });
  } catch (error) {
    console.error('Nem sikerült csatlakozni az adatbázishoz:', error.message);
    process.exit(1);
  }
}

start();
