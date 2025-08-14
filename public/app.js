const form = document.getElementById('searchForm');
const validateBtn = document.getElementById('validateBtn');
const demoBtn = document.getElementById('demoBtn');
const exportBtn = document.getElementById('exportBtn');
const newSearchBtn = document.getElementById('newSearchBtn');
const loading = document.querySelector('.loading-spinner');
const resultsContainer = document.querySelector('.results-container');
const influencersGrid = document.getElementById('influencersGrid');
const summaryStats = document.getElementById('summaryStats');
const keywordsList = document.getElementById('keywordsList');
const demoAlert = document.getElementById('demoAlert');
const progressInner = document.getElementById('progressInner');
const progressText = document.getElementById('progressText');

async function api(path, opts = {}) {
  const res = await fetch(`/api/${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return res.json();
  return res.text();
}

function renderSummary(summary) {
  summaryStats.innerHTML = '';
  const items = [
    { label: '总结果数', value: summary.count },
    { label: '平均订阅数', value: summary.avgSubscribers },
    { label: '最高订阅数', value: summary.maxSubscribers },
    { label: '平均观看数', value: summary.avgViews },
    { label: '最高观看数', value: summary.maxViews },
  ];
  for (const s of items) {
    const col = document.createElement('div');
    col.className = 'col-md-2 mb-3';
    col.innerHTML = `
      <div class="stats-card">
        <div class="h2">${s.value}</div>
        <div class="small">${s.label}</div>
      </div>
    `;
    summaryStats.appendChild(col);
  }
}

function renderInfluencers(list) {
  influencersGrid.innerHTML = '';
  for (const r of list) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-4';
    col.innerHTML = `
      <div class="card influencer-card h-100">
        <div class="card-body d-flex flex-column">
          <h5 class="card-title">${r.channel_title}</h5>
          <p class="card-text text-muted small mb-2">订阅数：${r.subscribers.toLocaleString()}</p>
          <p class="card-text fw-semibold">${r.video_title}</p>
          <p class="card-text text-muted small">观看数：${r.views.toLocaleString()}</p>
          <div class="mt-auto d-flex gap-2">
            <a class="btn btn-outline-primary btn-sm" href="${r.channel_url}" target="_blank">频道</a>
            <a class="btn btn-primary btn-sm" href="${r.video_url}" target="_blank">视频</a>
          </div>
        </div>
      </div>
    `;
    influencersGrid.appendChild(col);
  }
}

async function pollStatus(taskId, apiKey) {
  while (true) {
    const res = await fetch(`/api/status?task_id=${encodeURIComponent(taskId)}`, {
      headers: { 'X-YouTube-Key': apiKey },
    });
    const data = await res.json();
    if (typeof data.progress === 'number') {
      progressInner.style.width = `${data.progress}%`;
      progressInner.setAttribute('aria-valuenow', String(data.progress));
      progressText.textContent = `进度：${data.progress}%`;
    }
    if (data.status === 'completed' || data.status === 'failed') return data.status;
    await new Promise((r) => setTimeout(r, 1500));
  }
}

validateBtn.addEventListener('click', async () => {
  const apiKey = document.getElementById('apiKey').value.trim();
  if (!apiKey) return alert('请输入API密钥');
  validateBtn.disabled = true;
  try {
    const res = await api('validate-key', { method: 'POST', body: JSON.stringify({ apiKey }) });
    if (res.valid) alert('API密钥有效');
    else alert(`验证失败：${res.error || '未知错误'}`);
  } catch (e) {
    alert('验证失败');
  } finally {
    validateBtn.disabled = false;
  }
});

demoBtn.addEventListener('click', async () => {
  demoAlert.classList.remove('d-none');
  resultsContainer.style.display = 'block';
  loading.style.display = 'none';
  const demoSummary = { count: 6, avgSubscribers: 120000, maxSubscribers: 18600000, avgViews: 45000, maxViews: 725000 };
  renderSummary(demoSummary);
  renderInfluencers([
    {
      channel_title: 'CNN', subscribers: 18600000, channel_url: 'https://www.youtube.com/@CNN',
      video_title: 'eero 7 review: next-gen WiFi', views: 725000, video_url: 'https://www.youtube.com/watch?v=xxxxx'
    },
  ]);
  keywordsList.innerHTML = '<div>示例关键词：eero 7 review, eero 7 unboxing, eero 7 test</div>';
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const productName = document.getElementById('productName').value.trim();
  const apiKey = document.getElementById('apiKey').value.trim();
  const minSubscribers = Number(document.getElementById('minSubscribers').value);
  const minViews = Number(document.getElementById('minViews').value);
  const maxResults = Number(document.getElementById('maxResults').value);
  if (!productName || !apiKey) return alert('请输入产品机型和API密钥');

  demoAlert.classList.add('d-none');
  resultsContainer.style.display = 'none';
  loading.style.display = 'block';

  try {
    const { taskId } = await api('search', {
      method: 'POST',
      body: JSON.stringify({ productName, apiKey, minSubscribers, minViews, maxResults }),
    });

    const status = await pollStatus(taskId, apiKey);
    const data = await api(`results?task_id=${encodeURIComponent(taskId)}`);
    loading.style.display = 'none';
    resultsContainer.style.display = 'block';
    renderSummary(data.summary);
    renderInfluencers(data.influencers);
    keywordsList.innerHTML = `<div>关键词已生成并用于搜索</div>`;

    exportBtn.onclick = () => {
      window.location.href = `/api/download?task_id=${encodeURIComponent(taskId)}`;
    };
  } catch (err) {
    loading.style.display = 'none';
    alert('搜索失败，请检查API密钥或稍后重试');
  }
});

newSearchBtn.addEventListener('click', () => {
  resultsContainer.style.display = 'none';
});


