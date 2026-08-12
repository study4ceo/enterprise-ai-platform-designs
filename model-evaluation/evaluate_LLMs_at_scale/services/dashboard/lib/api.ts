import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
const ANALYTICS_BASE_URL = process.env.NEXT_PUBLIC_ANALYTICS_URL || 'http://localhost:8003/api/v1'

// Create axios instance with auth interceptor
const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

const analyticsClient = axios.create({
  baseURL: ANALYTICS_BASE_URL,
})

// Add auth token to requests
const addAuthToken = (config: any) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

apiClient.interceptors.request.use(addAuthToken)
analyticsClient.interceptors.request.use(addAuthToken)

export const api = {
  // Auth
  async login(email: string, password: string) {
    const response = await apiClient.post('/auth/login', { email, password })
    localStorage.setItem('token', response.data.access_token)
    return response.data
  },

  async register(email: string, password: string) {
    const response = await apiClient.post('/auth/register', { email, password })
    return response.data
  },

  async getCurrentUser() {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  // Jobs
  async getJobs(params?: any) {
    const response = await apiClient.get('/jobs', { params })
    return response.data
  },

  async getJob(id: string) {
    const response = await apiClient.get(`/jobs/${id}`)
    return response.data
  },

  async createJob(data: any) {
    const response = await apiClient.post('/jobs', data)
    return response.data
  },

  async deleteJob(id: string) {
    const response = await apiClient.delete(`/jobs/${id}`)
    return response.data
  },

  async getJobTasks(id: string) {
    const response = await apiClient.get(`/jobs/${id}/tasks`)
    return response.data
  },

  async getJobResults(id: string) {
    const response = await apiClient.get(`/jobs/${id}/results`)
    return response.data
  },

  // Analytics
  async getDashboardStats() {
    const response = await analyticsClient.get('/dashboard/stats')
    return response.data
  },

  async getJobAnalytics(id: string) {
    const response = await analyticsClient.get(`/jobs/${id}/analytics`)
    return response.data
  },

  async getModelComparison(params?: any) {
    const response = await analyticsClient.get('/models/comparison', { params })
    return response.data
  },

  async getCostBreakdown(params?: any) {
    const response = await analyticsClient.get('/costs/breakdown', { params })
    return response.data
  },

  async getDeploymentReadiness() {
    const response = await analyticsClient.get('/deployment/readiness')
    return response.data
  },

  async exportJob(id: string, format: 'json' | 'csv' | 'pdf' = 'json') {
    const response = await analyticsClient.get(`/export/${id}`, {
      params: { format }
    })
    return response.data
  },

  async chatQuery(query: string) {
    const response = await analyticsClient.post('/chat/query', { query })
    return response.data
  },

  // Health
  async getHealth() {
    const response = await apiClient.get('/health')
    return response.data
  },
}

export default api
