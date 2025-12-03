import axios from 'axios';

// Centralize the API base URL so it's easy to point the UI at a different backend.
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});
