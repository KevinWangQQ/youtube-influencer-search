// Simple in-memory storage for serverless functions
// In a real production app, you'd use a proper database like PlanetScale, Supabase, etc.

const tasks = new Map();
const keywords = new Map();
const influencers = new Map();

function createTask(data) {
  tasks.set(data.id, { ...data, created_at: Date.now() });
}

function getTask(id) {
  return tasks.get(id) || null;
}

function updateTask(id, updates) {
  const task = tasks.get(id);
  if (task) {
    tasks.set(id, { ...task, ...updates });
  }
}

function getAllTasks() {
  return Array.from(tasks.values()).sort((a, b) => b.created_at - a.created_at).slice(0, 100);
}

function addKeyword(taskId, keyword) {
  const keywordId = Date.now() + Math.random();
  keywords.set(keywordId, {
    id: keywordId,
    task_id: taskId,
    keyword,
    processed: 0
  });
  return keywordId;
}

function getNextKeyword(taskId) {
  for (const [id, kw] of keywords.entries()) {
    if (kw.task_id === taskId && kw.processed === 0) {
      return kw;
    }
  }
  return null;
}

function markKeywordDone(keywordId) {
  const kw = keywords.get(keywordId);
  if (kw) {
    keywords.set(keywordId, { ...kw, processed: 1 });
  }
}

function countKeywords(taskId, processed = null) {
  let count = 0;
  for (const kw of keywords.values()) {
    if (kw.task_id === taskId && (processed === null || kw.processed === processed)) {
      count++;
    }
  }
  return count;
}

function addInfluencer(data) {
  const id = Date.now() + Math.random();
  const key = `${data.task_id}_${data.channel_id}_${data.video_id}`;
  
  // Simple deduplication
  for (const inf of influencers.values()) {
    if (inf.task_id === data.task_id && 
        inf.channel_id === data.channel_id && 
        inf.video_id === data.video_id) {
      return; // Already exists
    }
  }
  
  influencers.set(id, { id, ...data });
}

function getInfluencersByTask(taskId) {
  const results = [];
  for (const inf of influencers.values()) {
    if (inf.task_id === taskId) {
      results.push(inf);
    }
  }
  return results.sort((a, b) => b.views - a.views);
}

module.exports = {
  createTask,
  getTask,
  updateTask,
  getAllTasks,
  addKeyword,
  getNextKeyword,
  markKeywordDone,
  countKeywords,
  addInfluencer,
  getInfluencersByTask,
};
