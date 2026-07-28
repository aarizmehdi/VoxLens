/**
 * App Component
 *
 * Root component that manages query client provider and main routing based on state.
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MainLayout } from "@/components/layout/MainLayout";
import { HomePage } from "@/pages/HomePage";
import { MeetingPage } from "@/pages/MeetingPage";
import { useStore } from "@/lib/store";

// Initialize TanStack Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const activeMeetingId = useStore((s) => s.activeMeetingId);

  return (
    <MainLayout>
      {activeMeetingId ? <MeetingPage /> : <HomePage />}
    </MainLayout>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}
