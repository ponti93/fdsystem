/**
 * API Service Layer
 * Handles all communication with the fraud detection backend
 */

import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || (
    process.env.NODE_ENV === 'production' 
      ? '' // Same domain in production (Docker deployment)
      : 'http://localhost:8000'
  ),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth token management
let authToken = localStorage.getItem('auth_token');

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('auth_token');
      authToken = null;
      toast.error('Session expired. Please login again.');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.data?.message) {
      toast.error(error.response.data.message);
    }
    return Promise.reject(error);
  }
);

// Auth functions
export const authAPI = {
  setToken: (token) => {
    authToken = token;
    localStorage.setItem('auth_token', token);
  },

  clearToken: () => {
    authToken = null;
    localStorage.removeItem('auth_token');
  },

  getToken: () => {
    return authToken;
  },

  isAuthenticated: () => {
    return !!authToken;
  }
};

// System APIs
export const systemAPI = {
  getHealth: () => api.get('/health'),
  getSystemInfo: () => api.get('/'),
};

// Transaction APIs
export const transactionAPI = {
  createTransaction: (transactionData) => api.post('/api/transactions', transactionData),
  getTransactions: (limit = 100) => api.get(`/api/transactions?limit=${limit}`),
  getTransaction: (transactionId) => api.get(`/api/transactions/${transactionId}`),
  runTestScenarios: () => api.post('/api/test-scenarios'),
};

// Statistics APIs
export const statsAPI = {
  getStats: () => api.get('/api/stats'),
};

// Admin APIs
export const adminAPI = {
  getUsers: () => api.get('/api/admin/users'),
  getFraudRules: () => api.get('/api/admin/fraud-rules'),
  createFraudRule: (ruleData) => api.post('/api/admin/fraud-rules', ruleData),
  getAnalytics: () => api.get('/api/admin/analytics'),
  clearTransactions: () => api.delete('/api/admin/transactions'),
};

// ML Model APIs
export const mlAPI = {
  getModelInfo: () => api.get('/api/ml/model-info'),
  trainModel: () => api.post('/api/ml/train-model', {}, { timeout: 300000 }), // 5 minutes timeout for training
};

// Flutterwave Payment APIs
export const flutterwaveAPI = {
  createPaymentLink: (transactionData) => api.post('/api/flutterwave/create-payment-link', transactionData),
  testWebhook: (transactionData) => api.post('/api/flutterwave/test-webhook', transactionData),
  verifyTransaction: (transactionId) => api.get(`/api/flutterwave/verify/${transactionId}`),
};

// Utility functions
export const formatCurrency = (amount, currency = 'NGN') => {
  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('en-NG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getDecisionColor = (decision) => {
  switch (decision?.toUpperCase()) {
    case 'APPROVE':
      return '#4caf50'; // Green
    case 'DECLINE':
      return '#f44336'; // Red
    case 'REVIEW':
      return '#ff9800'; // Orange
    default:
      return '#9e9e9e'; // Grey
  }
};

export const getRiskColor = (level) => {
  switch (level?.toUpperCase()) {
    case 'HIGH':
      return '#f44336'; // Red
    case 'MEDIUM':
      return '#ff9800'; // Orange
    case 'LOW':
      return '#4caf50'; // Green
    default:
      return '#9e9e9e'; // Grey
  }
};

export const getFraudScoreColor = (score) => {
  if (score >= 0.8) return '#f44336'; // Red - High risk
  if (score >= 0.5) return '#ff9800'; // Orange - Medium risk
  return '#4caf50'; // Green - Low risk
};

// Error handling utility
export const handleAPIError = (error, defaultMessage = 'An error occurred') => {
  console.error('API Error:', error);
  
  if (error.response?.data?.message) {
    return error.response.data.message;
  } else if (error.message) {
    return error.message;
  }
  
  return defaultMessage;
};

export default api;
