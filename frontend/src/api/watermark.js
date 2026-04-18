/**
 * 图片水印清除 API 工具函数
 */
import axios from 'axios'

const BASE_URL = '/api/watermark'

/**
 * 上传图片
 * @param {File} file - 图片文件
 * @returns {Promise} 上传结果
 */
export function uploadImage(file) {
  const formData = new FormData()
  formData.append('image', file)
  
  return axios.post(`${BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 手动框选去除水印
 * @param {Object} data - 处理参数
 * @param {string} data.filename - 文件名
 * @param {Array} data.bboxes - 边界框数组 [[x, y, w, h], ...]
 * @param {string} [data.algorithm='telea'] - 修复算法 (telea|ns)
 * @param {number} [data.radius=3] - 修复半径
 * @returns {Promise} 处理结果
 */
export function removeWatermark(data) {
  return axios.post(`${BASE_URL}/remove`, data)
}

/**
 * 自动识别并去除水印
 * @param {Object} data - 处理参数
 * @param {string} data.filename - 文件名
 * @param {string} [data.algorithm='telea'] - 修复算法 (telea|ns)
 * @param {number} [data.radius=3] - 修复半径
 * @returns {Promise} 处理结果
 */
export function autoRemoveWatermark(data) {
  return axios.post(`${BASE_URL}/auto-remove`, data)
}

/**
 * AI智能去除水印（使用IOPaint LaMa模型）
 * @param {Object} data - 处理参数
 * @param {string} data.filename - 文件名
 * @param {Array} data.bboxes - 边界框数组 [[x, y, w, h], ...]
 * @returns {Promise} 处理结果
 */
export function aiRemoveWatermark(data) {
  return axios.post(`${BASE_URL}/ai-remove`, data)
}

/**
 * 下载处理后的图片
 * @param {string} filename - 文件名
 * @returns {Promise} 下载链接
 */
export function downloadImage(filename) {
  return `${BASE_URL}/download/${filename}`
}

/**
 * 预览图片
 * @param {string} filename - 文件名
 * @returns {Promise} 图片URL
 */
export function previewImage(filename) {
  return `${BASE_URL}/preview/${filename}`
}

/**
 * 清理临时文件
 * @param {string} [filename] - 可选，指定清理特定文件
 * @returns {Promise} 清理结果
 */
export function cleanupTempFiles(filename) {
  const data = filename ? { filename } : {}
  return axios.post(`${BASE_URL}/cleanup`, data)
}
