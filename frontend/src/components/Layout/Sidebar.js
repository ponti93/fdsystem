/**
 * Sidebar Navigation Component
 * Main navigation for the fraud detection system
 */

import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Box,
  Chip,
  useTheme,
  Button,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Security as SecurityIcon,
  Analytics as AnalyticsIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
  Payment as PaymentIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../Auth/AuthProvider';

const DRAWER_WIDTH = 280;

const menuItems = [
  {
    id: 'overview',
    title: 'Dashboard Overview',
    icon: DashboardIcon,
    path: '/',
    description: 'System overview and key metrics'
  },
  {
    id: 'transactions',
    title: 'Transaction Monitor',
    icon: PaymentIcon,
    path: '/transactions',
    description: 'Real-time transaction monitoring'
  },
  {
    id: 'payment-test',
    title: 'Flutterwave Payment Test',
    icon: SecurityIcon,
    path: '/payment-test',
    description: 'Test real payments with fraud detection'
  },
  {
    id: 'analytics',
    title: 'Risk Analytics',
    icon: AnalyticsIcon,
    path: '/analytics',
    description: 'Advanced fraud analytics and trends'
  },
  {
    id: 'divider1',
    type: 'divider'
  },
  {
    id: 'users',
    title: 'User Management',
    icon: PeopleIcon,
    path: '/users',
    description: 'User profiles and risk scoring',
    adminOnly: true
  },
  {
    id: 'ml-models',
    title: 'ML Models',
    icon: PsychologyIcon,
    path: '/ml-models',
    description: 'Machine learning model management',
    adminOnly: true
  },
  {
    id: 'divider2',
    type: 'divider'
  },
  {
    id: 'system-config',
    title: 'System Configuration',
    icon: SettingsIcon,
    path: '/settings',
    description: 'System settings and configuration',
    adminOnly: true
  }
];

const Sidebar = ({ open, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { user, isAdmin, openAuthDialog } = useAuth();

  const handleNavigation = (path) => {
    navigate(path);
    if (onClose) onClose();
  };

  const filteredMenuItems = menuItems.filter(item => {
    if (item.adminOnly && !isAdmin()) return false;
    return true;
  });

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box
        sx={{
          p: 3,
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <SecurityIcon sx={{ mr: 1, fontSize: 28 }} />
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            Fraud Detection
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          Advanced Security System
        </Typography>
        <Chip
          label={user ? `${user.role.charAt(0).toUpperCase() + user.role.slice(1)} Access` : 'Guest'}
          size="small"
          sx={{
            mt: 1,
            backgroundColor: 'rgba(255,255,255,0.2)',
            color: 'white',
            fontWeight: 'bold'
          }}
        />
        {!user && (
          <Button
            variant="outlined"
            size="small"
            onClick={openAuthDialog}
            sx={{
              mt: 1,
              color: 'white',
              borderColor: 'rgba(255,255,255,0.5)',
              '&:hover': {
                borderColor: 'white',
                backgroundColor: 'rgba(255,255,255,0.1)'
              }
            }}
          >
            Login
          </Button>
        )}
      </Box>

      {/* Navigation Menu */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ pt: 2 }}>
          {filteredMenuItems.map((item) => {
            if (item.type === 'divider') {
              return <Divider key={item.id} sx={{ my: 1 }} />;
            }

            const isActive = location.pathname === item.path;
            const IconComponent = item.icon;

            return (
              <ListItem key={item.id} disablePadding sx={{ px: 2, mb: 0.5 }}>
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: 2,
                    py: 1.5,
                    px: 2,
                    backgroundColor: isActive ? theme.palette.primary.main : 'transparent',
                    color: isActive ? 'white' : theme.palette.text.primary,
                    '&:hover': {
                      backgroundColor: isActive 
                        ? theme.palette.primary.main 
                        : theme.palette.action.hover,
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: isActive ? 'white' : theme.palette.primary.main,
                      minWidth: 40,
                    }}
                  >
                    <IconComponent />
                  </ListItemIcon>
                  <Box sx={{ flex: 1 }}>
                    <ListItemText
                      primary={item.title}
                      secondary={item.description}
                      primaryTypographyProps={{
                        fontWeight: isActive ? 'bold' : 'medium',
                        fontSize: '0.9rem',
                      }}
                      secondaryTypographyProps={{
                        fontSize: '0.75rem',
                        color: isActive ? 'rgba(255,255,255,0.7)' : theme.palette.text.secondary,
                      }}
                    />
                  </Box>
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          Fraud Detection System v2.0
        </Typography>
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          Real-time AI-powered security
        </Typography>
      </Box>
    </Box>
  );

  return (
    <>
      {/* Desktop Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
            border: 'none',
            boxShadow: theme.shadows[3],
          },
        }}
        open
      >
        {drawer}
      </Drawer>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={open}
        onClose={onClose}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: DRAWER_WIDTH,
          },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export { DRAWER_WIDTH };
export default Sidebar;
