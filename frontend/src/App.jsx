import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { hasRole, useAuth } from './auth/AuthContext.jsx'
import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Users from './pages/Users.jsx'
import Subjects from './pages/Subjects.jsx'
import Periods from './pages/Periods.jsx'
import Enrollments from './pages/Enrollments.jsx'
import Grades from './pages/Grades.jsx'
import Reports from './pages/Reports.jsx'

function Protected({ children, roles }) {
  const { user } = useAuth()
  const location = useLocation()
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  if (roles && !roles.some((role) => hasRole(user, role))) return <Navigate to="/" replace />
  return <Layout>{children}</Layout>
}

export default function App() {
  return <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/" element={<Protected><Dashboard /></Protected>} />
    <Route path="/users" element={<Protected roles={['ADMINISTRADOR']}><Users /></Protected>} />
    <Route path="/subjects" element={<Protected><Subjects /></Protected>} />
    <Route path="/periods" element={<Protected><Periods /></Protected>} />
    <Route path="/enrollments" element={<Protected><Enrollments /></Protected>} />
    <Route path="/grades" element={<Protected><Grades /></Protected>} />
    <Route path="/reports" element={<Protected roles={['ADMINISTRADOR', 'DOCENTE']}><Reports /></Protected>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
}
