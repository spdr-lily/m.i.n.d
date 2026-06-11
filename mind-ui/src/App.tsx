import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import ptBR from 'antd/locale/pt_BR'
import MainLayout from './components/MainLayout'
import ProtectedRoute from './components/ProtectedRoute'
import ErrorBoundary from './components/ErrorBoundary'
import LoginPage from './pages/auth/LoginPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import PatientListPage from './pages/patients/PatientListPage'
import PatientCreatePage from './pages/patients/PatientCreatePage'
import PatientDetailPage from './pages/patients/PatientDetailPage'
import PatientEditPage from './pages/patients/PatientEditPage'
import PatientTimelinePage from './pages/patients/PatientTimelinePage'
import PatientReportsPage from './pages/patients/PatientReportsPage'
import ConsultationListPage from './pages/consultations/ConsultationListPage'
import ConsultationCreatePage from './pages/consultations/ConsultationCreatePage'
import ConsultationDetailPage from './pages/consultations/ConsultationDetailPage'
import AssessmentPage from './pages/assessments/AssessmentPage'
import InferencePage from './pages/inferences/InferencePage'
import AlertsPage from './pages/alerts/AlertsPage'
import UsersPage from './pages/admin/UsersPage'
import PermissionsPage from './pages/admin/PermissionsPage'
import MonitoringPage from './pages/admin/MonitoringPage'
import AuditLogPage from './pages/audit/AuditLogPage'
import ScalesPage from './pages/admin/ScalesPage'
import DisordersPage from './pages/admin/DisordersPage'
import SymptomsPage from './pages/admin/SymptomsPage'
import MedicationsPage from './pages/admin/MedicationsPage'
import ProfessionalsPage from './pages/professionals/ProfessionalsPage'

export default function App() {
  return (
    <ConfigProvider
      locale={ptBR}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 6,
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        },
      }}
    >
      <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<DashboardPage />} />
            <Route path="/patients" element={<PatientListPage />} />
            <Route path="/patients/new" element={<PatientCreatePage />} />
            <Route path="/patients/:uuid/timeline" element={<PatientTimelinePage />} />
            <Route path="/patients/:uuid/reports" element={<PatientReportsPage />} />
            <Route path="/patients/:uuid/edit" element={<PatientEditPage />} />
            <Route path="/patients/:uuid" element={<PatientDetailPage />} />
            <Route path="/consultations" element={<ConsultationListPage />} />
            <Route path="/consultations/new" element={<ConsultationCreatePage />} />
            <Route path="/consultations/:uuid" element={<ConsultationDetailPage />} />
            <Route path="/assessments" element={<AssessmentPage />} />
            <Route path="/inferences" element={<InferencePage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/admin/users" element={<UsersPage />} />
            <Route path="/admin/permissions" element={<PermissionsPage />} />
            <Route path="/admin/monitoring" element={<MonitoringPage />} />
            <Route path="/admin/scales" element={<ScalesPage />} />
            <Route path="/admin/symptoms" element={<SymptomsPage />} />
            <Route path="/admin/medications" element={<MedicationsPage />} />
            <Route path="/admin/disorders" element={<DisordersPage />} />
            <Route path="/professionals" element={<ProfessionalsPage />} />
            <Route path="/audit" element={<AuditLogPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      </ErrorBoundary>
    </ConfigProvider>
  )
}
