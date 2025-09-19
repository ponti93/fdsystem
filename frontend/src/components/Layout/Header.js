/**
 * Header Component
 * Top navigation bar with user controls and system status
 */

import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  Box,
  Chip,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  Alert,
  Collapse,
  Button,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { systemAPI, authAPI } from '../../services/api';
import { DRAWER_WIDTH } from './Sidebar';
import { useAuth } from '../Auth/AuthProvider';

const Header = ({ onMenuClick }) => {
  const { user, openAuthDialog, logout, isAuthenticated } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [systemStatus, setSystemStatus] = useState({
    status: 'checking',
    database: 'unknown',
    ml_model: 'unknown',
  });
  const [showStatusAlert, setShowStatusAlert] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await systemAPI.getHealth();
      setSystemStatus(response.data);
      setLastRefresh(new Date());
      
      // Show alert if there are issues
      if (response.data.status !== 'healthy' || response.data.ml_model === 'not_loaded') {
        setShowStatusAlert(true);
      }
    } catch (error) {
      setSystemStatus({
        status: 'error',
        database: 'disconnected',
        ml_model: 'unknown',
        error: error.message,
      });
      setShowStatusAlert(true);
    }
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    authAPI.clearToken();
    handleMenuClose();
    window.location.reload();
  };

  const getStatusIcon = () => {
    switch (systemStatus.status) {
      case 'healthy':
        return <CheckCircleIcon sx={{ color: '#4caf50' }} />;
      case 'error':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      default:
        return <WarningIcon sx={{ color: '#ff9800' }} />;
    }
  };

  const getStatusColor = () => {
    switch (systemStatus.status) {
      case 'healthy':
        return 'success';
      case 'error':
        return 'error';
      default:
        return 'warning';
    }
  };

  const isMenuOpen = Boolean(anchorEl);

  return (
    <>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { md: `${DRAWER_WIDTH}px` },
          backgroundColor: 'white',
          color: 'text.primary',
          boxShadow: 1,
        }}
      >
        <Toolbar>
          {/* Mobile menu button */}
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onMenuClick}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          {/* System Status */}
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
            {getStatusIcon()}
            <Chip
              label={`System ${systemStatus.status}`}
              color={getStatusColor()}
              size="small"
              sx={{ ml: 1, textTransform: 'capitalize' }}
            />
          </Box>

          {/* ML Model Status */}
          <Chip
            icon={<SecurityIcon />}
            label={`ML Model: ${systemStatus.ml_model === 'loaded' ? 'Active' : 'Inactive'}`}
            color={systemStatus.ml_model === 'loaded' ? 'success' : 'warning'}
            variant="outlined"
            size="small"
            sx={{ mr: 2 }}
          />

          {/* Spacer */}
          <Box sx={{ flexGrow: 1 }} />

          {/* Last Refresh */}
          <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
            Updated: {lastRefresh.toLocaleTimeString()}
          </Typography>

          {/* Refresh Button */}
          <IconButton
            color="inherit"
            onClick={checkSystemHealth}
            title="Refresh system status"
          >
            <RefreshIcon />
          </IconButton>

          {/* Notifications */}
          <IconButton
            size="large"
            aria-label="show notifications"
            color="inherit"
          >
            <Badge badgeContent={systemStatus.status !== 'healthy' ? 1 : 0} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          {/* Authentication */}
          {isAuthenticated ? (
            <>
              <Chip
                label={`${user.role} access`}
                color="primary"
                size="small"
                sx={{ mr: 2, textTransform: 'capitalize' }}
              />
              <IconButton
                size="large"
                edge="end"
                aria-label="account of current user"
                aria-controls="primary-search-account-menu"
                aria-haspopup="true"
                onClick={handleProfileMenuOpen}
                color="inherit"
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                  {user.role.charAt(0).toUpperCase()}
                </Avatar>
              </IconButton>
            </>
          ) : (
            <Button
              variant="contained"
              onClick={openAuthDialog}
              size="small"
            >
              Login
            </Button>
          )}
        </Toolbar>

        {/* System Status Alert */}
        <Collapse in={showStatusAlert}>
          <Alert
            severity={systemStatus.status === 'error' ? 'error' : 'warning'}
            onClose={() => setShowStatusAlert(false)}
            sx={{ borderRadius: 0 }}
          >
            {systemStatus.status === 'error' && (
              <strong>System Error: </strong>
            )}
            {systemStatus.database === 'disconnected' && 'Database connection failed. '}
            {systemStatus.ml_model === 'not_loaded' && 'ML model not loaded - using rule-based detection only. '}
            {systemStatus.error && `Error: ${systemStatus.error}`}
          </Alert>
        </Collapse>
      </AppBar>

      {/* User Menu */}
      <Menu
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        id="primary-search-account-menu"
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={isMenuOpen}
        onClose={handleMenuClose}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle2" color="text.secondary">
            Signed in as
          </Typography>
          <Typography variant="body1" sx={{ fontWeight: 'bold', textTransform: 'capitalize' }}>
            {user?.role || 'Guest'} User
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
            {user?.permissions?.map((permission) => (
              <Chip 
                key={permission} 
                label={permission} 
                size="small" 
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
        <Divider />
        <MenuItem onClick={openAuthDialog}>
          Switch Role
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => { logout(); handleMenuClose(); }} sx={{ color: 'error.main' }}>
          Logout
        </MenuItem>
      </Menu>
    </>
  );
};

export default Header;
