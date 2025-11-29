import { metricsHttp } from './http'

export const fetchVersionMetrics = async (version) => {
  const { data } = await metricsHttp.get(`/${encodeURIComponent(version)}`)
  return data
}

export const fetchComparisonMetrics = async (v1, v2) => {
  const { data } = await metricsHttp.get(`/cmp/${encodeURIComponent(v1)}/${encodeURIComponent(v2)}`)
  return data
}
