
import { getAccessToken } from '../features/auth/storage/authStorage'
import axios from 'axios'

const trimTrailingSlash = (value) => {
  if (!value) return value
  return value.endsWith('/') ? value.slice(0, -1) : value
}

const make = (baseURL) => {
  const instance = axios.create({ baseURL: trimTrailingSlash(baseURL) })

  instance.interceptors.request.use((config) => {
    const at = getAccessToken()
    if (at) config.headers.Authorization = `Bearer ${at}`
    return config
  })

  return instance
}

export const loadingHttp = make(import.meta.env?.VITE_LOADING_SERVICE_URL || 'http://192.168.0.110:8001')
export const metricsHttp = make(import.meta.env?.VITE_METRICS_SERVICE_URL || 'http://192.168.0.110:8002')
