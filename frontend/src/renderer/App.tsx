import type React from 'react';
import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import { ScreenReaderAnnouncer } from './accessibility/ScreenReaderAnnouncer';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { clearSession, getSessionId, validateSession } from './services/authApi';
import { useAppStore } from './store/appStore';

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">{title}</h1>
      <p className="text-[var(--color-text-secondary)]">
        This section is under construction. Check back soon.
      </p>
    </div>
  );
}

type AuthStatus = 'checking' | 'authenticated' | 'anonymous';

/**
 * Gate the authenticated area.
 *
 * Sessions are held server-side and invalidated whenever the backend restarts,
 * so a persisted token is verified once on mount rather than trusted. A stale
 * token is cleared instead of leaving the user in a shell that 401s on every
 * request.
 */
function RequireAuth({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const setUser = useAppStore((state) => state.setUser);
  const [status, setStatus] = useState<AuthStatus>(() =>
    getSessionId() ? 'checking' : 'anonymous',
  );

  useEffect(() => {
    const sessionId = getSessionId();
    if (!sessionId) {
      setStatus('anonymous');
      return;
    }

    let cancelled = false;
    validateSession(sessionId).then((valid) => {
      if (cancelled) return;
      if (!valid) {
        clearSession();
        setUser(null);
      }
      setStatus(valid ? 'authenticated' : 'anonymous');
    });

    return () => {
      cancelled = true;
    };
  }, [setUser]);

  if (status === 'checking') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-primary)]">
        <p className="text-sm text-[var(--color-text-secondary)]">Checking your session...</p>
      </div>
    );
  }

  if (status === 'anonymous') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}

/** The signed-in shell: exactly one <AppLayout> around the protected routes. */
function ProtectedLayout() {
  return (
    <RequireAuth>
      <AppLayout>
        <Outlet />
      </AppLayout>
    </RequireAuth>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ScreenReaderAnnouncer>
        <AppProvider>
          <Routes>
            {/* Unauthenticated screens render without the app chrome. */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route element={<ProtectedLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/authentication" element={<PlaceholderPage title="Authentication" />} />
              <Route path="/authentication/*" element={<PlaceholderPage title="Authentication" />} />
              <Route path="/users" element={<PlaceholderPage title="Users" />} />
              <Route path="/sessions" element={<PlaceholderPage title="Sessions" />} />
              <Route path="/attacks" element={<PlaceholderPage title="Attacks" />} />
              <Route path="/defenses" element={<PlaceholderPage title="Defenses" />} />
              <Route path="/analytics" element={<PlaceholderPage title="Analytics" />} />
              <Route path="/audit" element={<PlaceholderPage title="Audit Logs" />} />
              <Route path="/timeline" element={<PlaceholderPage title="Security Timeline" />} />
              <Route path="/reports" element={<PlaceholderPage title="Reports" />} />
              <Route path="/learning" element={<PlaceholderPage title="Learning Center" />} />
              <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
              <Route path="/help" element={<PlaceholderPage title="Help" />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
        </AppProvider>
      </ScreenReaderAnnouncer>
    </BrowserRouter>
  );
}
