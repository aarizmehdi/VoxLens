/**
 * Hook: Chat
 *
 * Manages chat state, message sending, and history.
 */

import { useState, useCallback } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  sendChatMessage,
  getChatHistory,
  type ChatMessage,
  type ChatResponse,
} from "@/lib/api";

export function useChatHistory(meetingId: string | null) {
  return useQuery<ChatMessage[]>({
    queryKey: ["chat-history", meetingId],
    queryFn: () => getChatHistory(meetingId!),
    enabled: !!meetingId,
  });
}

export function useChat(meetingId: string | null) {
  const queryClient = useQueryClient();
  const [isTyping, setIsTyping] = useState(false);

  const mutation = useMutation<ChatResponse, Error, string>({
    mutationFn: async (message: string) => {
      setIsTyping(true);
      return sendChatMessage(meetingId!, message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-history", meetingId] });
      setIsTyping(false);
    },
    onError: () => {
      setIsTyping(false);
    },
  });

  const sendMessage = useCallback(
    (message: string) => {
      if (!meetingId || !message.trim()) return;
      // Optimistically add user message to cache
      queryClient.setQueryData<ChatMessage[]>(
        ["chat-history", meetingId],
        (old = []) => [
          ...old,
          {
            id: `temp-${Date.now()}`,
            role: "user" as const,
            content: message,
            sources: null,
            created_at: new Date().toISOString(),
          },
        ],
      );
      mutation.mutate(message);
    },
    [meetingId, mutation, queryClient],
  );

  return {
    sendMessage,
    isTyping,
    isPending: mutation.isPending,
    error: mutation.error,
  };
}
