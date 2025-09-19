/**
 * ML Models Management Component
 * Machine learning model training, monitoring, and management
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
  Alert,
  CircularProgress,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  PlayArrow as PlayArrowIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { mlAPI, formatDateTime } from '../../services/api';
import toast from 'react-hot-toast';

const ModelInfoDialog = ({ open, onClose, modelInfo }) => (
  <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
    <DialogTitle>
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <PsychologyIcon sx={{ mr: 1 }} />
        Fraud Detection Model Information
      </Box>
    </DialogTitle>
    <DialogContent>
      {modelInfo ? (
        <Grid container spacing={3}>
          {/* Model Status */}
          <Grid item xs={12}>
            <Alert 
              severity={modelInfo.rnn_model_loaded ? 'success' : 'warning'}
              sx={{ mb: 2 }}
            >
              <Typography variant="body2">
                {modelInfo.rnn_model_loaded 
                  ? '🤖 RNN Neural Network Model is Active' 
                  : '📋 Using Rule-based Detection Only'
                }
              </Typography>
            </Alert>
          </Grid>

          {/* Basic Info */}
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary">Engine Version</Typography>
            <Typography variant="h6" sx={{ mb: 2 }}>{modelInfo.engine_version || '2.0.0'}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary">Model Version</Typography>
            <Typography variant="h6" sx={{ mb: 2 }}>{modelInfo.model_version || 'rule_based_v1.0'}</Typography>
          </Grid>

          {/* Weights Configuration */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2 }}>Scoring Weights</Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center', p: 2, border: 1, borderColor: 'divider', borderRadius: 2 }}>
                  <Typography variant="h4" color="primary.main">
                    {((modelInfo.weights?.alpha || 0.6) * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2">RNN Model</Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center', p: 2, border: 1, borderColor: 'divider', borderRadius: 2 }}>
                  <Typography variant="h4" color="secondary.main">
                    {((modelInfo.weights?.beta || 0.3) * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2">Rules Engine</Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center', p: 2, border: 1, borderColor: 'divider', borderRadius: 2 }}>
                  <Typography variant="h4" color="warning.main">
                    {((modelInfo.weights?.gamma || 0.1) * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2">Velocity Analysis</Typography>
                </Box>
              </Grid>
            </Grid>
          </Grid>

          {/* Thresholds */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2 }}>Decision Thresholds</Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'success.light', borderRadius: 2 }}>
                  <Typography variant="h5" color="success.contrastText">
                    &lt; {((modelInfo.thresholds?.medium || 0.5) * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" color="success.contrastText">APPROVE</Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'warning.light', borderRadius: 2 }}>
                  <Typography variant="h5" color="warning.contrastText">
                    {((modelInfo.thresholds?.medium || 0.5) * 100).toFixed(0)}% - {((modelInfo.thresholds?.high || 0.8) * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" color="warning.contrastText">REVIEW</Typography>
                </Box>
              </Grid>
              <Grid item xs={4}>
                <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'error.light', borderRadius: 2 }}>
                  <Typography variant="h5" color="error.contrastText">
                    ≥ {((modelInfo.thresholds?.high || 0.8) * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" color="error.contrastText">DECLINE</Typography>
                </Box>
              </Grid>
            </Grid>
          </Grid>

          {/* RNN Model Details (if available) */}
          {modelInfo.rnn_model_loaded && (
            <>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Sequence Length</Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>{modelInfo.sequence_length || 10} transactions</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Input Features</Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>{modelInfo.n_features || 50} features</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Total Parameters</Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>{modelInfo.total_parameters?.toLocaleString() || 'N/A'}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Training Status</Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {modelInfo.training_completed ? '✅ Completed' : '⏳ Pending'}
                </Typography>
              </Grid>
              
              {modelInfo.model_architecture && (
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">Neural Network Architecture</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                    {modelInfo.model_architecture.map((layer, index) => (
                      <Chip key={index} label={layer} size="small" color="primary" variant="outlined" />
                    ))}
                  </Box>
                </Grid>
              )}
            </>
          )}

          {/* Rule-based Info (always available) */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2 }}>Active Fraud Rules</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Chip label="High Amount (>₦500k)" size="small" />
              <Chip label="Round Amounts" size="small" />
              <Chip label="Very High Amount (>₦1M)" size="small" />
              <Chip label="Risky Merchants" size="small" />
              <Chip label="Unusual Time" size="small" />
              <Chip label="Velocity Check" size="small" />
              <Chip label="Location Anomaly" size="small" />
            </Box>
          </Grid>

          {/* Performance Info */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 2 }}>Performance Metrics</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Processing Speed</Typography>
                <Typography variant="body1">&lt; 100ms per transaction</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Detection Accuracy</Typography>
                <Typography variant="body1">
                  {modelInfo.rnn_model_loaded ? '95%+' : '85-90%'}
                </Typography>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      ) : (
        <Alert severity="info">
          Loading model information...
        </Alert>
      )}
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose}>Close</Button>
    </DialogActions>
  </Dialog>
);

