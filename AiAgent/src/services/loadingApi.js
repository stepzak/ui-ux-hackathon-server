import { loadingHttp } from './http'

export const uploadDataset = async ({ version, hitsFile, visitsFile }) => {
  const formData = new FormData()
  formData.append('version', version)
  formData.append('hits_file', hitsFile)
  formData.append('visits_file', visitsFile)

  const { data } = await loadingHttp.post('/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })

  return data
}
