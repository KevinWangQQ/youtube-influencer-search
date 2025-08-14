const crypto = require('crypto');
const axios = require('axios');

function sha256Hex(input) {
  return crypto.createHash('sha256').update(input).digest('hex');
}

function generateKeywords(productName) {
  const base = productName.trim();
  const suffixes = [
    'review',
    'unboxing',
    'test',
    'hands on',
    'setup',
    'performance',
    'comparison',
  ];
  const extra = [];
  if (/router|wifi|mesh|be|ax|ac|orbi|zenwifi|eero|archer/i.test(base)) {
    extra.push('wifi router review', 'mesh router review');
  }
  const raw = new Set([
    base,
    ...suffixes.map((s) => `${base} ${s}`),
    ...extra.map((e) => `${base} ${e}`),
  ]);
  return Array.from(raw).slice(0, 8);
}

async function youtubeSearch({ apiKey, query, maxResults = 10, regionCode = 'US' }) {
  const url = 'https://www.googleapis.com/youtube/v3/search';
  const params = {
    key: apiKey,
    q: query,
    part: 'snippet',
    type: 'video',
    maxResults: Math.min(Math.max(1, maxResults), 50),
    regionCode,
  };
  const { data } = await axios.get(url, { params });
  return data.items || [];
}

async function youtubeChannelsStats({ apiKey, channelIds }) {
  if (channelIds.length === 0) return {};
  const url = 'https://www.googleapis.com/youtube/v3/channels';
  const params = {
    key: apiKey,
    id: channelIds.join(','),
    part: 'statistics,snippet',
  };
  const { data } = await axios.get(url, { params });
  const map = {};
  for (const item of data.items || []) {
    map[item.id] = {
      title: item.snippet?.title || '',
      subscribers: Number(item.statistics?.subscriberCount || 0),
      url: `https://www.youtube.com/channel/${item.id}`,
    };
  }
  return map;
}

async function youtubeVideosStats({ apiKey, videoIds }) {
  if (videoIds.length === 0) return {};
  const url = 'https://www.googleapis.com/youtube/v3/videos';
  const params = {
    key: apiKey,
    id: videoIds.join(','),
    part: 'statistics,snippet',
  };
  const { data } = await axios.get(url, { params });
  const map = {};
  for (const item of data.items || []) {
    map[item.id] = {
      title: item.snippet?.title || '',
      views: Number(item.statistics?.viewCount || 0),
      url: `https://www.youtube.com/watch?v=${item.id}`,
    };
  }
  return map;
}

module.exports = {
  sha256Hex,
  generateKeywords,
  youtubeSearch,
  youtubeChannelsStats,
  youtubeVideosStats,
};


