import axios from 'axios'

export const login = async (username, password) => {
  const response = await fetch('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  })
  return response.json()
}

export const register = async (username, email, password) => {
  const response = await fetch('/api/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, email, password }),
  })
  return response.json()
}

export const logout = async () => {
  const response = await fetch('/api/logout', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  return response.json()
}

export const changePassword = async (oldPassword, newPassword, confirmNewPassword) => {
  const response = await fetch('/api/change-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmNewPassword,
    }),
  })
  return response.json()
}

export const forgotPassword = async (email) => {
  const response = await fetch('/api/forgot-password', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  })
  return response.json()
}
