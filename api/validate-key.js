const axios = require('axios');
const { sendJson } = require('./_http');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return sendJson(res, 405, { error: 'Method not allowed' });
  try {
    let body = '';
    for await (const chunk of req) body += chunk;
    const parsed = body ? JSON.parse(body) : {};
    const { apiKey } = parsed || {};
    if (!apiKey) return sendJson(res, 400, { valid: false, error: 'apiKey is required' });
    // Simple validation: call a cheap endpoint
    const url = 'https://www.googleapis.com/youtube/v3/videos';
    const params = { key: apiKey, id: 'dQw4w9WgXcQ', part: 'id' };
    await axios.get(url, { params });
    return sendJson(res, 200, { valid: true });
  } catch (e) {
    return sendJson(res, 200, { valid: false, error: e.response?.data?.error?.message || e.message });
  }
};


