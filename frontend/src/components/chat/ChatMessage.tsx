/**
 * ChatMessage Component
 *
 * Individual chat message bubble with source citations.
 */

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, ChevronDown, ChevronUp } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage as ChatMessageType } from "@/lib/api";
import styles from "./ChatMessage.module.css";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === "user";
  const hasSources = message.sources && message.sources.length > 0;

  return (
    <motion.div
      className={`${styles.message} ${isUser ? styles.user : styles.assistant}`}
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.175, 0.885, 0.32, 1.275] }}
      layout
    >
      <div className={styles.avatar}>
        {isUser ? <User size={16} /> : <img src="/logo.png" alt="AI" className={styles.botLogo} />}
      </div>
      <div className={styles.content}>
        {isUser ? (
          <p className={styles.text}>{message.content}</p>
        ) : (
          <div className={`${styles.text} ${styles.markdown}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {hasSources && (
          <div className={styles.sourcesWrapper}>
            <button
              className={styles.sourcesToggle}
              onClick={() => setShowSources(!showSources)}
            >
              {showSources ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              {message.sources!.length} source{message.sources!.length !== 1 ? "s" : ""}
            </button>

            <AnimatePresence>
              {showSources && (
                <motion.div
                  className={styles.sources}
                  initial={{ height: 0, opacity: 0, marginTop: 0 }}
                  animate={{ height: "auto", opacity: 1, marginTop: 10 }}
                  exit={{ height: 0, opacity: 0, marginTop: 0 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                >
                  {message.sources!.map((source, i) => (
                    <div key={i} className={styles.source}>
                      <span className={styles.sourceLabel}>
                        Segment {source.chunk_index + 1}
                      </span>
                      <p className={styles.sourceText}>{source.text}</p>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </motion.div>
  );
}
