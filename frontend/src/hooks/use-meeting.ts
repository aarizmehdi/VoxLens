/**
 * Hook: Meeting Data
 *
 * Queries for meeting, transcript, and report data.
 */

import { useQuery } from "@tanstack/react-query";
import {
  getMeeting,
  getMeetings,
  getTranscript,
  getReport,
} from "@/lib/api";

export function useMeetings() {
  return useQuery({
    queryKey: ["meetings"],
    queryFn: () => getMeetings(),
  });
}

export function useMeeting(meetingId: string | null) {
  return useQuery({
    queryKey: ["meeting", meetingId],
    queryFn: () => getMeeting(meetingId!),
    enabled: !!meetingId,
  });
}

export function useTranscript(meetingId: string | null) {
  return useQuery({
    queryKey: ["transcript", meetingId],
    queryFn: () => getTranscript(meetingId!),
    enabled: !!meetingId,
  });
}

export function useReport(meetingId: string | null) {
  return useQuery({
    queryKey: ["report", meetingId],
    queryFn: () => getReport(meetingId!),
    enabled: !!meetingId,
  });
}
