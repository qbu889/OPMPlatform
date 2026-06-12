/**
 * CityColor 颜色提取系统 - API 封装
 */
const API_BASE = '/api/city-color'

export default {
  /** 提取颜色 */
  extract(params) {
    return fetch(`${API_BASE}/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    }).then(r => r.json())
  },

  /** 获取方案列表 */
  getSchemes(page = 1, pageSize = 20) {
    return fetch(`${API_BASE}/schemes?page=${page}&page_size=${pageSize}`)
      .then(r => r.json())
  },

  /** 获取单个方案 */
  getScheme(id) {
    return fetch(`${API_BASE}/schemes/${id}`)
      .then(r => r.json())
  },

  /** 保存方案 */
  saveScheme(data) {
    return fetch(`${API_BASE}/schemes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json())
  },

  /** 更新方案 */
  updateScheme(id, data) {
    return fetch(`${API_BASE}/schemes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json())
  },

  /** 删除方案 */
  deleteScheme(id) {
    return fetch(`${API_BASE}/schemes/${id}`, { method: 'DELETE' })
      .then(r => r.json())
  },

  /** 获取配色类型列表 */
  getPaletteTypes() {
    return fetch(`${API_BASE}/palette-types`)
      .then(r => r.json())
  },

  /** 导出PNG */
  exportPNG(params) {
    return fetch(`${API_BASE}/export/png`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    }).then(r => r.blob())
  }
}