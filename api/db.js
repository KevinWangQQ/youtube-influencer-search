const Database = require('better-sqlite3');
const path = require('path');

function openDatabase() {
  const primaryPath = path.join(process.cwd(), 'database.db');
  try {
    return new Database(primaryPath);
  } catch (e) {
    const tmpPath = path.join('/tmp', 'database.db');
    return new Database(tmpPath);
  }
}

const db = openDatabase();

db.pragma('journal_mode = WAL');

db.exec(`
CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  product_name TEXT NOT NULL,
  api_key_hash TEXT NOT NULL,
  min_subscribers INTEGER NOT NULL,
  min_views INTEGER NOT NULL,
  max_results INTEGER NOT NULL,
  status TEXT NOT NULL,
  progress INTEGER NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS task_keywords (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT NOT NULL,
  keyword TEXT NOT NULL,
  processed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS influencers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT NOT NULL,
  channel_id TEXT NOT NULL,
  channel_title TEXT NOT NULL,
  channel_url TEXT NOT NULL,
  video_id TEXT NOT NULL,
  video_title TEXT NOT NULL,
  video_url TEXT NOT NULL,
  subscribers INTEGER NOT NULL,
  views INTEGER NOT NULL,
  UNIQUE(task_id, channel_id, video_id)
);
`);

const insertTask = db.prepare(`
INSERT INTO tasks (id, product_name, api_key_hash, min_subscribers, min_views, max_results, status, progress, created_at)
VALUES (@id, @product_name, @api_key_hash, @min_subscribers, @min_views, @max_results, @status, @progress, @created_at)
`);

const updateTask = db.prepare(`
UPDATE tasks SET status=@status, progress=@progress WHERE id=@id
`);

const selectTask = db.prepare(`SELECT * FROM tasks WHERE id = ?`);
const selectTasks = db.prepare(`SELECT * FROM tasks ORDER BY created_at DESC LIMIT 100`);

const insertInfluencer = db.prepare(`
INSERT OR IGNORE INTO influencers (
  task_id, channel_id, channel_title, channel_url, video_id, video_title, video_url, subscribers, views
) VALUES (@task_id, @channel_id, @channel_title, @channel_url, @video_id, @video_title, @video_url, @subscribers, @views)
`);

const selectInfluencersByTask = db.prepare(`SELECT * FROM influencers WHERE task_id = ? ORDER BY views DESC`);

const insertKeyword = db.prepare(`INSERT INTO task_keywords (task_id, keyword, processed) VALUES (?, ?, 0)`);
const selectNextKeyword = db.prepare(`SELECT * FROM task_keywords WHERE task_id = ? AND processed = 0 LIMIT 1`);
const markKeywordDone = db.prepare(`UPDATE task_keywords SET processed = 1 WHERE id = ?`);
const countAllKeywords = db.prepare(`SELECT COUNT(1) AS c FROM task_keywords WHERE task_id = ?`);
const countProcessedKeywords = db.prepare(`SELECT COUNT(1) AS c FROM task_keywords WHERE task_id = ? AND processed = 1`);

module.exports = {
  insertTask,
  updateTask,
  selectTask,
  selectTasks,
  insertInfluencer,
  selectInfluencersByTask,
  insertKeyword,
  selectNextKeyword,
  markKeywordDone,
  countAllKeywords,
  countProcessedKeywords,
};


