const { sendJson } = require('./_http');
const { selectTasks } = require('./db');

module.exports = async (_req, res) => {
  const rows = selectTasks.all();
  return sendJson(res, 200, { tasks: rows });
};


