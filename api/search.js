const { nanoid } = require('nanoid');
const { sendJson } = require('./_http');
const { createTask, addKeyword } = require('./storage');
const { sha256Hex, generateKeywords } = require('./utils');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return sendJson(res, 405, { error: 'Method not allowed' });
  try {
    let body = '';
    for await (const chunk of req) body += chunk;
    const parsed = body ? JSON.parse(body) : {};
    const { productName, apiKey, minSubscribers = 10000, minViews = 5000, maxResults = 50 } = parsed || {};
    if (!productName || !apiKey) {
      return sendJson(res, 400, { error: 'productName and apiKey are required' });
    }

    const taskId = nanoid(12);
    const apiKeyHash = sha256Hex(apiKey);
    createTask({
      id: taskId,
      product_name: productName,
      api_key_hash: apiKeyHash,
      min_subscribers: Number(minSubscribers),
      min_views: Number(minViews),
      max_results: Number(maxResults),
      status: 'running',
      progress: 0,
    });

    // Initialize keywords for stepwise polling
    const keywords = generateKeywords(productName);
    if (!Array.isArray(keywords) || keywords.length === 0) {
      return sendJson(res, 400, { error: 'Failed to generate keywords' });
    }
    for (const kw of keywords) addKeyword(taskId, kw);
    return sendJson(res, 200, { taskId, keywords });
  } catch (e) {
    return sendJson(res, 500, { error: e?.response?.data?.error?.message || e.message || 'Internal error' });
  }
};


