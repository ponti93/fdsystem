/**
 * Protected Route Component
 * Handles access control for admin-only pages
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  Lock as LockIcon,
  Security as SecurityIcon,
  VpnKey as VpnKeyIcon,
} from '@mui/icons-material';
import { useAuth } from './AuthProvider';

const AccessDenied = ({ requiredPermission = 'admin' }) => {
  const { openAuthDialog, user } = useAuth();

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
      <Card sx={{ maxWidth: 500, textAlign: 'center' }}>
        <CardContent sx={{ p: 4 }}>
          <SecurityIcon sx={{ fontSize: 80, color: 'warning.main', mb: 2 }} />
          
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 2 }}>
            Access Restricted
          </Typography>
          
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            This page requires <strong>{requiredPermission}</strong> access level.
          </Typography>

          {user ? (
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="body2">
                You are currently logged in as <strong>{user.role}</strong> with permissions:
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: 1 }}>
                {user.permissions?.map((permission) => (
                  <Chip key={permission} label={permission} size="small" />
                ))}
              </Box>
            </Alert>
          ) : (
            <Alert severity="info" sx={{ mb: 3 }}>
              You are not currently authenticated. Please login to access this page.
            </Alert>
          )}

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              startIcon={<VpnKeyIcon />}
              onClick={openAuthDialog}
              size="large"
            >
              {user ? 'Switch Role' : 'Login'}
            </Button>
          </Box>

          <Box sx={{ mt: 4, p: 2, backgroundColor: 'grey.50', borderRadius: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <LockIcon sx={{ mr: 1 }} />
              Quick Access Tokens
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Admin Access:</strong> admin_token123
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Analyst Access:</strong> analyst_token123
            </Typography>
            <Typography variant="body2">
              <strong>Viewer Access:</strong> viewer_token123
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

const ProtectedRoute = ({ children, requiredPermission = 'read', adminOnly = false }) => {
  const { user, hasPermission, isAdmin } = useAuth();

  // Check if user has required permission
  if (adminOnly && !isAdmin()) {
    return <AccessDenied requiredPermission="admin" />;
  }

  if (!hasPermission(requiredPermission)) {
    return <AccessDenied requiredPermission={requiredPermission} />;
  }

  return children;
};

export default ProtectedRoute;
