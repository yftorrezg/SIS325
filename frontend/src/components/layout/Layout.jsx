import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import ChatWidget from '../chatbot/ChatWidget'

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-6 max-w-7xl">
        <Outlet />
      </main>
      <footer className="bg-blue-900 text-white text-center py-3 text-sm">
        <p>© 2024 Facultad de Tecnología - Universidad San Francisco Xavier de Chuquisaca</p>
      </footer>
      <ChatWidget />
    </div>
  )
}
