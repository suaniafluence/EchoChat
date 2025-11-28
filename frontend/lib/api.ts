import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatMessage {
  message: string;
  conversation_history?: Array<{role: string; content: string}>;
}

export interface ChatSource {
  url: string;
  title: string;
  excerpt: string;
}

export interface ChatResponse {
  response: string;
  sources: ChatSource[];
}

export interface ScrapeRequest {
  target_url: string;
  reindex?: boolean;
}

export interface ScrapeJob {
  id: number;
  target_url: string;
  status: string;
  pages_scraped: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface Stats {
  total_pages: number;
  total_chunks: number;
  last_scrape?: string;
  target_url: string;
  scrape_frequency_hours: number;
}

export const chatAPI = {
  sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/api/chat', message);
    return response.data;
  },
};

export const adminAPI = {
  startScrape: async (request: ScrapeRequest): Promise<ScrapeJob> => {
    const response = await api.post<ScrapeJob>('/api/admin/scrape', request);
    return response.data;
  },

  getJobs: async (limit: number = 10): Promise<ScrapeJob[]> => {
    const response = await api.get<ScrapeJob[]>('/api/admin/jobs', { params: { limit } });
    return response.data;
  },

  getJob: async (jobId: number): Promise<ScrapeJob> => {
    const response = await api.get<ScrapeJob>(`/api/admin/jobs/${jobId}`);
    return response.data;
  },

  getStats: async (): Promise<Stats> => {
    const response = await api.get<Stats>('/api/admin/stats');
    return response.data;
  },

  getHomepage: async (): Promise<{url: string; title: string; html: string; scraped_at: string}> => {
    const response = await api.get('/api/admin/homepage');
    return response.data;
  },

  getLogs: async (limit: number = 100): Promise<{logs: Array<{timestamp: string; level: string; logger: string; message: string}>; total: number}> => {
    const response = await api.get('/api/admin/logs', { params: { limit } });
    return response.data;
  },

  loadJobToRAG: async (jobId: number): Promise<{message: string; pages_loaded: number; chunks_indexed: number}> => {
    const response = await api.post(`/api/admin/jobs/${jobId}/load-rag`);
    return response.data;
  },

  deleteJob: async (jobId: number): Promise<{message: string; pages_deleted: number}> => {
    const response = await api.delete(`/api/admin/jobs/${jobId}`);
    return response.data;
  },
};

export default api;
