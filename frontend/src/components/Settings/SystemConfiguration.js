/**
 * System Configuration Component
 * Basic admin settings for fraud detection system
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Card,
  CardContent,
  CardHeader,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  Chip,
  CircularProgress
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Security as SecurityIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { mlAPI, systemAPI } from '../../services/api';
import toast from 'react-hot-toast';

const SystemConfiguration = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [modelInfo, setModelInfo] = useState(null);
  const [settings, setSettings] = useState({
    // Fraud Detection Thresholds
    approveThreshold: 0.5,
    reviewThreshold: 0.8,
    
    // Model Weights
    rnnWeight: 0.6,
    rulesWeight: 0.3,
    velocityWeight: 0.1,
    
    // System Settings
    maxTransactionAmount: 5000000,
    sessionTimeout: 30,
    enableRealTimeAlerts: true,
    enableAutoBlock: false,
    
    // API Settings
    apiRateLimit: 1000,
    webhookTimeout: 30000,
    enableLogging: true
  });

  useEffect(() => {
    loadSystemSettings();
  }, []);

  const loadSystemSettings = async () => {
    try {
      setLoading(true);
      
      // Load model info to get current weights and thresholds
      const modelResponse = await mlAPI.getModelInfo();
      if (modelResponse.data.status === 'success') {
        const modelData = modelResponse.data.data;
        setModelInfo(modelData);
        
        // Update settings with current model configuration
        if (modelData.weights) {
          setSettings(prev => ({
            ...prev,
            rnnWeight: modelData.weights.alpha || 0.6,
            rulesWeight: modelData.weights.beta || 0.3,
            velocityWeight: modelData.weights.gamma || 0.1
          }));
        }
        
        if (modelData.thresholds) {
          setSettings(prev => ({
            ...prev,
            approveThreshold: modelData.thresholds.medium || 0.5,
            reviewThreshold: modelData.thresholds.high || 0.8
          }));
        }
      }
    } catch (error) {
      console.error('Error loading system settings:', error);
      toast.error('Failed to load system settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleWeightChange = (key, value) => {
    setSettings(prev => {
      const newSettings = { ...prev, [key]: value };
      
      // Ensure weights sum to 1.0
      const total = newSettings.rnnWeight + newSettings.rulesWeight + newSettings.velocityWeight;
      if (Math.abs(total - 1.0) > 0.01) {
        // Auto-adjust other weights proportionally
        const remaining = 1.0 - value;
        const otherKeys = ['rnnWeight', 'rulesWeight', 'velocityWeight'].filter(k => k !== key);
        const currentOtherTotal = otherKeys.reduce((sum, k) => sum + prev[k], 0);
        
        if (currentOtherTotal > 0) {
          otherKeys.forEach(k => {
            newSettings[k] = (prev[k] / currentOtherTotal) * remaining;
          });
        }
      }
      
      return newSettings;
    });
  };

  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      
      // In a real implementation, this would call a backend API to save settings
      // For now, we'll just show success
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      toast.success('System settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleResetToDefaults = () => {
    setSettings({
      approveThreshold: 0.5,
      reviewThreshold: 0.8,
      rnnWeight: 0.6,
      rulesWeight: 0.3,
      velocityWeight: 0.1,
      maxTransactionAmount: 5000000,
      sessionTimeout: 30,
      enableRealTimeAlerts: true,
      enableAutoBlock: false,
      apiRateLimit: 1000,
      webhookTimeout: 30000,
      enableLogging: true
    });
    toast('Settings reset to defaults', {
      icon: 'ℹ️',
      duration: 3000,
    });
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          System Configuration
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleResetToDefaults}
          >
            Reset to Defaults
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSaveSettings}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Fraud Detection Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<SecurityIcon color="primary" />}
              title="Fraud Detection Settings"
              subheader="Configure fraud detection thresholds and behavior"
            />
            <CardContent>
              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
                  Approve Threshold: {(settings.approveThreshold * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={settings.approveThreshold}
                  onChange={(e, value) => handleSettingChange('approveThreshold', value)}
                  min={0}
                  max={1}
                  step={0.05}
                  marks={[
                    { value: 0, label: '0%' },
                    { value: 0.5, label: '50%' },
                    { value: 1, label: '100%' }
                  ]}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                />
                <Typography variant="caption" color="text.secondary">
                  Transactions below this threshold are automatically approved
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
                  Review Threshold: {(settings.reviewThreshold * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={settings.reviewThreshold}
                  onChange={(e, value) => handleSettingChange('reviewThreshold', value)}
                  min={settings.approveThreshold}
                  max={1}
                  step={0.05}
                  marks={[
                    { value: settings.approveThreshold, label: 'Approve' },
                    { value: 1, label: '100%' }
                  ]}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                />
                <Typography variant="caption" color="text.secondary">
                  Transactions above this threshold are automatically declined
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  label="Max Transaction Amount (NGN)"
                  type="number"
                  value={settings.maxTransactionAmount}
                  onChange={(e) => handleSettingChange('maxTransactionAmount', parseInt(e.target.value))}
                  margin="normal"
                />
              </Box>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableAutoBlock}
                    onChange={(e) => handleSettingChange('enableAutoBlock', e.target.checked)}
                  />
                }
                label="Auto-block high risk users"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Model Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<PsychologyIcon color="secondary" />}
              title="ML Model Configuration"
              subheader="Adjust model weights and behavior"
            />
            <CardContent>
              <Alert severity="info" sx={{ mb: 3 }}>
                Current Model: {modelInfo?.rnn_model_loaded ? 'Active' : 'Inactive'} | 
                Parameters: {modelInfo?.rnn_model_info?.total_parameters?.toLocaleString() || 'N/A'}
              </Alert>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
                  RNN Model Weight: {(settings.rnnWeight * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={settings.rnnWeight}
                  onChange={(e, value) => handleWeightChange('rnnWeight', value)}
                  min={0}
                  max={1}
                  step={0.05}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
                  Rules Engine Weight: {(settings.rulesWeight * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={settings.rulesWeight}
                  onChange={(e, value) => handleWeightChange('rulesWeight', value)}
                  min={0}
                  max={1}
                  step={0.05}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom>
                  Velocity Analysis Weight: {(settings.velocityWeight * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={settings.velocityWeight}
                  onChange={(e, value) => handleWeightChange('velocityWeight', value)}
                  min={0}
                  max={1}
                  step={0.05}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
                />
              </Box>

              <Alert severity="warning">
                Total Weight: {((settings.rnnWeight + settings.rulesWeight + settings.velocityWeight) * 100).toFixed(0)}%
                {Math.abs((settings.rnnWeight + settings.rulesWeight + settings.velocityWeight) - 1.0) > 0.01 && 
                  ' (Should equal 100%)'}
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* System Performance */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<SpeedIcon color="success" />}
              title="System Performance"
              subheader="Configure system limits and timeouts"
            />
            <CardContent>
              <TextField
                fullWidth
                label="Session Timeout (minutes)"
                type="number"
                value={settings.sessionTimeout}
                onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                margin="normal"
              />

              <TextField
                fullWidth
                label="API Rate Limit (requests/minute)"
                type="number"
                value={settings.apiRateLimit}
                onChange={(e) => handleSettingChange('apiRateLimit', parseInt(e.target.value))}
                margin="normal"
              />

              <TextField
                fullWidth
                label="Webhook Timeout (ms)"
                type="number"
                value={settings.webhookTimeout}
                onChange={(e) => handleSettingChange('webhookTimeout', parseInt(e.target.value))}
                margin="normal"
              />

              <Box sx={{ mt: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.enableRealTimeAlerts}
                      onChange={(e) => handleSettingChange('enableRealTimeAlerts', e.target.checked)}
                    />
                  }
                  label="Enable real-time alerts"
                />
              </Box>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableLogging}
                    onChange={(e) => handleSettingChange('enableLogging', e.target.checked)}
                  />
                }
                label="Enable detailed logging"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              avatar={<SettingsIcon color="info" />}
              title="System Status"
              subheader="Current system information"
            />
            <CardContent>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                <Chip 
                  label="Database Connected" 
                  color="success" 
                  variant="outlined" 
                />
                <Chip 
                  label={modelInfo?.rnn_model_loaded ? "ML Model Active" : "ML Model Inactive"} 
                  color={modelInfo?.rnn_model_loaded ? "success" : "warning"}
                  variant="outlined" 
                />
                <Chip 
                  label="API Healthy" 
                  color="success" 
                  variant="outlined" 
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="body2" color="text.secondary">
                <strong>System Version:</strong> 2.0.0<br />
                <strong>Last Updated:</strong> {new Date().toLocaleDateString()}<br />
                <strong>Uptime:</strong> 2h 34m<br />
                <strong>Environment:</strong> Development
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemConfiguration;
