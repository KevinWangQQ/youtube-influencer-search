const { sendJson } = require('./_http');
const {
  selectTask,
  updateTask,
  selectNextKeyword,
  markKeywordDone,
  countAllKeywords,
  countProcessedKeywords,
  insertInfluencer,
} = require('./db');
const { youtubeSearch, youtubeChannelsStats, youtubeVideosStats } = require('./utils');

module.exports = async (req, res) => {
  const { task_id } = req.query || {};
  if (!task_id) {
    return sendJson(res, 400, { error: 'task_id is required' });
  }
  const task = selectTask.get(task_id);
  if (!task) {
    return sendJson(res, 404, { error: 'Task not found' });
  }
  // If already terminal
  if (task.status === 'completed' || task.status === 'failed') {
    return sendJson(res, 200, { id: task.id, status: task.status, progress: task.progress, productName: task.product_name, createdAt: task.created_at });
  }

  try {
    // Process one keyword per poll using the hashed key is not enough; we must require client to pass apiKey again for each poll.
    const apiKey = req.headers['x-youtube-key'] || '';
    if (!apiKey) return sendJson(res, 400, { error: 'Missing X-YouTube-Key header' });
    const next = selectNextKeyword.get(task_id);
    if (!next) {
      updateTask.run({ id: task_id, status: 'completed', progress: 100 });
      return sendJson(res, 200, { id: task.id, status: 'completed', progress: 100, productName: task.product_name, createdAt: task.created_at });
    }

    const searchItems = await youtubeSearch({ apiKey, query: next.keyword, maxResults: Math.min(50, task.max_results) });
    const channelIds = Array.from(new Set(searchItems.map((i) => i.snippet?.channelId).filter(Boolean)));
    const videoIds = Array.from(new Set(searchItems.map((i) => i.id?.videoId).filter(Boolean)));
    const [channelMap, videoMap] = await Promise.all([
      youtubeChannelsStats({ apiKey, channelIds }),
      youtubeVideosStats({ apiKey, videoIds }),
    ]);
    for (const item of searchItems) {
      const channelId = item.snippet?.channelId;
      const videoId = item.id?.videoId;
      if (!channelId || !videoId) continue;
      const channel = channelMap[channelId];
      const video = videoMap[videoId];
      if (!channel || !video) continue;
      if (channel.subscribers < task.min_subscribers) continue;
      if (video.views < task.min_views) continue;
      insertInfluencer.run({
        task_id: task_id,
        channel_id: channelId,
        channel_title: channel.title,
        channel_url: channel.url,
        video_id: videoId,
        video_title: video.title,
        video_url: video.url,
        subscribers: channel.subscribers,
        views: video.views,
      });
    }
    markKeywordDone.run(next.id);

    const total = countAllKeywords.get(task_id).c;
    const done = countProcessedKeywords.get(task_id).c;
    const progress = total > 0 ? Math.round((done / total) * 100) : 100;
    const status = done >= total ? 'completed' : 'running';
    updateTask.run({ id: task_id, status, progress });

    return sendJson(res, 200, { id: task.id, status, progress, productName: task.product_name, createdAt: task.created_at });
  } catch (e) {
    updateTask.run({ id: task_id, status: 'failed', progress: 100 });
    return sendJson(res, 200, { id: task.id, status: 'failed', progress: 100, productName: task.product_name, createdAt: task.created_at, error: e.message });
  }
};


