/**
 * Zustand Store for Global State
 */

import { create } from 'zustand';

interface AppState {
  selectedModel: string | null;
  setSelectedModel: (modelId: string | null) => void;
  
  refreshInterval: number;
  setRefreshInterval: (interval: number) => void;
  
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedModel: null,
  setSelectedModel: (modelId) => set({ selectedModel: modelId }),
  
  refreshInterval: 5000, // 5 seconds default
  setRefreshInterval: (interval) => set({ refreshInterval: interval }),
  
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));
