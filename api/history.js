const { sendJson } = require('./_http');
const { getAllTasks } = require('./storage');

module.exports = async (_req, res) => {
  const rows = getAllTasks();
  return sendJson(res, 200, { tasks: rows });
};


