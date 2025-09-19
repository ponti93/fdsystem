/**
 * Transaction Monitor Component
 * Real-time transaction monitoring and testing interface
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Tooltip,
  Badge,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';
import { DataGrid } from '@mui/x-data-grid';
import { transactionAPI, formatCurrency, formatDateTime, getFraudScoreColor, getDecisionColor } from '../../services/api';
import toast from 'react-hot-toast';

const TransactionTester = ({ onTransactionCreated }) => {
  const [formData, setFormData] = useState({
    amount: 100000,
    user_id: 1,
    merchant_id: 'TEST_MERCHANT',
    currency: 'NGN',
    payment_method: 'card',
    ip_address: '192.168.1.100',
  });
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await transactionAPI.createTransaction(formData);
      toast.success('Transaction processed successfully!');
      onTransactionCreated(response.data.data);
      
      // Reset form with new random values
      setFormData(prev => ({
        ...prev,
        amount: Math.floor(Math.random() * 1000000) + 10000,
        ip_address: `192.168.1.${Math.floor(Math.random() * 255) + 1}`,
      }));
    } catch (error) {
      toast.error('Failed to process transaction');
    } finally {
      setLoading(false);
    }
  };

  const runTestScenarios = async () => {
    setLoading(true);
    try {
      const response = await transactionAPI.runTestScenarios();
      toast.success(`Generated ${response.data.data.results.length} test transactions`);
      onTransactionCreated();
    } catch (error) {
      toast.error('Failed to run test scenarios');
    } finally {
      setLoading(false);
    }
  };

  const quickTests = [
    { label: 'Normal (₦50k)', amount: 50000, merchant_id: 'Coffee Shop' },
    { label: 'High Amount (₦600k)', amount: 600000, merchant_id: 'Electronics Store' },
    { label: 'Round Amount (₦1M)', amount: 1000000, merchant_id: 'Car Dealer' },
    { label: 'Risky Merchant', amount: 100000, merchant_id: 'Casino Resort' },
  ];

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
        Transaction Testing
      </Typography>
      
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Amount"
              type="number"
              value={formData.amount}
              onChange={(e) => handleInputChange('amount', Number(e.target.value))}
              InputProps={{
                startAdornment: '₦',
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="User ID"
              type="number"
              value={formData.user_id}
              onChange={(e) => handleInputChange('user_id', Number(e.target.value))}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Merchant"
              value={formData.merchant_id}
              onChange={(e) => handleInputChange('merchant_id', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Payment Method</InputLabel>
              <Select
                value={formData.payment_method}
                onChange={(e) => handleInputChange('payment_method', e.target.value)}
                label="Payment Method"
              >
                <MenuItem value="card">Card</MenuItem>
                <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
                <MenuItem value="mobile_money">Mobile Money</MenuItem>
                <MenuItem value="crypto">Cryptocurrency</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <Button
            type="submit"
            variant="contained"
            startIcon={<PlayArrowIcon />}
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Test Transaction'}
          </Button>
          
          <Button
            variant="outlined"
            onClick={runTestScenarios}
            disabled={loading}
          >
            Run Test Scenarios
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Typography variant="body2" sx={{ mr: 2, alignSelf: 'center' }}>
            Quick Tests:
          </Typography>
          {quickTests.map((test, index) => (
            <Button
              key={index}
              size="small"
              variant="outlined"
              onClick={() => {
                setFormData(prev => ({
                  ...prev,
                  amount: test.amount,
                  merchant_id: test.merchant_id,
                }));
              }}
            >
              {test.label}
            </Button>
          ))}
        </Box>
      </form>
    </Paper>
  );
};

const TransactionDetailsDialog = ({ open, onClose, transaction }) => {
  if (!transaction) return null;

  const fraudAssessment = transaction.fraud_assessment;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Transaction Details - {transaction.transaction_id}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          {/* Basic Info */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" sx={{ mb: 2 }}>Basic Information</Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">Amount</Typography>
              <Typography variant="h6">{formatCurrency(transaction.amount, transaction.currency)}</Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">Merchant</Typography>
              <Typography>{transaction.merchant_id}</Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">Payment Method</Typography>
              <Typography>{transaction.payment_method}</Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">Timestamp</Typography>
              <Typography>{formatDateTime(transaction.timestamp)}</Typography>
            </Box>
          </Grid>

          {/* Fraud Analysis */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" sx={{ mb: 2 }}>Fraud Analysis</Typography>
            {fraudAssessment ? (
              <>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Decision</Typography>
                  <Chip
                    label={fraudAssessment.decision}
                    sx={{
                      backgroundColor: getDecisionColor(fraudAssessment.decision),
                      color: 'white',
                      fontWeight: 'bold',
                    }}
                  />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Fraud Score</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="h6" sx={{ mr: 1 }}>
                      {(fraudAssessment.fraud_score * 100).toFixed(1)}%
                    </Typography>
                    <Chip
                      size="small"
                      label={fraudAssessment.fraud_score >= 0.8 ? 'High Risk' : 
                            fraudAssessment.fraud_score >= 0.5 ? 'Medium Risk' : 'Low Risk'}
                      sx={{
                        backgroundColor: getFraudScoreColor(fraudAssessment.fraud_score),
                        color: 'white',
                      }}
                    />
                  </Box>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Model Version</Typography>
                  <Typography>{fraudAssessment.model_version}</Typography>
                </Box>
                {fraudAssessment.confidence_level && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">Confidence Level</Typography>
                    <Typography>{(fraudAssessment.confidence_level * 100).toFixed(1)}%</Typography>
                  </Box>
                )}
              </>
            ) : (
              <Alert severity="info">No fraud analysis available</Alert>
            )}
          </Grid>

          {/* Risk Factors */}
          {fraudAssessment?.risk_factors && fraudAssessment.risk_factors.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2 }}>Risk Factors</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {fraudAssessment.risk_factors.map((factor, index) => (
                  <Chip
                    key={index}
                    label={`${factor.factor} (${(factor.weight * 100).toFixed(0)}%)`}
                    variant={factor.triggered ? 'filled' : 'outlined'}
                    color={factor.triggered ? 'error' : 'default'}
                    size="small"
                  />
                ))}
              </Box>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

