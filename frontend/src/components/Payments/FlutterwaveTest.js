/**
 * Flutterwave Integration Test Component
 * Test Flutterwave payment integration and fraud detection
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Payment as PaymentIcon,
  Security as SecurityIcon,
  Link as LinkIcon,
  Webhook as WebhookIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { formatCurrency, formatDateTime } from '../../services/api';
import toast from 'react-hot-toast';

const FlutterwaveTest = () => {
  const [loading, setLoading] = useState(false);
  const [paymentLink, setPaymentLink] = useState(null);
  const [webhookResult, setWebhookResult] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  
  const [formData, setFormData] = useState({
    amount: 50000,
    currency: 'NGN',
    email: 'test@fraudsystem.com',
    phone: '+2348012345678',
    customer_name: 'Test Customer',
    merchant_id: 'FLUTTERWAVE_TEST',
    user_id: 1,
    payment_method: 'card',
    ip_address: '192.168.1.100'
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const createPaymentLink = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/flutterwave/create-payment-link', formData);
      
      if (response.data.status === 'success') {
        setPaymentLink(response.data.data);
        toast.success('Payment link created successfully!');
      } else {
        toast.error('Failed to create payment link');
      }
    } catch (error) {
      console.error('Error creating payment link:', error);
      toast.error('Error creating payment link');
    } finally {
      setLoading(false);
    }
  };

  const testWebhook = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/flutterwave/test-webhook', formData);
      
      if (response.data.status === 'success') {
        setWebhookResult(response.data.data);
        toast.success('Webhook test completed!');
      } else {
        toast.error('Webhook test failed');
      }
    } catch (error) {
      console.error('Error testing webhook:', error);
      toast.error('Error testing webhook');
    } finally {
      setLoading(false);
    }
  };

  const verifyTransaction = async () => {
    const txRef = webhookResult?.webhook_payload?.data?.tx_ref;
    if (!txRef) {
      toast.error('No transaction reference to verify');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`/api/flutterwave/verify/${txRef}`);
      
      if (response.data.status === 'success') {
        setVerificationResult(response.data.data);
        toast.success('Transaction verified!');
      } else {
        toast.error('Transaction verification failed');
      }
    } catch (error) {
      console.error('Error verifying transaction:', error);
      toast.error('Error verifying transaction');
    } finally {
      setLoading(false);
    }
  };

  const quickTests = [
    { label: 'Normal Payment', amount: 50000, merchant_id: 'COFFEE_SHOP' },
    { label: 'High Amount', amount: 750000, merchant_id: 'LUXURY_STORE' },
    { label: 'Suspicious Merchant', amount: 100000, merchant_id: 'CASINO_RESORT' },
    { label: 'Round Amount', amount: 1000000, merchant_id: 'CAR_DEALER' },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 3 }}>
        Flutterwave Integration Test
      </Typography>

      {/* Test Form */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
          Transaction Details
        </Typography>
        
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
            <FormControl fullWidth>
              <InputLabel>Currency</InputLabel>
              <Select
                value={formData.currency}
                onChange={(e) => handleInputChange('currency', e.target.value)}
                label="Currency"
              >
                <MenuItem value="NGN">Nigerian Naira (NGN)</MenuItem>
                <MenuItem value="USD">US Dollar (USD)</MenuItem>
                <MenuItem value="GHS">Ghana Cedi (GHS)</MenuItem>
                <MenuItem value="KES">Kenyan Shilling (KES)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Customer Email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Phone Number"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Customer Name"
              value={formData.customer_name}
              onChange={(e) => handleInputChange('customer_name', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Merchant ID"
              value={formData.merchant_id}
              onChange={(e) => handleInputChange('merchant_id', e.target.value)}
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
              label="IP Address"
              value={formData.ip_address}
              onChange={(e) => handleInputChange('ip_address', e.target.value)}
            />
          </Grid>
        </Grid>

        {/* Quick Test Buttons */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Quick Tests:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
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
        </Box>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<LinkIcon />}
            onClick={createPaymentLink}
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Payment Link'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<WebhookIcon />}
            onClick={testWebhook}
            disabled={loading}
          >
            {loading ? 'Testing...' : 'Test Webhook'}
          </Button>
          {webhookResult && (
            <Button
              variant="outlined"
              startIcon={<SecurityIcon />}
              onClick={verifyTransaction}
              disabled={loading}
            >
              {loading ? 'Verifying...' : 'Verify Transaction'}
            </Button>
          )}
        </Box>
      </Paper>

      {/* Results */}
      <Grid container spacing={3}>
        {/* Payment Link Result */}
        {paymentLink && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <PaymentIcon sx={{ mr: 1 }} />
                  Payment Link Created
                </Typography>
                <Alert severity="success" sx={{ mb: 2 }}>
                  Payment link created successfully!
                </Alert>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Transaction Reference:
                  </Typography>
                  <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                    {paymentLink.tx_ref}
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Payment Link:
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => window.open(paymentLink.payment_link, '_blank')}
                    sx={{ mt: 1 }}
                  >
                    Open Payment Page
                  </Button>
                </Box>
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="body2">Full Response</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ fontSize: '12px', overflow: 'auto' }}>
                      {JSON.stringify(paymentLink, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Webhook Test Result */}
        {webhookResult && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <WebhookIcon sx={{ mr: 1 }} />
                  Webhook Test Result
                </Typography>
                
                {webhookResult.processing_result?.status === 'success' ? (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {webhookResult.message}
                  </Alert>
                ) : (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    Webhook processing failed
                  </Alert>
                )}

                {webhookResult.processing_result?.data && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Fraud Analysis Result:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                      <Chip
                        label={webhookResult.processing_result.data.fraud_decision || 'Unknown'}
                        color={
                          webhookResult.processing_result.data.fraud_decision === 'APPROVE' ? 'success' :
                          webhookResult.processing_result.data.fraud_decision === 'DECLINE' ? 'error' :
                          'warning'
                        }
                      />
                      <Chip
                        label={`Score: ${((webhookResult.processing_result.data.fraud_score || 0) * 100).toFixed(1)}%`}
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="body2">
                      Transaction ID: {webhookResult.processing_result.data.transaction_id}
                    </Typography>
                  </Box>
                )}

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="body2">Webhook Payload</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ fontSize: '12px', overflow: 'auto' }}>
                      {JSON.stringify(webhookResult.webhook_payload, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Verification Result */}
        {verificationResult && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <SecurityIcon sx={{ mr: 1 }} />
                  Transaction Verification
                </Typography>
                
                {verificationResult.status === 'success' ? (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Transaction verified successfully!
                  </Alert>
                ) : (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    Transaction verification failed
                  </Alert>
                )}

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="body2">Verification Data</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <pre style={{ fontSize: '12px', overflow: 'auto' }}>
                      {JSON.stringify(verificationResult, null, 2)}
                    </pre>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* API Configuration Info */}
      <Paper sx={{ p: 3, mt: 3, backgroundColor: 'grey.50' }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
          Flutterwave Configuration
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">
              Public Key
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              FLWPUBK_TEST-b6356446868a345e87f49853ca840527-X
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">
              Secret Key
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              FLWSECK_TEST-29709f78d8dcc264a86c250cd0836bd8-X
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">
              Encryption Key
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              FLWSECK_TEST39addd482452
            </Typography>
          </Grid>
        </Grid>
        <Alert severity="info" sx={{ mt: 2 }}>
          These are test API keys. The system is configured to process test transactions and webhooks 
          for fraud detection analysis.
        </Alert>
      </Paper>
    </Box>
  );
};

export default FlutterwaveTest;
