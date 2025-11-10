// ========================================
// Block Trade DT V2 - 现代化交互脚本
// ========================================

// 全局变量
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ========================================
// 自定义光标效果
// ========================================

function initCustomCursor() {
  if (window.innerWidth < 768) return; // 移动端不启用
  
  const cursor = $('.custom-cursor');
  const cursorDot = $('.cursor-dot');
  const cursorOutline = $('.cursor-outline');
  
  if (!cursor) return;
  
  let mouseX = 0, mouseY = 0;
  let cursorX = 0, cursorY = 0;
  let cursorOutlineX = 0, cursorOutlineY = 0;
  
  // 跟随鼠标移动
  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });
  
  // 平滑动画
  function animateCursor() {
    // 光标点快速跟随
    cursorX += (mouseX - cursorX) * 0.5;
    cursorY += (mouseY - cursorY) * 0.5;
    cursorDot.style.transform = `translate(${cursorX}px, ${cursorY}px)`;
    
    // 光标轮廓缓慢跟随
    cursorOutlineX += (mouseX - cursorOutlineX) * 0.15;
    cursorOutlineY += (mouseY - cursorOutlineY) * 0.15;
    cursorOutline.style.transform = `translate(${cursorOutlineX}px, ${cursorOutlineY}px)`;
    
    requestAnimationFrame(animateCursor);
  }
  
  animateCursor();
  
  // 悬停在可点击元素上
  const interactiveElements = $$('a, button, input, .card-hover, .nav-link, .suggestion-chip');
  
  interactiveElements.forEach(el => {
    el.addEventListener('mouseenter', () => {
      document.body.classList.add('cursor-hover');
    });
    
    el.addEventListener('mouseleave', () => {
      document.body.classList.remove('cursor-hover');
    });
  });
}

// ========================================
// 滑动分屏功能
// ========================================

function initFullpageScroll() {
  const sections = $$('.section');
  const indicators = $$('.indicator-item');
  const navLinks = $$('.nav-link');
  
  // 滚动观察器
  const observerOptions = {
    root: null,
    threshold: 0.5,
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const sectionId = entry.target.id;
        
        // 更新指示器
        indicators.forEach(indicator => {
          indicator.classList.remove('active');
          if (indicator.dataset.target === sectionId) {
            indicator.classList.add('active');
          }
        });
        
        // 更新导航
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.dataset.section === sectionId) {
            link.classList.add('active');
          }
        });
      }
    });
  }, observerOptions);
  
  sections.forEach(section => observer.observe(section));
  
  // 指示器点击事件
  indicators.forEach(indicator => {
    indicator.addEventListener('click', () => {
      const targetId = indicator.dataset.target;
      scrollToSection(targetId);
    });
  });
  
  // 导航链接点击
  navLinks.forEach(link => {
    if (link.dataset.section) {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.dataset.section;
        scrollToSection(targetId);
      });
    }
  });
}

// 滚动到指定区域
function scrollToSection(sectionId) {
  const section = $(`#${sectionId}`);
  if (section) {
    section.scrollIntoView({ behavior: 'smooth' });
  }
}

// ========================================
// GSAP动画效果
// ========================================

function initGSAPAnimations() {
  if (typeof gsap === 'undefined') return;
  
  gsap.registerPlugin(ScrollTrigger);
  
  // 文本逐字显现
  $$('.reveal-text').forEach(text => {
    gsap.from(text, {
      scrollTrigger: {
        trigger: text,
        start: 'top 80%',
      },
      y: 30,
      opacity: 0,
      duration: 0.8,
      ease: 'power3.out',
      onComplete: () => {
        text.classList.add('revealed');
      }
    });
  });
  
  // 卡片渐入动画
  $$('.data-card, .news-card').forEach((card, index) => {
    gsap.from(card, {
      scrollTrigger: {
        trigger: card,
        start: 'top 85%',
      },
      y: 50,
      opacity: 0,
      duration: 0.6,
      delay: index * 0.1,
      ease: 'power2.out'
    });
  });
}

// ========================================
// 懒加载图片
// ========================================

