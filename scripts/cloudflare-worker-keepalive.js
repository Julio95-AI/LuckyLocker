/**
 * Cloudflare Worker - 防止Render自动休眠
 * 
 * 使用方法：
 * 1. 登录 Cloudflare Dashboard
 * 2. 点击 "Workers & Pages" -> "Create Application" -> "Create Worker"
 * 3. 复制此代码到编辑器
 * 4. 点击 "Save and Deploy"
 * 5. 点击 "Triggers" -> "Add Cron Trigger"
 * 6. 输入：*/10 * * * * (每10分钟执行一次)
 */

export default {
  // 定时任务触发器
  async scheduled(event, env, ctx) {
    try {
      // 替换为你的域名
      const response = await fetch('https://julio98.dpdns.org/api/system/config', {
        method: 'GET',
        headers: {
          'User-Agent': 'Cloudflare-Worker-KeepAlive'
        }
      });
      
      console.log('Keep-alive ping successful:', response.status);
    } catch (error) {
      console.error('Keep-alive ping failed:', error);
    }
  },

  // HTTP请求处理（可选，用于测试）
  async fetch(request, env, ctx) {
    return new Response('LuckyLocker Keep-Alive Worker is running!', {
      headers: { 'content-type': 'text/plain' }
    });
  }
};
