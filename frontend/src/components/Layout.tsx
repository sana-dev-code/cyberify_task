import { Outlet } from 'react-router-dom'

export function Layout() {
  return (
    <div className="h-full min-h-screen bg-chat-bg">
      <Outlet />
    </div>
  )
}
