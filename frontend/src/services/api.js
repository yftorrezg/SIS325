import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

// Attach token from localStorage
api.interceptors.request.use((config) => {
  try {
    const auth = JSON.parse(localStorage.getItem('usfx-auth') || '{}')
    const token = auth?.state?.token
    if (token) config.headers.Authorization = `Bearer ${token}`
  } catch {}
  return config
})

// Handle 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('usfx-auth')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const tramiteService = {
  list: (params = {}) => api.get('/tramites', { params }),
  search: (q) => api.get('/tramites/search', { params: { q } }),
  getById: (id) => api.get(`/tramites/${id}`),
  create: (data) => api.post('/tramites', data),
  update: (id, data) => api.put(`/tramites/${id}`, data),
  delete: (id) => api.delete(`/tramites/${id}`),
  addRequirement: (tramiteId, data) => api.post(`/tramites/${tramiteId}/requirements`, data),
  updateRequirement: (tramiteId, reqId, data) => api.put(`/tramites/${tramiteId}/requirements/${reqId}`, data),
  deleteRequirement: (tramiteId, reqId) => api.delete(`/tramites/${tramiteId}/requirements/${reqId}`),
}

export const careerService = {
  list: () => api.get('/careers'),
}

export const kardistaService = {
  list: () => api.get('/kardistas'),
  update: (id, data) => api.put(`/kardistas/${id}`, data),
}

export const requestService = {
  create: (data) => api.post('/requests', data),
  myRequests: () => api.get('/requests/my'),
  list: (params) => api.get('/requests', { params }),
  getById: (id) => api.get(`/requests/${id}`),
  updateStatus: (id, data) => api.put(`/requests/${id}/status`, data),
}

export const authService = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export const aiService = {
  chat: (data) => api.post('/ai/chat', data),
  classify: (text) => api.post('/ai/classify', { text }),
  transcribe: (formData) => api.post('/ai/transcribe', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
}

export const trainingService = {
  listSamples: (params) => api.get('/training/samples', { params }),
  countSamples: (params) => api.get('/training/samples/count', { params }),
  createSample: (data) => api.post('/training/samples', data),
  updateSample: (id, data) => api.put(`/training/samples/${id}`, data),
  verifySample: (id) => api.put(`/training/samples/${id}/verify`),
  deleteSample: (id) => api.delete(`/training/samples/${id}`),
  stats: () => api.get('/training/samples/stats'),
}

export const adminService = {
  stats: () => api.get('/admin/stats'),
}

export const notificationService = {
  list: () => api.get('/notifications'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
}

export const modelVersionService = {
  list: () => api.get('/model-versions'),
  activate: (id) => api.post(`/model-versions/${id}/activate`),
  delete: (id) => api.delete(`/model-versions/${id}`),
}
