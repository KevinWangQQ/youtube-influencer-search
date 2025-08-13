// 全局变量
let currentTaskId = null;
let progressInterval = null;
let loadingModal = null;

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    
    // 绑定事件监听器
    document.getElementById('searchForm').addEventListener('submit', handleSearchSubmit);
    document.getElementById('validateKeyBtn').addEventListener('click', validateApiKey);
    document.getElementById('downloadBtn').addEventListener('click', downloadResults);
    
    // 检查是否有正在运行的任务
    checkRunningTasks();
});

// 处理搜索表单提交
async function handleSearchSubmit(event) {
    event.preventDefault();
    
    const formData = {
        product_name: document.getElementById('productName').value.trim(),
        api_key: document.getElementById('apiKey').value.trim(),
        min_subscribers: parseInt(document.getElementById('minSubscribers').value) || 10000,
        min_view_count: parseInt(document.getElementById('minViewCount').value) || 5000
    };
    
    // 表单验证
    if (!formData.product_name) {
        showAlert('请输入产品机型', 'warning');
        return;
    }
    
    if (!formData.api_key) {
        showAlert('请输入YouTube API密钥', 'warning');
        return;
    }
    
    try {
        showAlert('正在启动搜索任务...', 'info');
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentTaskId = result.task_id;
            showProgressSection(formData.product_name);
            startProgressMonitoring();
            showAlert(result.message, 'success');
        } else {
            showAlert(result.error || '启动搜索失败', 'danger');
        }
        
    } catch (error) {
        console.error('搜索请求失败:', error);
        showAlert('网络请求失败，请重试', 'danger');
    }
}

// 验证API密钥
async function validateApiKey() {
    const apiKey = document.getElementById('apiKey').value.trim();
    
    if (!apiKey) {
        showAlert('请先输入API密钥', 'warning');
        return;
    }
    
    loadingModal.show();
    
    try {
        const response = await fetch('/api/validate-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const result = await response.json();
        
        if (result.valid) {
            showAlert('API密钥验证成功！', 'success');
            document.getElementById('validateKeyBtn').innerHTML = '<i class="fas fa-check-circle text-success"></i>';
        } else {
            showAlert(`API密钥验证失败: ${result.error}`, 'danger');
            document.getElementById('validateKeyBtn').innerHTML = '<i class="fas fa-times-circle text-danger"></i>';
        }
        
    } catch (error) {
        console.error('验证API密钥失败:', error);
        showAlert('验证API密钥时发生错误', 'danger');
    } finally {
        loadingModal.hide();
    }
}

// 显示进度部分
function showProgressSection(productName) {
    document.getElementById('taskProduct').textContent = `- ${productName}`;
    document.getElementById('progressContainer').style.display = 'block';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('historyContainer').style.display = 'none';
    
    // 滚动到进度部分
    document.getElementById('progressContainer').scrollIntoView({ behavior: 'smooth' });
}

// 开始进度监控
function startProgressMonitoring() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    
    progressInterval = setInterval(async () => {
        if (currentTaskId) {
            await updateProgress();
        }
    }, 2000); // 每2秒更新一次
}

// 更新进度
async function updateProgress() {
    try {
        const response = await fetch(`/api/status/${currentTaskId}`);
        const result = await response.json();
        
        if (result.success) {
            const status = result.status;
            
            // 更新进度条
            const progress = status.progress || 0;
            document.getElementById('progressBar').style.width = `${progress}%`;
            document.getElementById('progressText').textContent = `${Math.round(progress)}%`;
            
            // 更新统计信息
            document.getElementById('currentKeyword').textContent = status.current_keyword || 0;
            document.getElementById('totalKeywords').textContent = status.total_keywords || 0;
            document.getElementById('foundInfluencers').textContent = status.found_influencers || 0;
            document.getElementById('taskStatus').textContent = getStatusText(status.status);
            document.getElementById('progressMessage').textContent = status.progress_message || '';
            
            // 检查任务是否完成
            if (status.status === 'completed') {
                clearInterval(progressInterval);
                await loadResults();
                showAlert('搜索完成！', 'success');
            } else if (status.status === 'failed') {
                clearInterval(progressInterval);
                showAlert(`搜索失败: ${status.error_message}`, 'danger');
            }
        }
        
    } catch (error) {
        console.error('获取进度失败:', error);
    }
}

// 加载搜索结果
async function loadResults() {
    try {
        const response = await fetch(`/api/results/${currentTaskId}`);
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.summary, result.results);
            document.getElementById('progressContainer').style.display = 'none';
            document.getElementById('resultsContainer').style.display = 'block';
            document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
        }
        
    } catch (error) {
        console.error('加载结果失败:', error);
        showAlert('加载结果失败', 'danger');
    }
}

