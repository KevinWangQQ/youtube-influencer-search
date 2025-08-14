const { sendJson } = require('./_http');
const { getTask, getInfluencersByTask } = require('./storage');

module.exports = async (req, res) => {
  const { task_id } = req.query || {};
  if (!task_id) return sendJson(res, 400, { error: 'task_id is required' });
  const task = getTask(task_id);
  if (!task) return sendJson(res, 404, { error: 'Task not found' });
  const list = getInfluencersByTask(task_id);
  const summary = {
    count: list.length,
    maxSubscribers: list.reduce((m, r) => Math.max(m, r.subscribers), 0),
    maxViews: list.reduce((m, r) => Math.max(m, r.views), 0),
    avgSubscribers: list.length ? Math.round(list.reduce((s, r) => s + r.subscribers, 0) / list.length) : 0,
    avgViews: list.length ? Math.round(list.reduce((s, r) => s + r.views, 0) / list.length) : 0,
  };
  return sendJson(res, 200, { taskId: task_id, summary, influencers: list });
};