function initLazyLoad() {
  if (typeof LazyLoad !== 'undefined') {
    const lazyLoadInstance = new LazyLoad({
      elements_selector: '.lazy',
      threshold: 300,
      callback_loaded: (el) => {
        el.classList.add('loaded');
      }
    });
  }
}

// ========================================
// 数字动画
// ========================================

function animateNumber(element, target, duration = 2000) {
  const start = 0;
  const increment = target / (duration / 16);
  let current = start;
  
  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    element.textContent = Math.round(current).toLocaleString();
  }, 16);
}

function initNumberAnimations() {
  const statValues = $$('.stat-value[data-value]');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
        entry.target.classList.add('animated');
        const target = parseInt(entry.target.dataset.value);
        animateNumber(entry.target, target);
      }
    });
  }, { threshold: 0.5 });
  
  statValues.forEach(el => observer.observe(el));
}

// ========================================
// 实时数据更新
// ========================================

function updateMarketData() {
  // 模拟实时数据
  const indexValue = $('#indexValue');
  const indexChange = $('#indexChange');
  
  if (indexValue) {
    const baseValue = 3666.44;
    const change = (Math.random() - 0.5) * 10;
    const newValue = (baseValue + change).toFixed(2);
    indexValue.textContent = newValue.toLocaleString();
    
    const changePercent = ((change / baseValue) * 100).toFixed(2);
    indexChange.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent}%`;
    indexChange.className = `value-change ${changePercent >= 0 ? 'positive' : 'negative'}`;
  }
}

function populateHotStocks() {
  const tbody = $('#hotStocksTable');
  if (!tbody) return;
  
  const mockData = [
    { rank: 1, code: '000001', name: '平安银行', price: 12.34, change: 2.5, amount: 12345.6 },
    { rank: 2, code: '000002', name: '万科A', price: 18.56, change: -1.2, amount: 9876.5 },
    { rank: 3, code: '000858', name: '五粮液', price: 156.78, change: 3.4, amount: 8765.4 },
    { rank: 4, code: '002415', name: '海康威视', price: 34.56, change: 1.8, amount: 6543.2 },
    { rank: 5, code: '600036', name: '招商银行', price: 45.67, change: -0.9, amount: 5432.1 }
  ];
  
  tbody.innerHTML = mockData.map(stock => `
    <tr>
      <td>${stock.rank}</td>
      <td>${stock.code}</td>
      <td>${stock.name}</td>
      <td>¥${stock.price}</td>
      <td class="value-change ${stock.change >= 0 ? 'positive' : 'negative'}">
        ${stock.change >= 0 ? '+' : ''}${stock.change}%
      </td>
      <td>${stock.amount.toLocaleString()}</td>
    </tr>
  `).join('');
}

// ========================================
// 搜索功能
// ========================================

async function performSearch() {
  const query = $('#query').value.trim();
  const topk = parseInt($('#topk').value) || 10;
  const useLLM = $('#use_llm').checked;
  
  if (!query) {
    $('#query').focus();
    return;
  }
  
  showLoading();
  
  const resultsSection = $('#resultsSection');
  const summaryEl = $('#summary');
  const resultsEl = $('#results');
  const countEl = $('#result-count');
  const searchTimeEl = $('#searchTime');
  
  resultsSection.style.display = 'block';
  summaryEl.textContent = '';
  countEl.textContent = '搜索中...';
  resultsEl.innerHTML = '<div class="loading-spinner"></div>';
  
  const startTime = Date.now();
  
  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topk, use_llm: useLLM })
    });
    
    if (!response.ok) {
      throw new Error('搜索失败');
    }
    
    const data = await response.json();
    const endTime = Date.now();
    // 使用API返回的search_time，如果没有则使用本地计算
    const searchTime = data.search_time || ((endTime - startTime) / 1000).toFixed(2) + '秒';
    
    searchTimeEl.textContent = searchTime;
    summaryEl.innerHTML = data.summary ? `<div class="ai-summary-content"><p>${data.summary}</p></div>` : '';
    countEl.textContent = `共找到 ${data.total || data.results.length} 条结果`;
    
    resultsEl.innerHTML = data.results.map(r => {
      const l = r.listing;
      return `
        <div class="data-card card-hover">
          <h3>${l.title}</h3>
          <div class="card-tags">
            ${l.category ? `<span class="tag">${l.category}</span>` : ''}
            ${l.region ? `<span class="tag">${l.region}</span>` : ''}
          </div>
          <p class="ai-insight">${l.description || ''}</p>
          <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
            <span style="color: var(--text-muted); font-size: 0.875rem;">
              ${l.price ? `价格: ${l.price}${l.unit || ''}` : ''}
            </span>
            <span style="color: var(--primary-color); font-weight: 600;">
              匹配度: ${r.score.toFixed(3)}
            </span>
          </div>
        </div>
      `;
    }).join('');
    
  } catch (error) {
    resultsEl.innerHTML = `<div style="color: var(--error-color);">搜索失败: ${error.message}</div>`;
  } finally {
    hideLoading();
  }
}

// ========================================
// AI聊天功能
// ========================================

function addMessageToChat(role, content) {
  const chatMessages = $('#chatMessages');
  if (!chatMessages) return;
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;
  messageDiv.innerHTML = `
    <div class="message-avatar">${role === 'user' ? '👤' : '🤖'}</div>
    <div class="message-content">
      <p>${content}</p>
    </div>
  `;
  
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function handleAIChat() {
  const messageInput = $('#aiMessageInput');
  const message = messageInput.value.trim();
  
  if (!message) return;
  
  addMessageToChat('user', message);
  messageInput.value = '';
  
  addMessageToChat('assistant', '正在思考...');
  
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        system_prompt: "你是一个专业的金融分析师，专门分析大宗交易数据。请用中文回答，语言要专业、准确。"
      })
    });
    
    const data = await response.json();
    
    // 移除"正在思考..."消息
    const chatMessages = $('#chatMessages');
    if (chatMessages && chatMessages.lastChild) {
      chatMessages.removeChild(chatMessages.lastChild);
    }
    
    addMessageToChat('assistant', data.response || '抱歉，AI服务暂时不可用。');
    
  } catch (error) {
    console.error('AI聊天失败:', error);
    const chatMessages = $('#chatMessages');
    if (chatMessages && chatMessages.lastChild) {
      chatMessages.removeChild(chatMessages.lastChild);
    }
    addMessageToChat('assistant', '抱歉，AI服务暂时不可用，请稍后重试。');
  }
}

function clearChat() {
  const chatMessages = $('#chatMessages');
  if (!chatMessages) return;
  
  chatMessages.innerHTML = `
    <div class="message assistant">
      <div class="message-avatar">🤖</div>
      <div class="message-content">
        <p>您好！我是您的专业金融分析助手。我可以帮您：</p>
        <ul>
          <li>分析大宗交易市场数据</li>
          <li>解读K线图和趋势</li>
          <li>提供投资建议和风险评估</li>
        </ul>
      </div>
    </div>
  `;
}

// ========================================
// 东方财富网数据加载
// ========================================

async function loadEastMoneyData() {
  try {
    const response = await fetch('/api/eastmoney/data');
    const data = await response.json();
    
    if (data.success && data.data) {
      updateMarketOverview(data.data.market_overview);
      updateHotStocks(data.data.hot_stocks);
    }
  } catch (error) {
    console.error('加载东方财富网数据失败:', error);
  }
}

function updateMarketOverview(marketData) {
  // 更新上证指数
  const indexValue = $('#indexValue');
  const indexChange = $('#indexChange');
  
  if (indexValue && marketData.shanghai_index) {
    indexValue.textContent = marketData.shanghai_index.toFixed(2);
  }
  
  if (indexChange && marketData.shanghai_change) {
    const change = marketData.shanghai_change;
    indexChange.textContent = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
    indexChange.className = `value-change ${change >= 0 ? 'positive' : 'negative'}`;
  }
}

function updateHotStocks(stocks) {
  const hotStocksTable = $('#hotStocksTable');
  if (!hotStocksTable || !stocks) return;
  
  hotStocksTable.innerHTML = stocks.slice(0, 10).map((stock, index) => `
    <tr>
      <td>${index + 1}</td>
      <td>${stock.code || 'N/A'}</td>
      <td>${stock.name || 'N/A'}</td>
      <td>${stock.price || 'N/A'}</td>
      <td class="${stock.change && stock.change.includes('-') ? 'negative' : 'positive'}">
        ${stock.change || 'N/A'}
      </td>
      <td>${stock.amount || 'N/A'}</td>
    </tr>
  `).join('');
}

// ========================================

async function loadLatestNews() {
  const newsGrid = $('#newsGrid');
  if (!newsGrid) return;
  
  try {
    const response = await fetch('/api/news/latest?limit=6');
    const news = await response.json();
    
    newsGrid.innerHTML = news.map(item => {
      // 使用新闻的URL，如果没有则使用默认链接
      const newsUrl = item.url || `https://finance.sina.com.cn/stock/marketresearch/`;
      return `
      <div class="news-card" onclick="window.open('${newsUrl}', '_blank')" style="cursor: pointer;">
        <img class="lazy news-image" data-src="${item.image || 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&q=80'}" alt="${item.title}" />
        <div class="news-content">
          <div class="news-meta">
            <span>📅 ${item.time}</span>
            <span>📰 ${item.source}</span>
          </div>
          <h3 class="news-title">${item.title}</h3>
          <p class="news-summary">${item.summary}</p>
        </div>
      </div>
    `;
    }).join('');
    
    // 重新初始化懒加载
    initLazyLoad();
    
  } catch (error) {
    console.error('加载新闻失败:', error);
    newsGrid.innerHTML = `
      <div class="data-card" style="grid-column: 1 / -1;">
        <p style="color: var(--text-muted); text-align: center;">暂无最新新闻</p>
      </div>
    `;
  }
}

