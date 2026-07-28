/**
 * Hook: Job Status Polling
 *
 * Polls the backend for job processing progress until complete or failed.
 */

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getJobStatus, type JobStatus } from "@/lib/api";
import { useStore } from "@/lib/store";

export function useJobStatus(meetingId: string | null) {
  const setProcessingMeetingId = useStore((s) => s.setProcessingMeetingId);
  const queryClient = useQueryClient();

  return useQuery<JobStatus>({
    queryKey: ["job-status", meetingId],
    queryFn: () => getJobStatus(meetingId!),
    enabled: !!meetingId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return 2000;
      // Stop polling when complete or failed
      if (data.status === "completed" || data.status === "failed") {
        if (data.status === "completed") {
          setProcessingMeetingId(null);
          queryClient.invalidateQueries({ queryKey: ["meeting", meetingId] });
          queryClient.invalidateQueries({ queryKey: ["meetings"] });
        }
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });
}
