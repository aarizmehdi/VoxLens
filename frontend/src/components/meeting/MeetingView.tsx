/**
 * MeetingView Component
 *
 * Main meeting detail view with tabs for different content panels.
 * Layout: left side = meeting content (tabbed), right side = chat.
 */

import { useState, useRef, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { useStore } from "@/lib/store";
import { useMeeting } from "@/hooks/use-meeting";
import { SummaryPanel } from "./SummaryPanel";
import { TranscriptPanel } from "./TranscriptPanel";
import { ActionItems } from "./ActionItems";
import { Decisions } from "./Decisions";
import { OpenQuestions } from "./OpenQuestions";
import { ExportButton } from "./ExportButton";
import { ChatPanel } from "@/components/chat/ChatPanel";
import styles from "./MeetingView.module.css";

const TABS = [
  { key: "summary", label: "Summary" },
  { key: "transcript", label: "Transcript" },
  { key: "actions", label: "Actions" },
  { key: "decisions", label: "Decisions" },
  { key: "questions", label: "Questions" },
] as const;

interface MeetingViewProps {
  meetingId: string;
}

export function MeetingView({ meetingId }: MeetingViewProps) {
  const activeTab = useStore((s) => s.activeTab);
  const setActiveTab = useStore((s) => s.setActiveTab);
  const { data: meeting } = useMeeting(meetingId);

  // VS Code style draggable resizer for the chat panel
  const [chatWidth, setChatWidth] = useState(380);
  const isDragging = useRef(false);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    isDragging.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return;
      // Chat is on the right, so new width is window width minus mouse X
      // We bound it between 300px and 800px to prevent breaking the layout
      const newWidth = window.innerWidth - e.clientX;
      if (newWidth > 300 && newWidth < 800) {
        setChatWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      isDragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, []);

  return (
    <div className={styles.container}>
      {/* Left: Content Panel */}
      <div className={styles.contentPanel}>
        {/* Meeting Header */}
        <motion.div
          className={styles.meetingHeader}
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className={styles.headerLeft}>
            <h1 className={styles.meetingTitle}>
              {meeting?.title || "Processing..."}
            </h1>
            {meeting && (
              <div className={styles.meetingMeta}>
                {meeting.status !== "completed" && (
                  <span className="badge badge-info">
                    {meeting.status}
                  </span>
                )}
                {meeting.language && (
                  <span className={styles.metaItem}>
                    {meeting.language === "en" ? "English" : meeting.language === "hi" ? "Hindi" : meeting.language}
                  </span>
                )}
                {meeting.duration_seconds && (
                  <span className={styles.metaItem}>
                    {Math.round(meeting.duration_seconds / 60)} min
                  </span>
                )}
              </div>
            )}
          </div>
          <ExportButton meetingId={meetingId} />
        </motion.div>

        {/* Tabs */}
        <div className="tabs" id="meeting-tabs">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              className={`tab ${activeTab === tab.key ? "active" : ""}`}
              onClick={() => setActiveTab(tab.key)}
              id={`tab-${tab.key}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          className={styles.tabContent}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
        >
          {activeTab === "summary" && <SummaryPanel meetingId={meetingId} />}
          {activeTab === "transcript" && <TranscriptPanel meetingId={meetingId} />}
          {activeTab === "actions" && <ActionItems meetingId={meetingId} />}
          {activeTab === "decisions" && <Decisions meetingId={meetingId} />}
          {activeTab === "questions" && <OpenQuestions meetingId={meetingId} />}
        </motion.div>
      </div>

      {/* VS Code Style Draggable Resizer */}
      <div
        className={styles.resizer}
        onMouseDown={handleMouseDown}
      />

      {/* Right: Chat Panel */}
      <div 
        className={styles.chatPanel}
        style={{ width: `${chatWidth}px` }}
      >
        <ChatPanel meetingId={meetingId} />
      </div>
    </div>
  );
}
