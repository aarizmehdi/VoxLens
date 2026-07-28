/**
 * VoxLens — Global State Store (Zustand)
 *
 * Manages UI state: active meeting, sidebar visibility, etc.
 */

import { create } from "zustand";

interface VoxLensState {
  // Active meeting
  activeMeetingId: string | null;
  setActiveMeetingId: (id: string | null) => void;

  // UI state
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;

  // Active tab in meeting view
  activeTab: "summary" | "transcript" | "actions" | "decisions" | "questions";
  setActiveTab: (tab: VoxLensState["activeTab"]) => void;

  // Processing state
  processingMeetingId: string | null;
  setProcessingMeetingId: (id: string | null) => void;
}

export const useStore = create<VoxLensState>((set) => ({
  activeMeetingId: null,
  setActiveMeetingId: (id) => set({ activeMeetingId: id }),

  sidebarOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  activeTab: "summary",
  setActiveTab: (tab) => set({ activeTab: tab }),

  processingMeetingId: null,
  setProcessingMeetingId: (id) => set({ processingMeetingId: id }),
}));
