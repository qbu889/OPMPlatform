/**
 * 彩色抽奖转盘 - API 服务层
 * 封装所有后端接口调用，统一管理请求地址和异常处理。
 */

/**
 * 获取转盘配置
 * @returns {Promise<Object>} 包含 code, msg, data 的响应对象
 */
export async function getWheelConfig() {
  const res = await fetch('/api/wheel-lottery/config', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
  return res.json()
}

/**
 * 保存/更新转盘配置
 * @param {Array} items - 分区列表 [{id, name, color, weight}]
 * @returns {Promise<Object>} 包含 code, msg 的响应对象
 */
export async function saveWheelConfig(items) {
  const res = await fetch('/api/wheel-lottery/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items }),
  })
  return res.json()
}

/**
 * 执行抽奖
 * @returns {Promise<Object>} 包含 code, msg, data(中奖分区) 的响应对象
 */
export async function drawWheel() {
  const res = await fetch('/api/wheel-lottery/draw', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  return res.json()
}

/**
 * 重置配置为默认分区
 * @returns {Promise<Object>} 包含 code, msg, data 的响应对象
 */
export async function resetWheel() {
  const res = await fetch('/api/wheel-lottery/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  return res.json()
}