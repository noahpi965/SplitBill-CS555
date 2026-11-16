import axios from 'axios'

const USER_KEY = 'splitbill_user'

export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    return null
  }
}

export function storeSession(payload) {
  const session = { ...payload.user, token: payload.token }
  localStorage.setItem(USER_KEY, JSON.stringify(session))
  return session
}

export function clearSession() {
  localStorage.removeItem(USER_KEY)
}

axios.interceptors.request.use((config) => {
  const session = getStoredUser()
  if (session?.token) {
    config.headers.Authorization = `Bearer ${session.token}`
  }
  return config
})

export default axios
