const { sendJson } = require('./_http');
module.exports = async (_req, res) => sendJson(res, 200, { ok: true, message: 'YouTube Influencer Search API (Node 22)' });


