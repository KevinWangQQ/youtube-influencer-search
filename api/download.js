const { sendCsv, sendJson } = require('./_http');
const { selectInfluencersByTask, selectTask } = require('./db');

function toCsv(rows) {
  const header = [
    'channel_id',
    'channel_title',
    'channel_url',
    'video_id',
    'video_title',
    'video_url',
    'subscribers',
    'views',
  ];
  const escape = (v) => '"' + String(v).replace(/"/g, '""') + '"';
  const lines = [header.join(',')];
  for (const r of rows) {
    lines.push([
      r.channel_id,
      r.channel_title,
      r.channel_url,
      r.video_id,
      r.video_title,
      r.video_url,
      r.subscribers,
      r.views,
    ].map(escape).join(','));
  }
  return lines.join('\n');
}

module.exports = async (req, res) => {
  const { task_id } = req.query || {};
  if (!task_id) return sendJson(res, 400, { error: 'task_id is required' });
  const task = selectTask.get(task_id);
  if (!task) return sendJson(res, 404, { error: 'Task not found' });
  const rows = selectInfluencersByTask.all(task_id);
  const csv = toCsv(rows);
  return sendCsv(res, 200, `results_${task_id}.csv`, csv);
};


