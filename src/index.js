import { Hono } from 'hono';
import { serveStatic } from 'hono/cloudflare-workers';
import { jwtVerify } from 'jose';

const app = new Hono();

// 中间件：CORS
app.use('*', async (c, next) => {
  c.header('Access-Control-Allow-Origin', '*');
  c.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  c.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (c.req.method === 'OPTIONS') {
    return c.text('', 200);
  }
  
  await next();
});

// 静态文件服务
app.use('/static/*', serveStatic({ root: './' }));

// 首页路由
app.get('/', async (c) => {
  const html = await c.env.BLOCK_TRADE_KV.get('index.html');
  if (html) {
    return c.html(html);
  }
  return c.html('<h1>Block Trade DT</h1><p>正在部署中...</p>');
});

// 趋势页面
app.get('/trends', async (c) => {
  const html = await c.env.BLOCK_TRADE_KV.get('trends.html');
  if (html) {
    return c.html(html);
  }
  return c.html('<h1>实时趋势</h1><p>正在部署中...</p>');
});

// API路由
app.get('/api/trends/data', async (c) => {
  // 模拟市场数据
  const marketData = {
    market_data: {
      shanghai_index: Math.round((3600 + Math.random() * 200 - 100) * 100) / 100,
      shanghai_change: Math.round((Math.random() * 4 - 2) * 100) / 100,
      total_volume: Math.round((Math.random() * 30000 + 50000) * 100) / 100,
      premium_volume: Math.round((Math.random() * 300 + 200) * 100) / 100,
      discount_volume: Math.round((Math.random() * 30000 + 45000) * 100) / 100
    },
    daily_stats: generateDailyStats()
  };
  
  return c.json(marketData);
});

// 搜索API
app.post('/api/search', async (c) => {
  const body = await c.req.json();
  const { query, top_k = 10, use_llm = false } = body;
  
  // 模拟搜索结果
  const results = generateMockResults(query, top_k);
  
  return c.json({
    results,
    summary: use_llm ? `关于"${query}"的搜索结果摘要...` : null,
    total: results.length
  });
});

// AI聊天API
app.post('/api/chat', async (c) => {
  const body = await c.req.json();
  const { message } = body;
  
  // 调用智谱AI API
  try {
    const response = await fetch('https://open.bigmodel.cn/api/paas/v4/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${c.env.ZHIPU_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'glm-4',
        messages: [
          {
            role: 'system',
            content: '你是一个专业的金融分析师，请用中文回答用户的问题。'
          },
          {
            role: 'user',
            content: message
          }
        ],
        temperature: 0.7
      })
    });
    
    const data = await response.json();
    const aiResponse = data.choices?.[0]?.message?.content || '抱歉，AI服务暂时不可用。';
    
    return c.json({
      response: aiResponse,
      timestamp: new Date().toISOString(),
      success: true
    });
  } catch (error) {
    return c.json({
      response: '抱歉，AI服务暂时不可用。',
      timestamp: new Date().toISOString(),
      success: false
    });
  }
});

// 用户注册
app.post('/api/register', async (c) => {
  const body = await c.req.json();
  const { username, email, password, full_name } = body;
  
  // 检查用户是否已存在
  const existingUser = await c.env.BLOCK_TRADE_KV.get(`user:${username}`);
  if (existingUser) {
    return c.json({ error: '用户名已存在' }, 400);
  }
  
  // 创建用户（简化版，实际应该加密密码）
  const user = {
    username,
    email,
    full_name,
    created_at: new Date().toISOString()
  };
  
  await c.env.BLOCK_TRADE_KV.put(`user:${username}`, JSON.stringify(user));
  
  return c.json({ message: '注册成功' });
});

// 用户登录
app.post('/api/login', async (c) => {
  const body = await c.req.json();
  const { username, password } = body;
  
  // 验证用户（简化版）
  const userData = await c.env.BLOCK_TRADE_KV.get(`user:${username}`);
  if (!userData) {
    return c.json({ error: '用户名或密码错误' }, 401);
  }
  
  const user = JSON.parse(userData);
  
  // 生成JWT token（简化版）
  const token = await generateJWT(user.username, c.env.JWT_SECRET_KEY);
  
  return c.json({
    access_token: token,
    token_type: 'bearer',
    user: {
      username: user.username,
      email: user.email,
      full_name: user.full_name
    }
  });
});

// 辅助函数
function generateDailyStats() {
  const stats = [];
  for (let i = 29; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    stats.push({
      date: date.toISOString().split('T')[0],
      index: Math.round((3600 + Math.random() * 300 - 150) * 100) / 100,
      change: Math.round((Math.random() * 6 - 3) * 100) / 100,
      total_volume: Math.round((Math.random() * 50000 + 40000) * 100) / 100,
      premium_volume: Math.round((Math.random() * 700 + 100) * 100) / 100,
      premium_ratio: Math.round((Math.random() * 2 + 0.5) * 100) / 100,
      discount_volume: Math.round((Math.random() * 50000 + 35000) * 100) / 100,
      discount_ratio: Math.round((Math.random() * 2 + 97.5) * 100) / 100
    });
  }
  return stats;
}

function generateMockResults(query, topK) {
  const mockResults = [
    {
      id: 1,
      title: `${query}相关交易记录`,
      content: `这是关于${query}的详细交易信息...`,
      score: 0.95,
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      title: `${query}市场分析报告`,
      content: `基于${query}的市场趋势分析...`,
      score: 0.87,
      timestamp: new Date().toISOString()
    },
    {
      id: 3,
      title: `${query}投资建议`,
      content: `针对${query}的专业投资建议...`,
      score: 0.82,
      timestamp: new Date().toISOString()
    }
  ];
  
  return mockResults.slice(0, topK);
}

async function generateJWT(username, secret) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  
  const header = { alg: 'HS256', typ: 'JWT' };
  const payload = { sub: username, exp: Math.floor(Date.now() / 1000) + 3600 };
  
  const headerB64 = btoa(JSON.stringify(header));
  const payloadB64 = btoa(JSON.stringify(payload));
  const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(`${headerB64}.${payloadB64}`));
  
  return `${headerB64}.${payloadB64}.${btoa(String.fromCharCode(...new Uint8Array(signature)))}`;
}

export default app;
