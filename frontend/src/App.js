/**
 * Main App Component
 * Advanced Fraud Detection System Frontend
 */

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { Toaster } from 'react-hot-toast';

// Layout Components
import Header from './components/Layout/Header';
import Sidebar, { DRAWER_WIDTH } from './components/Layout/Sidebar';
import AuthProvider from './components/Auth/AuthProvider';
import ProtectedRoute from './components/Auth/ProtectedRoute';

// Page Components
import DashboardOverview from './components/Dashboard/DashboardOverview';
import TransactionMonitor from './components/Transactions/TransactionMonitor';
import RiskAnalytics from './components/Analytics/RiskAnalytics';
import MLModels from './components/ML/MLModels';
import PaymentInterface from './components/Payments/PaymentInterface';
import UserManagement from './components/Users/UserManagement';
import SystemConfiguration from './components/Settings/SystemConfiguration';

// Services
import { authAPI } from './services/api';

// Create Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});


function App() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Box sx={{ display: 'flex' }}>
            {/* Sidebar */}
            <Sidebar 
              open={mobileOpen} 
              onClose={handleDrawerToggle}
            />
            
            {/* Main Content */}
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                width: { xs: '100%', md: `calc(100% - ${DRAWER_WIDTH}px)` },
                ml: { xs: 0, md: `${DRAWER_WIDTH}px` },
                minHeight: '100vh',
                backgroundColor: 'background.default',
              }}
            >
              {/* Header */}
              <Header 
                onMenuClick={handleDrawerToggle}
              />
              
              {/* Page Content */}
              <Box sx={{ mt: 8, p: { xs: 1, sm: 2, md: 3 } }}>
                <Routes>
                  <Route path="/" element={<DashboardOverview />} />
                  <Route path="/transactions" element={<TransactionMonitor />} />
                  <Route path="/payment-test" element={<PaymentInterface />} />
                  <Route path="/analytics" element={
                    <ProtectedRoute requiredPermission="read">
                      <RiskAnalytics />
                    </ProtectedRoute>
                  } />
                  <Route path="/users" element={
                    <ProtectedRoute adminOnly={true}>
                      <UserManagement />
                    </ProtectedRoute>
                  } />
                  <Route path="/ml-models" element={
                    <ProtectedRoute adminOnly={true}>
                      <MLModels />
                    </ProtectedRoute>
                  } />
                  <Route path="/settings" element={
                    <ProtectedRoute adminOnly={true}>
                      <SystemConfiguration />
                    </ProtectedRoute>
                  } />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Box>
            </Box>
          </Box>
        </Router>
        
        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#4caf50',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#f44336',
                secondary: '#fff',
              },
            },
          }}
        />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