// ========================================
// 工具函数
// ========================================

function showLoading() {
  const loading = $('#loadingOverlay');
  if (loading) loading.style.display = 'flex';
}

function hideLoading() {
  const loading = $('#loadingOverlay');
  if (loading) loading.style.display = 'none';
}

// ========================================
// 事件监听
// ========================================

function initEventListeners() {
  // 搜索按钮
  const searchBtn = $('#search-btn');
  if (searchBtn) {
    searchBtn.addEventListener('click', performSearch);
  }
  
  // 搜索输入框回车
  const queryInput = $('#query');
  if (queryInput) {
    queryInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') performSearch();
    });
  }
  
  // 搜索建议
  $$('.suggestion-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const query = chip.dataset.query;
      if ($('#query')) {
        $('#query').value = query;
        performSearch();
      }
    });
  });
  
  // AI聊天输入框回车
  const aiInput = $('#aiMessageInput');
  if (aiInput) {
    aiInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleAIChat();
    });
  }
  
  // 导航栏滚动隐藏
  let lastScroll = 0;
  const header = $('#mainHeader');
  
  window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > lastScroll && currentScroll > 100) {
      header?.classList.add('header-hidden');
    } else {
      header?.classList.remove('header-hidden');
    }
    
    lastScroll = currentScroll;
  });
}

// ========================================
// 初始化
// ========================================

document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Block Trade DT V2 初始化中...');
  
  // 初始化各个功能模块
  initCustomCursor();
  initFullpageScroll();
  initGSAPAnimations();
  initLazyLoad();
  initNumberAnimations();
  initEventListeners();
  
  // 加载初始数据
  populateHotStocks();
  loadLatestNews();
  loadEastMoneyData(); // 加载东方财富网数据
  
  // 定时更新市场数据
  setInterval(updateMarketData, 5000);
  setInterval(loadEastMoneyData, 30000); // 每30秒更新东方财富网数据
  
  // 定时刷新新闻
  setInterval(loadLatestNews, 60000);
  
  console.log('✅ Block Trade DT V2 初始化完成！');
});

// 全局函数供HTML调用
window.scrollToSection = scrollToSection;
window.performSearch = performSearch;
window.handleAIChat = handleAIChat;
window.clearChat = clearChat;


