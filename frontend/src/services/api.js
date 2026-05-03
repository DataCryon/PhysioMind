/**
 * API service layer.
 * Centralized Axios instance with all backend API calls.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes — PDF processing can be slow
  headers: {
    'Accept': 'application/json',
  },
});

// Response interceptor for consistent error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';

    console.error('[API Error]', message);
    return Promise.reject(new Error(message));
  }
);

/**
 * Upload a PDF document.
 * @param {File} file - The PDF file to upload.
 * @param {Function} onProgress - Optional progress callback (0-100).
 */
export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent);
      }
    },
  });

  return response.data;
}

/**
 * Fetch all uploaded documents.
 */
export async function getDocuments() {
  const response = await api.get('/documents');
  return response.data;
}

/**
 * Delete a document by its ID.
 * @param {string} fileId
 */
export async function deleteDocument(fileId) {
  const response = await api.delete(`/documents/${fileId}`);
  return response.data;
}

/**
 * Ask a question against uploaded documents.
 */
export async function askQuestion(question, history = [], fileId = null, systemPrompt = null, sessionId = null) {
  const payload = { 
    question, 
    history: history.map(m => ({ role: m.role, content: m.content })),
    file_id: fileId,
    session_id: sessionId
  };
  
  if (systemPrompt && systemPrompt.trim()) {
    payload.system_prompt = systemPrompt.trim();
  }

  const response = await api.post('/query', payload);
  return response.data;
}

/**
 * Session management
 */
export async function getSessions() {
  const response = await api.get('/sessions');
  return response.data;
}

export async function createSession(title) {
  const response = await api.post('/sessions', null, { params: { title } });
  return response.data;
}

export async function getSessionMessages(sessionId) {
  const response = await api.get(`/sessions/${sessionId}/messages`);
  return response.data;
}

export async function deleteSession(sessionId) {
  const response = await api.delete(`/sessions/${sessionId}`);
  return response.data;
}

/**
 * Health check.
 */
export async function checkHealth() {
  const response = await api.get('/health');
  return response.data;
}

export default api;
