/**
 * Authentication Provider Component
 * Handles user authentication and role management
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import { authAPI } from '../../services/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [authDialogOpen, setAuthDialogOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState('admin');
  const [customToken, setCustomToken] = useState('');

  useEffect(() => {
    // Check if user is already authenticated
    const token = authAPI.getToken();
    if (token) {
      // Determine role from token
      if (token.startsWith('admin_')) {
        setUser({ role: 'admin', token, permissions: ['read', 'write', 'admin'] });
      } else if (token.startsWith('analyst_')) {
        setUser({ role: 'analyst', token, permissions: ['read'] });
      } else {
        setUser({ role: 'viewer', token, permissions: ['read'] });
      }
    }
  }, []);

  const login = (role, token = null) => {
    let authToken;
    
    if (token) {
      authToken = token;
    } else {
      // Use predefined tokens
      switch (role) {
        case 'admin':
          authToken = 'admin_token123';
          break;
        case 'analyst':
          authToken = 'analyst_token123';
          break;
        case 'viewer':
          authToken = 'viewer_token123';
          break;
        default:
          authToken = 'admin_token123';
      }
    }

    authAPI.setToken(authToken);
    
    const permissions = role === 'admin' ? ['read', 'write', 'admin'] :
                      role === 'analyst' ? ['read'] :
                      ['read'];

    setUser({ role, token: authToken, permissions });
    setAuthDialogOpen(false);
    toast.success(`Logged in as ${role}`);
  };

  const logout = () => {
    authAPI.clearToken();
    setUser(null);
    toast.success('Logged out successfully');
  };

  const openAuthDialog = () => {
    setAuthDialogOpen(true);
  };

  const handleQuickLogin = () => {
    login(selectedRole);
  };

  const handleCustomLogin = () => {
    if (!customToken.trim()) {
      toast.error('Please enter a token');
      return;
    }
    
    // Determine role from custom token
    let role = 'viewer';
    if (customToken.includes('admin')) role = 'admin';
    else if (customToken.includes('analyst')) role = 'analyst';
    
    login(role, customToken.trim());
    setCustomToken('');
  };

  const hasPermission = (permission) => {
    return user?.permissions?.includes(permission) || false;
  };

  const isAdmin = () => hasPermission('admin');
  const canRead = () => hasPermission('read');
  const canWrite = () => hasPermission('write');

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      openAuthDialog,
      hasPermission,
      isAdmin,
      canRead,
      canWrite,
      isAuthenticated: !!user,
    }}>
      {children}
      
      {/* Authentication Dialog */}
      <Dialog open={authDialogOpen} onClose={() => setAuthDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">System Authentication</Typography>
            {user && (
              <Chip 
                label={`Current: ${user.role}`} 
                color="primary" 
                size="small"
              />
            )}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 3 }}>
            Select your access level or enter a custom authentication token.
          </Alert>
          
          {/* Quick Role Selection */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>Quick Access</Typography>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Role</InputLabel>
              <Select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                label="Select Role"
              >
                <MenuItem value="admin">
                  <Box>
                    <Typography variant="body1">Administrator</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Full system access, can train models, manage rules
                    </Typography>
                  </Box>
                </MenuItem>
                <MenuItem value="analyst">
                  <Box>
                    <Typography variant="body1">Analyst</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Read access to analytics and transaction data
                    </Typography>
                  </Box>
                </MenuItem>
                <MenuItem value="viewer">
                  <Box>
                    <Typography variant="body1">Viewer</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Basic transaction viewing permissions
                    </Typography>
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>
            <Button 
              variant="contained" 
              fullWidth 
              onClick={handleQuickLogin}
              sx={{ mb: 2 }}
            >
              Login as {selectedRole}
            </Button>
          </Box>

          {/* Custom Token */}
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>Custom Token</Typography>
            <TextField
              fullWidth
              label="Authentication Token"
              value={customToken}
              onChange={(e) => setCustomToken(e.target.value)}
              placeholder="Enter your authentication token"
              sx={{ mb: 2 }}
            />
            <Button 
              variant="outlined" 
              fullWidth 
              onClick={handleCustomLogin}
              disabled={!customToken.trim()}
            >
              Login with Custom Token
            </Button>
          </Box>

          {/* Token Reference */}
          <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.100', borderRadius: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Default Tokens:
            </Typography>
            <Typography variant="caption" display="block">
              Admin: admin_token123
            </Typography>
            <Typography variant="caption" display="block">
              Analyst: analyst_token123
            </Typography>
            <Typography variant="caption" display="block">
              Viewer: viewer_token123
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAuthDialogOpen(false)}>Cancel</Button>
          {user && (
            <Button onClick={logout} color="error">
              Logout
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </AuthContext.Provider>
  );
};

export default AuthProvider;