const TransactionMonitor = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  useEffect(() => {
    loadTransactions();
    const interval = setInterval(loadTransactions, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadTransactions = async () => {
    try {
      const response = await transactionAPI.getTransactions(100);
      setTransactions(response.data.data);
    } catch (error) {
      console.error('Error loading transactions:', error);
      toast.error('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const handleTransactionCreated = (newTransaction) => {
    if (newTransaction) {
      setTransactions(prev => [newTransaction, ...prev]);
    } else {
      loadTransactions(); // Reload all if multiple transactions created
    }
  };

  const handleViewDetails = (transaction) => {
    setSelectedTransaction(transaction);
    setDetailsOpen(true);
  };

  const columns = [
    {
      field: 'transaction_id',
      headerName: 'Transaction ID',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {params.value}
        </Typography>
      ),
    },
    {
      field: 'amount',
      headerName: 'Amount',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
          {formatCurrency(params.value, params.row.currency)}
        </Typography>
      ),
    },
    {
      field: 'merchant_id',
      headerName: 'Merchant',
      width: 150,
    },
    {
      field: 'timestamp',
      headerName: 'Time',
      width: 160,
      renderCell: (params) => formatDateTime(params.value),
    },
    {
      field: 'fraud_score',
      headerName: 'Fraud Score',
      width: 120,
      renderCell: (params) => {
        const score = params.row.fraud_assessment?.fraud_score;
        if (!score) return '-';
        
        return (
          <Chip
            label={`${(score * 100).toFixed(0)}%`}
            size="small"
            sx={{
              backgroundColor: getFraudScoreColor(score),
              color: 'white',
              fontWeight: 'bold',
            }}
          />
        );
      },
    },
    {
      field: 'decision',
      headerName: 'Decision',
      width: 120,
      renderCell: (params) => {
        const decision = params.row.fraud_assessment?.decision || params.row.status;
        const color = getDecisionColor(decision);
        
        return (
          <Chip
            label={decision}
            size="small"
            sx={{
              backgroundColor: color,
              color: 'white',
              fontWeight: 'bold',
            }}
          />
        );
      },
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 100,
      sortable: false,
      renderCell: (params) => (
        <IconButton
          size="small"
          onClick={() => handleViewDetails(params.row)}
          title="View Details"
        >
          <VisibilityIcon />
        </IconButton>
      ),
    },
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
            Transaction Monitor
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time transaction processing and fraud detection
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadTransactions}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Transaction Tester */}
      <TransactionTester onTransactionCreated={handleTransactionCreated} />

      {/* Transactions Table */}
      <Paper sx={{ height: 600 }}>
        <DataGrid
          rows={transactions}
          columns={columns}
          getRowId={(row) => row.transaction_id}
          pageSize={rowsPerPage}
          rowsPerPageOptions={[25, 50, 100]}
          loading={loading}
          disableSelectionOnClick
          sx={{
            '& .MuiDataGrid-cell': {
              borderBottom: 1,
              borderColor: 'divider',
            },
            '& .MuiDataGrid-row:hover': {
              backgroundColor: 'action.hover',
            },
          }}
        />
      </Paper>

      {/* Transaction Details Dialog */}
      <TransactionDetailsDialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        transaction={selectedTransaction}
      />
    </Box>
  );
};

export default TransactionMonitor;
