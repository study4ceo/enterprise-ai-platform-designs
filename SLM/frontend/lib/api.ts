/**
 * API Client for SLM Platform Backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Model {
  id: number;
  model_id: string;
  name: string;
  size?: string;
  parameters?: number;
  download_status: string;
  is_finetuned: boolean;
  disk_size_mb?: number;
  created_at: string;
}

export interface Dataset {
  id: number;
  dataset_id: string;
  name: string;
  format: string;
  num_samples?: number;
  size_mb?: number;
  created_at: string;
}

export interface TrainingJob {
  id: number;
  job_id: string;
  name: string;
  model_id: string;
  dataset_id: string;
  training_method: string;
  status: string;
  progress_percent: number;
  current_epoch: number;
  current_step: number;
  total_steps?: number;
  train_loss?: number;
  eval_loss?: number;
  gpu_type?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface DashboardStats {
  total_models: number;
  downloaded_models: number;
  finetuned_models: number;
  total_datasets: number;
  total_training_jobs: number;
  active_training_jobs: number;
  completed_training_jobs: number;
  failed_training_jobs: number;
  total_disk_space_gb: number;
  used_disk_space_gb: number;
}

export interface HealthStatus {
  status: string;
  version: string;
  database: string;
  redis: string;
  minio: string;
  gpu_available: boolean;
  gpu_count: number;
}

// API Functions

// Health
export const checkHealth = () => api.get<HealthStatus>('/health');

// Models
export const getModels = (page = 1, pageSize = 20) => 
  api.get<{models: Model[], total: number}>('/api/v1/models', {
    params: { page, page_size: pageSize }
  });

export const getModel = (modelId: string) => 
  api.get<Model>(`/api/v1/models/${modelId}`);

export const deleteModel = (modelId: string) => 
  api.delete(`/api/v1/models/${modelId}`);

// Datasets
export const getDatasets = (page = 1, pageSize = 20) => 
  api.get<{datasets: Dataset[], total: number}>('/api/v1/datasets', {
    params: { page, page_size: pageSize }
  });

export const uploadDataset = (file: File, name: string, description?: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('name', name);
  if (description) formData.append('description', description);
  return api.post('/api/v1/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const deleteDataset = (datasetId: string) => 
  api.delete(`/api/v1/datasets/${datasetId}`);

// Training
export const getTrainingJobs = (page = 1, pageSize = 20, status?: string) => 
  api.get<{jobs: TrainingJob[], total: number}>('/api/v1/training', {
    params: { page, page_size: pageSize, status }
  });

export const getTrainingJob = (jobId: string) => 
  api.get<TrainingJob>(`/api/v1/training/${jobId}`);

export const startTraining = (data: {
  name: string;
  model_id: string;
  dataset_id: string;
  training_method: 'lora' | 'qlora';
  lora_config?: {
    rank?: number;
    alpha?: number;
    dropout?: number;
  };
  training_config?: {
    learning_rate?: number;
    num_epochs?: number;
    batch_size?: number;
  };
}) => api.post<TrainingJob>('/api/v1/training/start', data);

export const cancelTraining = (jobId: string) => 
  api.post(`/api/v1/training/${jobId}/cancel`);

// Inference
export const chatCompletion = (data: {
  model_id: string;
  messages: Array<{role: string; content: string}>;
  temperature?: number;
  max_tokens?: number;
}) => api.post('/api/v1/chat', data);

export const textGeneration = (data: {
  model_id: string;
  prompt: string;
  temperature?: number;
  max_tokens?: number;
}) => api.post('/api/v1/generate', data);

// Dashboard
export const getDashboardStats = () => 
  api.get<DashboardStats>('/api/v1/dashboard/stats');
