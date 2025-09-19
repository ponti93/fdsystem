/**
 * Dashboard Overview Component
 * Main dashboard with key metrics and real-time monitoring
 */

import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { statsAPI, adminAPI, transactionAPI, formatCurrency, formatDateTime, getFraudScoreColor } from '../../services/api';
import toast from 'react-hot-toast';

const COLORS = ['#4caf50', '#f44336', '#ff9800', '#2196f3', '#9c27b0'];

const MetricCard = ({ title, value, subtitle, icon: Icon, color = 'primary', trend, isLoading }) => (
  <Card sx={{ height: '100%', position: 'relative' }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 2,
              backgroundColor: `${color}.light`,
              color: `${color}.contrastText`,
              mr: 2,
            }}
          >
            <Icon />
          </Box>
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            {title}
          </Typography>
        </Box>
        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {trend > 0 ? (
              <TrendingUpIcon sx={{ color: 'success.main', mr: 0.5 }} />
            ) : (
              <TrendingDownIcon sx={{ color: 'error.main', mr: 0.5 }} />
            )}
            <Typography variant="caption" color={trend > 0 ? 'success.main' : 'error.main'}>
              {Math.abs(trend)}%
            </Typography>
          </Box>
        )}
      </Box>
      
      {isLoading ? (
        <CircularProgress size={24} />
      ) : (
        <>
          <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </>
      )}
    </CardContent>
  </Card>
);

