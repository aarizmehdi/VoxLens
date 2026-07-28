/**
 * ChatPanel Component
 *
 * Full chat interface with message history, typing indicator, and input.
 */

import { useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { MessageSquare, Loader2 } from "lucide-react";
import { useChatHistory, useChat } from "@/hooks/use-chat";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import styles from "./ChatPanel.module.css";

interface ChatPanelProps {
  meetingId: string;
}

export function ChatPanel({ meetingId }: ChatPanelProps) {
  const { data: messages = [] } = useChatHistory(meetingId);
  const { sendMessage, isTyping, isPending } = useChat(meetingId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, isTyping]);

  return (
    <div className={styles.container} id="chat-panel">
      {/* Header */}
      <div className={styles.header}>
        <MessageSquare size={16} />
        <span>Meeting Chat</span>
      </div>

      {/* Messages */}
      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.empty}>
            <MessageSquare size={24} className={styles.emptyIcon} />
            <p>Ask anything about this meeting</p>
            <span>The AI will search the transcript and provide grounded answers</span>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <motion.div
            className={styles.typing}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <Loader2 size={14} className={styles.spinner} />
            <span>Searching meeting content...</span>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isPending} />
    </div>
  );
}
