/**
 * Sidebar Component
 *
 * Meeting history list with status indicators.
 */

import { motion, AnimatePresence } from "framer-motion";
import { Clock, AlertCircle, Loader2, MessageSquare } from "lucide-react";
import { useMeetings } from "@/hooks/use-meeting";
import { useStore } from "@/lib/store";
import { formatDate } from "@/lib/utils";
import styles from "./Sidebar.module.css";

const STATUS_ICONS: Record<string, React.ReactNode> = {
  completed: <MessageSquare size={14} className={styles.statusCompleted} />,
  failed: <AlertCircle size={14} className={styles.statusError} />,
  pending: <Clock size={14} className={styles.statusPending} />,
};

const PROCESSING_STATUSES = [
  "downloading",
  "processing_audio",
  "transcribing",
  "summarizing",
  "embedding",
];

export function Sidebar() {
  const sidebarOpen = useStore((s) => s.sidebarOpen);
  const activeMeetingId = useStore((s) => s.activeMeetingId);
  const setActiveMeetingId = useStore((s) => s.setActiveMeetingId);
  const setSidebarOpen = useStore((s) => s.setSidebarOpen);
  const { data } = useMeetings();

  const allMeetings = data?.meetings ?? [];
  const completedMeetings = allMeetings
    .filter((m) => m.status === "completed")
    .slice(0, 5);

  return (
    <AnimatePresence>
      {sidebarOpen && (
        <motion.aside
          className={styles.sidebar}
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 300, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className={styles.inner}>
            <div className={styles.sectionTitle}>
              Recent
            </div>

            <div className={styles.list}>
              {completedMeetings.length === 0 && (
                <div className={styles.empty}>
                  No completed meetings.
                  <br />
                  Upload a file to get started!
                </div>
              )}

              {completedMeetings.map((meeting, i) => {
                const isActive = meeting.id === activeMeetingId;
                const isProcessing = PROCESSING_STATUSES.includes(meeting.status);
                const statusIcon = isProcessing ? (
                  <Loader2 size={14} className={styles.spinner} />
                ) : (
                  STATUS_ICONS[meeting.status] ?? <Clock size={14} className={styles.statusPending} />
                );

                return (
                  <motion.button
                    key={meeting.id}
                    className={`${styles.item} ${isActive ? styles.itemActive : ""}`}
                    onClick={() => {
                      setActiveMeetingId(meeting.id);
                      if (window.innerWidth < 1024) {
                        setSidebarOpen(false);
                      } else {
                        // Optional: auto-close on desktop too, matching user request
                        setSidebarOpen(false);
                      }
                    }}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    id={`meeting-item-${meeting.id}`}
                  >
                    <div className={styles.itemHeader}>
                      {statusIcon}
                      <span className={styles.itemTitle}>
                        {meeting.title
                          ? meeting.title
                          : meeting.source_type === "youtube"
                            ? "YouTube Video"
                            : meeting.file_name
                              ? meeting.file_name
                              : "Untitled"}
                      </span>
                    </div>
                    <div className={styles.itemMeta}>
                      {formatDate(meeting.created_at)}
                    </div>
                    {isProcessing && (
                      <div className={styles.progressBar}>
                        <motion.div
                          className={styles.progressFill}
                          initial={{ width: 0 }}
                          animate={{ width: `${meeting.progress}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    )}
                  </motion.button>
                );
              })}
            </div>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