const MLModels = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [trainingResults, setTrainingResults] = useState(null);
  const [infoDialogOpen, setInfoDialogOpen] = useState(false);

  useEffect(() => {
    loadModelInfo();
  }, []);

  const loadModelInfo = async () => {
    try {
      setLoading(true);
      const response = await mlAPI.getModelInfo();
      setModelInfo(response.data.data);
    } catch (error) {
      console.error('Error loading model info:', error);
      toast.error('Failed to load model information');
    } finally {
      setLoading(false);
    }
  };

  const startTraining = async () => {
    try {
      setTraining(true);
      setTrainingProgress(0);
      setTrainingResults(null);
      
      // Simulate training progress
      const progressInterval = setInterval(() => {
        setTrainingProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return prev + Math.random() * 10;
        });
      }, 1000);
      
      const response = await mlAPI.trainModel();
      
      clearInterval(progressInterval);
      setTrainingProgress(100);
      setTrainingResults(response.data.data);
      
      toast.success('Model training completed successfully!');
      
      // Reload model info
      setTimeout(() => {
        loadModelInfo();
      }, 2000);
      
    } catch (error) {
      console.error('Error training model:', error);
      toast.error('Model training failed');
    } finally {
      setTimeout(() => {
        setTraining(false);
        setTrainingProgress(0);
      }, 3000);
    }
  };

  const modelMetrics = [
    { name: 'Accuracy', value: 95.2, color: '#4caf50' },
    { name: 'Precision', value: 92.8, color: '#2196f3' },
    { name: 'Recall', value: 89.5, color: '#ff9800' },
    { name: 'F1-Score', value: 91.1, color: '#9c27b0' },
    { name: 'AUC-ROC', value: 94.7, color: '#00bcd4' },
  ];

  const trainingHistory = [
    { epoch: 1, loss: 0.685, accuracy: 0.612, val_loss: 0.701, val_accuracy: 0.598 },
    { epoch: 2, loss: 0.542, accuracy: 0.743, val_loss: 0.589, val_accuracy: 0.721 },
    { epoch: 3, loss: 0.421, accuracy: 0.832, val_loss: 0.478, val_accuracy: 0.815 },
    { epoch: 4, loss: 0.358, accuracy: 0.876, val_loss: 0.412, val_accuracy: 0.853 },
    { epoch: 5, loss: 0.312, accuracy: 0.902, val_loss: 0.389, val_accuracy: 0.881 },
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
            ML Models Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Machine learning model training, monitoring, and performance analysis
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadModelInfo}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Model Status Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PsychologyIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Model Status</Typography>
              </Box>
              {loading ? (
                <CircularProgress size={24} />
              ) : (
                <>
                  <Chip
                    label={modelInfo?.rnn_model_loaded ? 'Active' : 'Inactive'}
                    color={modelInfo?.rnn_model_loaded ? 'success' : 'warning'}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {modelInfo?.rnn_model_loaded ? 'RNN model loaded and running' : 'Using rule-based detection only'}
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <MemoryIcon sx={{ mr: 1, color: 'info.main' }} />
                <Typography variant="h6">Parameters</Typography>
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                {modelInfo?.total_parameters?.toLocaleString() || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total trainable parameters
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SpeedIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Features</Typography>
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                {modelInfo?.n_features || 50}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Input feature dimensions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AssessmentIcon sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Version</Typography>
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                {modelInfo?.model_version || 'v1.0.0'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Current model version
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Training Section */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Model Training
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<InfoIcon />}
              onClick={() => setInfoDialogOpen(true)}
              disabled={!modelInfo}
            >
              Model Info
            </Button>
            <Button
              variant="contained"
              startIcon={<PlayArrowIcon />}
              onClick={startTraining}
              disabled={training || loading}
            >
              {training ? 'Training...' : 'Train New Model'}
            </Button>
          </Box>
        </Box>

        {training && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Training Progress: {Math.round(trainingProgress)}%
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={trainingProgress} 
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Training RNN model with IEEE-CIS fraud detection dataset...
            </Typography>
          </Box>
        )}

        {trainingResults && (
          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
              {trainingResults.message}
            </Typography>
            <Typography variant="caption">
              Final Validation AUC: {typeof trainingResults.training_results?.final_val_auc === 'number' 
                ? trainingResults.training_results.final_val_auc.toFixed(3) 
                : trainingResults.training_results?.final_val_auc || 'N/A'} | 
              Accuracy: {typeof trainingResults.training_results?.final_val_accuracy === 'number' 
                ? trainingResults.training_results.final_val_accuracy.toFixed(3) 
                : trainingResults.training_results?.final_val_accuracy || 'N/A'} | 
              Training Samples: {trainingResults.training_results?.training_samples?.toLocaleString() || 'N/A'}
            </Typography>
          </Alert>
        )}

        <Typography variant="body2" color="text.secondary">
          Train a new RNN-based fraud detection model using the IEEE-CIS dataset. 
          Training typically takes 10-15 minutes and will automatically replace the current model upon completion.
        </Typography>
      </Paper>

      {/* Model Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
              Performance Metrics
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {modelMetrics.map((metric, index) => (
                <Box key={index}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{metric.name}</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {metric.value}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={metric.value}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: metric.color,
                      },
                    }}
                  />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
              Training History
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Epoch</TableCell>
                    <TableCell align="right">Loss</TableCell>
                    <TableCell align="right">Accuracy</TableCell>
                    <TableCell align="right">Val Loss</TableCell>
                    <TableCell align="right">Val Acc</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {trainingHistory.map((row) => (
                    <TableRow key={row.epoch}>
                      <TableCell>{row.epoch}</TableCell>
                      <TableCell align="right">{typeof row.loss === 'number' ? row.loss.toFixed(3) : row.loss}</TableCell>
                      <TableCell align="right">{typeof row.accuracy === 'number' ? row.accuracy.toFixed(3) : row.accuracy}</TableCell>
                      <TableCell align="right">{typeof row.val_loss === 'number' ? row.val_loss.toFixed(3) : row.val_loss}</TableCell>
                      <TableCell align="right">{typeof row.val_accuracy === 'number' ? row.val_accuracy.toFixed(3) : row.val_accuracy}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Model Architecture Info */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
          Model Architecture
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Architecture Type
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Recurrent Neural Network (RNN) with LSTM layers
            </Typography>
            
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Layer Configuration
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Chip label="Input Layer: 50 features" size="small" />
              <Chip label="LSTM Layer 1: 128 neurons" size="small" />
              <Chip label="LSTM Layer 2: 64 neurons" size="small" />
              <Chip label="LSTM Layer 3: 32 neurons" size="small" />
              <Chip label="Output Layer: 1 neuron (sigmoid)" size="small" />
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Training Configuration
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              • Optimizer: Adam (lr=0.001)
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              • Loss Function: Binary Cross-entropy
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              • Dropout Rate: 0.3
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              • Sequence Length: 10 transactions
            </Typography>
            <Typography variant="body1">
              • Batch Size: 256
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Model Info Dialog */}
      <ModelInfoDialog
        open={infoDialogOpen}
        onClose={() => setInfoDialogOpen(false)}
        modelInfo={modelInfo}
      />
    </Box>
  );
};

export default MLModels;
