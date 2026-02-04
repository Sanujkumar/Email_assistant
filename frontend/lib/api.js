import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = Cookies.get('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      Cookies.remove('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth APIs
export const authAPI = {
  getLoginUrl: async () => {
    const response = await api.get('/api/auth/login');
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/user');
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post('/api/auth/logout');
    Cookies.remove('token');
    return response.data;
  },
};

// Email APIs
export const emailAPI = {
  listEmails: async (maxResults = 5, query = '') => {
    const response = await api.get('/api/emails/list', {
      params: { max_results: maxResults, query },
    });
    return response.data;
  },
  
  getEmail: async (emailId) => {
    const response = await api.get(`/api/emails/${emailId}`);
    return response.data;
  },
  
  generateReply: async (emailId, context = null) => {
    const response = await api.post('/api/emails/generate-reply', {
      email_id: emailId,
      context,
    });
    return response.data;
  },
  
  sendReply: async (emailId, replyContent) => {
    const response = await api.post('/api/emails/send-reply', null, {
      params: { email_id: emailId, reply_content: replyContent },
    });
    return response.data;
  },
  
  deleteEmail: async (emailId) => {
    const response = await api.delete(`/api/emails/${emailId}`);
    return response.data;
  },
  
  searchEmails: async (query, maxResults = 10) => {
    const response = await api.get(`/api/emails/search/${encodeURIComponent(query)}`, {
      params: { max_results: maxResults },
    });
    return response.data;
  },
  
  categorizeEmails: async () => {
    const response = await api.post('/api/emails/categorize');
    return response.data;
  },
  
  getDailyDigest: async () => {
    const response = await api.get('/api/emails/digest/daily');
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (message) => {
    const response = await api.post('/api/chat/message', { message });
    return response.data;
  },
  
  confirmDelete: async (emailId) => {
    const response = await api.post('/api/chat/confirm-delete', null, {
      params: { email_id: emailId },
    });
    return response.data;
  },
};