// 显示搜索结果
function displayResults(summary, results) {
    // 显示摘要统计
    const summaryHtml = `
        <div class="col-md-2 text-center">
            <div class="h4 mb-0 text-primary">${summary.total_influencers}</div>
            <small class="text-muted">总influencer数</small>
        </div>
        <div class="col-md-2 text-center">
            <div class="h4 mb-0 text-info">${summary.unique_channels}</div>
            <small class="text-muted">独立频道数</small>
        </div>
        <div class="col-md-2 text-center">
            <div class="h4 mb-0 text-success">${formatNumber(summary.avg_subscriber_count)}</div>
            <small class="text-muted">平均订阅数</small>
        </div>
        <div class="col-md-2 text-center">
            <div class="h4 mb-0 text-warning">${formatNumber(summary.max_subscriber_count)}</div>
            <small class="text-muted">最高订阅数</small>
        </div>
        <div class="col-md-2 text-center">
            <div class="h4 mb-0 text-info">${formatNumber(summary.avg_video_view_count)}</div>
            <small class="text-muted">平均观看数</small>
        </div>
        <div class="col-md-2 text-center">
            <div class="h4 mb-0 text-danger">${formatNumber(summary.max_video_view_count)}</div>
            <small class="text-muted">最高观看数</small>
        </div>
    `;
    document.getElementById('summaryStats').innerHTML = summaryHtml;
    
    // 显示结果表格
    const tableBody = document.getElementById('resultsTable');
    tableBody.innerHTML = '';
    
    results.forEach(influencer => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <div>
                        <div class="fw-bold">${escapeHtml(influencer.channel_name)}</div>
                        <small class="text-muted">${influencer.channel_country || 'US'}</small>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge bg-primary">${formatNumber(influencer.subscriber_count)}</span>
            </td>
            <td>
                <span class="badge bg-info">${escapeHtml(influencer.product_reviewed)}</span>
            </td>
            <td>
                <div style="max-width: 200px;">
                    <div class="text-truncate" title="${escapeHtml(influencer.video_title)}">
                        ${escapeHtml(influencer.video_title)}
                    </div>
                </div>
            </td>
            <td>
                <span class="badge bg-success">${formatNumber(influencer.video_view_count)}</span>
            </td>
            <td>
                <small>${formatDate(influencer.video_published_at)}</small>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <a href="${influencer.channel_url}" target="_blank" class="btn btn-outline-primary btn-sm">
                        <i class="fab fa-youtube"></i> 频道
                    </a>
                    <a href="${influencer.video_url}" target="_blank" class="btn btn-outline-success btn-sm">
                        <i class="fas fa-play"></i> 视频
                    </a>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// 下载结果
async function downloadResults() {
    if (!currentTaskId) {
        showAlert('没有可下载的结果', 'warning');
        return;
    }
    
    try {
        window.open(`/api/download/${currentTaskId}`, '_blank');
    } catch (error) {
        console.error('下载失败:', error);
        showAlert('下载失败', 'danger');
    }
}

// 显示搜索历史
async function showHistory() {
    try {
        const response = await fetch('/api/history');
        const result = await response.json();
        
        if (result.success) {
            displayHistory(result.history);
            document.getElementById('historyContainer').style.display = 'block';
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('progressContainer').style.display = 'none';
            document.getElementById('historyContainer').scrollIntoView({ behavior: 'smooth' });
        }
        
    } catch (error) {
        console.error('获取搜索历史失败:', error);
        showAlert('获取搜索历史失败', 'danger');
    }
}

// 显示历史记录
function displayHistory(history) {
    const tableBody = document.getElementById('historyTable');
    tableBody.innerHTML = '';
    
    history.forEach(task => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(task.product_name)}</td>
            <td>
                <span class="badge status-badge ${getStatusBadgeClass(task.status)}">
                    ${getStatusText(task.status)}
                </span>
            </td>
            <td>
                <span class="badge bg-info">${task.found_influencers || 0}</span>
            </td>
            <td>
                <small>${formatDate(task.created_at)}</small>
            </td>
            <td>
                ${task.status === 'completed' ? 
                    `<button class="btn btn-sm btn-outline-primary" onclick="viewTaskResults('${task.task_id}')">
                        <i class="fas fa-eye"></i> 查看
                    </button>` : 
                    '<span class="text-muted">-</span>'
                }
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// 查看历史任务结果
async function viewTaskResults(taskId) {
    currentTaskId = taskId;
    await loadResults();
    hideHistory();
}

// 隐藏历史记录
function hideHistory() {
    document.getElementById('historyContainer').style.display = 'none';
}

// 新搜索
function newSearch() {
    // 重置表单和界面
    document.getElementById('searchForm').reset();
    document.getElementById('minSubscribers').value = '10000';
    document.getElementById('minViewCount').value = '5000';
    document.getElementById('validateKeyBtn').innerHTML = '<i class="fas fa-check"></i> 验证';
    
    // 隐藏结果和进度
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('historyContainer').style.display = 'none';
    
    // 清理任务状态
    currentTaskId = null;
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 检查正在运行的任务
async function checkRunningTasks() {
    try {
        const response = await fetch('/api/running-tasks');
        const result = await response.json();
        
        if (result.success && result.running_tasks.length > 0) {
            const task = result.running_tasks[0]; // 取第一个运行中的任务
            currentTaskId = task.task_id;
            showProgressSection(task.product_name);
            startProgressMonitoring();
            showAlert('检测到正在运行的搜索任务，已自动连接', 'info');
        }
        
    } catch (error) {
        console.error('检查运行任务失败:', error);
    }
}

// 工具函数
function showAlert(message, type = 'info') {
    // 移除现有的alert
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

function formatNumber(num) {
    if (!num) return '0';
    return num.toLocaleString();
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getStatusText(status) {
    const statusMap = {
        'pending': '等待中',
        'running': '运行中',
        'completed': '已完成',
        'failed': '失败'
    };
    return statusMap[status] || status;
}

function getStatusBadgeClass(status) {
    const classMap = {
        'pending': 'bg-secondary',
        'running': 'bg-primary',
        'completed': 'bg-success',
        'failed': 'bg-danger'
    };
    return classMap[status] || 'bg-secondary';
}