import React from 'react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'

import Login from '../pages/Login.jsx'

const loginMock = vi.fn()
const navigateMock = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

vi.mock('../state/auth.jsx', () => ({
  useAuth: () => ({ login: loginMock }),
}))

describe('Login', () => {
  beforeEach(() => {
    loginMock.mockReset()
    navigateMock.mockReset()
  })

  it('submits credentials and navigates to / on success', async () => {
    loginMock.mockResolvedValueOnce(undefined)
    render(<Login />)

    const inputs = screen.getAllByRole('textbox')
    fireEvent.change(inputs[0], { target: { value: 'student1' } })
    // password input role is textbox too in jsdom
    fireEvent.change(inputs[1], { target: { value: 'student123' } })
    fireEvent.click(screen.getByRole('button', { name: /login/i }))

    await Promise.resolve()

    expect(loginMock).toHaveBeenCalledWith('student1', 'student123')
    expect(navigateMock).toHaveBeenCalledWith('/')
  })

  it('shows error on failed login', async () => {
    loginMock.mockRejectedValueOnce({ response: { data: { error: { message: 'Bad creds' } } } })
    render(<Login />)

    fireEvent.click(screen.getByRole('button', { name: /login/i }))
    await Promise.resolve()

    expect(screen.getByText('Bad creds')).toBeInTheDocument()
  })
})
