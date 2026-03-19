import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/layout/Layout'
import Home from './pages/student/Home'
import TramitesIndex from './pages/student/TramitesIndex'
import TramiteDetailPage from './pages/student/TramiteDetailPage'
import MyRequests from './pages/student/MyRequests'
import Login from './pages/auth/Login'
import Dashboard from './pages/admin/Dashboard'
import TramitesManager from './pages/admin/TramitesManager'
import RequestsManager from './pages/admin/RequestsManager'
import TrainingManager from './pages/admin/TrainingManager'
import ModelEvaluation from './pages/admin/ModelEvaluation'
import KardistasInfo from './pages/student/KardistasInfo'

function ProtectedRoute({ children, roles }) {
  const { user, token } = useAuthStore()
  if (!token) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user?.role)) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="tramites" element={<TramitesIndex />} />
        <Route path="tramites/:id" element={<TramiteDetailPage />} />
        <Route path="kardistas" element={<KardistasInfo />} />
        <Route path="mis-solicitudes" element={
          <ProtectedRoute><MyRequests /></ProtectedRoute>
        } />
        <Route path="admin" element={
          <ProtectedRoute roles={['admin', 'kardista']}><Dashboard /></ProtectedRoute>
        } />
        <Route path="admin/tramites" element={
          <ProtectedRoute roles={['admin']}><TramitesManager /></ProtectedRoute>
        } />
        <Route path="admin/solicitudes" element={
          <ProtectedRoute roles={['admin', 'kardista']}><RequestsManager /></ProtectedRoute>
        } />
        <Route path="admin/entrenamiento" element={
          <ProtectedRoute roles={['admin']}><TrainingManager /></ProtectedRoute>
        } />
        <Route path="admin/modelo" element={
          <ProtectedRoute roles={['admin']}><ModelEvaluation /></ProtectedRoute>
        } />
      </Route>
    </Routes>
  )
}