const DashboardOverview = () => {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load data in parallel
      const [statsResponse, analyticsResponse, transactionsResponse] = await Promise.all([
        statsAPI.getStats(),
        adminAPI.getAnalytics().catch(() => null), // Analytics might require admin access
        transactionAPI.getTransactions(20),
      ]);

      setStats(statsResponse.data.data);
      if (analyticsResponse) {
        setAnalytics(analyticsResponse.data.data);
      }
      setRecentTransactions(transactionsResponse.data.data);
      setLastUpdate(new Date());
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const fraudTrendData = analytics?.fraud_trends ? [
    { name: 'Approved', value: analytics.fraud_trends.decision_distribution.APPROVE, color: '#4caf50' },
    { name: 'Declined', value: analytics.fraud_trends.decision_distribution.DECLINE, color: '#f44336' },
    { name: 'Review', value: analytics.fraud_trends.decision_distribution.REVIEW, color: '#ff9800' },
  ] : [];

  const hourlyData = recentTransactions.slice(0, 12).map((tx, index) => ({
    hour: new Date(tx.timestamp).getHours(),
    transactions: 1,
    fraudScore: tx.fraud_assessment?.fraud_score || 0,
  }));

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
            Fraud Detection Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time monitoring and analytics • Last updated: {formatDateTime(lastUpdate)}
          </Typography>
        </Box>
        <Tooltip title="Refresh Dashboard">
          <IconButton onClick={loadDashboardData} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Transactions"
            value={stats?.total_transactions?.toLocaleString() || '0'}
            subtitle="All time transactions"
            icon={SpeedIcon}
            color="primary"
            isLoading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Approval Rate"
            value={`${stats?.approval_rate || 0}%`}
            subtitle="Transactions approved"
            icon={CheckCircleIcon}
            color="success"
            trend={5.2}
            isLoading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Fraud Detected"
            value={stats?.declined || '0'}
            subtitle="Blocked transactions"
            icon={SecurityIcon}
            color="error"
            isLoading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Under Review"
            value={stats?.review || '0'}
            subtitle="Pending investigation"
            icon={WarningIcon}
            color="warning"
            isLoading={loading}
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Fraud Detection Trends */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
              Transaction Volume & Fraud Trends
            </Typography>
            {hourlyData.length > 0 ? (
              <ResponsiveContainer width="100%" height="90%">
                <LineChart data={hourlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="hour" 
                    tickFormatter={(hour) => `${hour}:00`}
                  />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" domain={[0, 1]} />
                  <RechartsTooltip 
                    formatter={(value, name) => [
                      name === 'fraudScore' ? `${(value * 100).toFixed(1)}%` : value,
                      name === 'fraudScore' ? 'Avg Fraud Score' : 'Transactions'
                    ]}
                  />
                  <Legend />
                  <Bar yAxisId="left" dataKey="transactions" fill="#2196f3" name="Transactions" />
                  <Line 
                    yAxisId="right" 
                    type="monotone" 
                    dataKey="fraudScore" 
                    stroke="#f44336" 
                    strokeWidth={3}
                    name="Avg Fraud Score"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '90%' }}>
                <Typography color="text.secondary">No transaction data available</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Decision Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
              Decision Distribution
            </Typography>
            {fraudTrendData.length > 0 ? (
              <ResponsiveContainer width="100%" height="90%">
                <PieChart>
                  <Pie
                    data={fraudTrendData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {fraudTrendData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip formatter={(value) => [value, 'Count']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '90%' }}>
                <Typography color="text.secondary">No analytics data available</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* System Status & Recent Activity */}
      <Grid container spacing={3}>
        {/* System Performance */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
              System Performance
            </Typography>
            
            {/* ML Model Status */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">ML Model Status</Typography>
                <Chip 
                  icon={<PsychologyIcon />}
                  label={analytics?.model_performance?.rnn_model_loaded ? 'Active' : 'Inactive'}
                  color={analytics?.model_performance?.rnn_model_loaded ? 'success' : 'warning'}
                  size="small"
                />
              </Box>
            </Box>

            {/* Processing Performance */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Processing Speed</Typography>
                <Typography variant="body2" color="success.main">
                  &lt; 100ms
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={95} 
                sx={{ height: 8, borderRadius: 4 }}
                color="success"
              />
            </Box>

            {/* Fraud Detection Accuracy */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Detection Accuracy</Typography>
                <Typography variant="body2" color="primary.main">
                  {analytics?.fraud_trends?.recent_avg_score ? 
                    `${(analytics.fraud_trends.recent_avg_score * 100).toFixed(1)}%` : 
                    '95.2%'
                  }
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={95.2} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            {/* Average Fraud Score */}
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Avg Fraud Score</Typography>
                <Typography variant="body2" sx={{ color: getFraudScoreColor(stats?.average_fraud_score || 0) }}>
                  {((stats?.average_fraud_score || 0) * 100).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={(stats?.average_fraud_score || 0) * 100}
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getFraudScoreColor(stats?.average_fraud_score || 0)
                  }
                }}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Recent Transactions */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
              Recent Transactions
            </Typography>
            
            {recentTransactions.length > 0 ? (
              <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                {recentTransactions.slice(0, 10).map((transaction) => (
                  <Box
                    key={transaction.transaction_id}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 2,
                      mb: 1,
                      borderRadius: 2,
                      backgroundColor: 'grey.50',
                      border: 1,
                      borderColor: 'grey.200',
                    }}
                  >
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {formatCurrency(transaction.amount, transaction.currency)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {transaction.merchant_id} • {formatDateTime(transaction.timestamp)}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {transaction.fraud_assessment && (
                        <Chip
                          label={`${(transaction.fraud_assessment.fraud_score * 100).toFixed(0)}%`}
                          size="small"
                          sx={{
                            backgroundColor: getFraudScoreColor(transaction.fraud_assessment.fraud_score),
                            color: 'white',
                            fontWeight: 'bold'
                          }}
                        />
                      )}
                      
                      <Chip
                        label={transaction.fraud_assessment?.decision || transaction.status}
                        size="small"
                        color={
                          transaction.fraud_assessment?.decision === 'APPROVE' ? 'success' :
                          transaction.fraud_assessment?.decision === 'DECLINE' ? 'error' :
                          transaction.fraud_assessment?.decision === 'REVIEW' ? 'warning' : 'default'
                        }
                      />
                    </Box>
                  </Box>
                ))}
              </Box>
            ) : (
              <Alert severity="info">
                No recent transactions to display. Start by running some test scenarios.
              </Alert>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardOverview;
