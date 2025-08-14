const { selectTask } = require('../db');

module.exports = async (req, res) => {
  const { task_id } = req.query || {};
  if (!task_id) {
    res.status(400).json({ error: 'task_id is required' });
    return;
  }
  const task = selectTask.get(task_id);
  if (!task) {
    res.status(404).json({ error: 'Task not found' });
    return;
  }
  res.status(200).json({
    id: task.id,
    status: task.status,
    progress: task.progress,
    productName: task.product_name,
    createdAt: task.created_at,
  });
};


