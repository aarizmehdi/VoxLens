/**
 * Hook: Process Meeting
 * 
 * TanStack Query mutation for submitting a URL or file for processing.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { processUrl, processUpload, type Meeting } from "@/lib/api";
import { useStore } from "@/lib/store";

export function useProcessUrl() {
  const queryClient = useQueryClient();
  const setProcessingMeetingId = useStore((s) => s.setProcessingMeetingId);
  const setActiveMeetingId = useStore((s) => s.setActiveMeetingId);

  return useMutation({
    mutationFn: ({ url, language }: { url: string; language?: string }) =>
      processUrl(url, language),
    onSuccess: (meeting: Meeting) => {
      setProcessingMeetingId(meeting.id);
      setActiveMeetingId(meeting.id);
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
    },
  });
}

export function useProcessUpload() {
  const queryClient = useQueryClient();
  const setProcessingMeetingId = useStore((s) => s.setProcessingMeetingId);
  const setActiveMeetingId = useStore((s) => s.setActiveMeetingId);

  return useMutation({
    mutationFn: ({ file, language }: { file: File; language?: string }) =>
      processUpload(file, language),
    onSuccess: (meeting: Meeting) => {
      setProcessingMeetingId(meeting.id);
      setActiveMeetingId(meeting.id);
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
    },
  });
}
