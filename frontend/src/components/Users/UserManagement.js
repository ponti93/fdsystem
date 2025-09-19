/**
 * Simplified User Management Component
 * Shows user list with risk scores and basic management
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Block as BlockIcon,
  CheckCircle as CheckCircleIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import { adminAPI, formatDateTime } from '../../services/api';
import toast from 'react-hot-toast';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selectedUser, setSelectedUser] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    highRiskUsers: 0,
    blockedUsers: 0
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getUsers();
      
      if (response.data.status === 'success') {
        const userData = response.data.data || [];
        console.log('Raw user data from API:', userData); // Debug logging
        
        // Clean and normalize user data
        const cleanedUsers = userData.map(user => ({
          ...user,
          // Handle potential object values by extracting string values
          risk_profile: typeof user.risk_profile === 'object' 
            ? user.risk_profile?.risk_level || 'MEDIUM'
            : user.risk_profile || 'MEDIUM',
          status: typeof user.status === 'object'
            ? user.status?.role || 'active'
            : user.status || 'active',
          // Ensure other fields are strings
          email: typeof user.email === 'string' ? user.email : String(user.email || ''),
          phone_number: typeof user.phone_number === 'string' ? user.phone_number : String(user.phone_number || ''),
          user_id: typeof user.user_id === 'number' || typeof user.user_id === 'string' ? user.user_id : String(user.user_id || '')
        }));
        
        setUsers(cleanedUsers);
        
        // Calculate stats with safe filtering
        const stats = {
          totalUsers: cleanedUsers.length,
          activeUsers: cleanedUsers.filter(u => u.status === 'active').length,
          highRiskUsers: cleanedUsers.filter(u => u.risk_profile?.toUpperCase() === 'HIGH').length,
          blockedUsers: cleanedUsers.filter(u => u.status === 'blocked').length
        };
        setStats(stats);
      }
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleViewUser = (user) => {
    setSelectedUser(user);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedUser(null);
  };

  const getRiskColor = (riskLevel) => {
    if (!riskLevel || typeof riskLevel !== 'string') {
      return 'default';
    }
    
    switch (riskLevel.toUpperCase()) {
      case 'HIGH':
        return 'error';
      case 'MEDIUM':
        return 'warning';
      case 'LOW':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status) => {
    if (!status || typeof status !== 'string') {
      return 'default';
    }
    
    switch (status.toLowerCase()) {
      case 'active':
        return 'success';
      case 'blocked':
        return 'error';
      case 'inactive':
        return 'default';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        User Management
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PersonIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {stats.totalUsers}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Users
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {stats.activeUsers}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Users
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <SecurityIcon sx={{ fontSize: 40, color: 'error.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {stats.highRiskUsers}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    High Risk Users
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <BlockIcon sx={{ fontSize: 40, color: 'warning.main', mr: 2 }} />
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {stats.blockedUsers}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Blocked Users
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Users Table */}
      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User ID</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Phone</TableCell>
                <TableCell>Risk Profile</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Last Login</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((user) => (
                  <TableRow key={user.user_id}>
                    <TableCell>{String(user.user_id || 'N/A')}</TableCell>
                    <TableCell>{String(user.email || 'N/A')}</TableCell>
                    <TableCell>{String(user.phone_number || 'N/A')}</TableCell>
                    <TableCell>
                      <Chip
                        label={user.risk_profile || 'MEDIUM'}
                        color={getRiskColor(user.risk_profile || 'MEDIUM')}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.status || 'active'}
                        color={getStatusColor(user.status || 'active')}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {user.created_at ? formatDateTime(user.created_at) : 'N/A'}
                    </TableCell>
                    <TableCell>
                      {user.last_login ? formatDateTime(user.last_login) : 'Never'}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleViewUser(user)}
                        color="primary"
                      >
                        <ViewIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={users.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(event, newPage) => setPage(newPage)}
          onRowsPerPageChange={(event) => {
            setRowsPerPage(parseInt(event.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>

      {/* User Details Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          User Details - {selectedUser?.email}
        </DialogTitle>
        <DialogContent>
          {selectedUser && (
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="User ID"
                    value={String(selectedUser.user_id || 'N/A')}
                    disabled
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    value={String(selectedUser.email || 'N/A')}
                    disabled
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    value={String(selectedUser.phone_number || 'N/A')}
                    disabled
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Risk Profile"
                    value={String(selectedUser.risk_profile || 'MEDIUM')}
                    disabled
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Status"
                    value={String(selectedUser.status || 'active')}
                    disabled
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Created At"
                    value={formatDateTime(selectedUser.created_at)}
                    disabled
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Last Login"
                    value={selectedUser.last_login ? formatDateTime(selectedUser.last_login) : 'Never logged in'}
                    disabled
                    margin="normal"
                  />
                </Grid>
              </Grid>
              
              <Alert severity="info" sx={{ mt: 2 }}>
                User risk profiles are automatically calculated based on transaction patterns and fraud detection models.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;
