/**
 * ProcessingStatus Component
 *
 * Multi-step progress indicator that animates through pipeline stages.
 */

import { motion } from "framer-motion";
import {
  Download,
  AudioWaveform,
  FileText,
  Brain,
  Database,
  CheckCircle2,
  XCircle,
  Loader2,
} from "lucide-react";
import { useJobStatus } from "@/hooks/use-job-status";
import styles from "./ProcessingStatus.module.css";

const STEPS = [
  { key: "downloading", label: "Downloading Media", icon: Download },
  { key: "processing_audio", label: "Processing Audio", icon: AudioWaveform },
  { key: "transcribing", label: "Transcribing", icon: FileText },
  { key: "summarizing", label: "Analyzing Content", icon: Brain },
  { key: "embedding", label: "Building Knowledge", icon: Database },
  { key: "completed", label: "Complete", icon: CheckCircle2 },
];

const STATUS_ORDER = STEPS.map((s) => s.key);

interface ProcessingStatusProps {
  meetingId: string;
}

export function ProcessingStatus({ meetingId }: ProcessingStatusProps) {
  const { data: job } = useJobStatus(meetingId);

  if (!job) return null;

  const currentIndex = STATUS_ORDER.indexOf(job.status);
  const isFailed = job.status === "failed";

  return (
    <motion.div
      className={styles.container}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      id="processing-status"
    >
      <div className={styles.header}>
        <h3 className={styles.title}>
          {isFailed ? "Processing Failed" : "Processing Your Meeting"}
        </h3>
        {!isFailed && (
          <span className={styles.progress}>{job.progress}%</span>
        )}
      </div>

      {/* Progress bar */}
      {!isFailed && (
        <div className={styles.progressBar}>
          <motion.div
            className={styles.progressFill}
            initial={{ width: 0 }}
            animate={{ width: `${job.progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      )}

      {/* Steps */}
      <div className={styles.steps}>
        {STEPS.map((step, i) => {
          const isActive = step.key === job.status;
          const isComplete = currentIndex > i;
          const Icon = step.icon;

          return (
            <motion.div
              key={step.key}
              className={`${styles.step} ${
                isActive
                  ? styles.stepActive
                  : isComplete
                    ? styles.stepComplete
                    : styles.stepPending
              }`}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              {isActive && !isFailed && (
                <motion.div
                  className={styles.pulse}
                  animate={{ scale: [1, 1.4, 1], opacity: [0.3, 0, 0.3] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
              )}
              <div className={styles.stepHeader}>
                <div className={styles.stepIcon}>
                  {isActive && !isFailed ? (
                    <Loader2 size={16} className={styles.spinner} />
                  ) : isComplete ? (
                    <CheckCircle2 size={16} />
                  ) : (
                    <Icon size={16} />
                  )}
                </div>
                <span className={styles.stepLabel}>{step.label}</span>
              </div>
              
              {isActive && !isFailed && (
                <motion.div 
                  className={styles.skeletonContainer}
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  transition={{ duration: 0.3 }}
                >
                  <div className={styles.skeletonLine} />
                  <div className={styles.skeletonLine} style={{ width: '85%' }} />
                  <div className={styles.skeletonLine} style={{ width: '60%' }} />
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Error message */}
      {isFailed && job.error_message && (
        <motion.div
          className={styles.error}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <XCircle size={16} />
          <span>{job.error_message}</span>
        </motion.div>
      )}
    </motion.div>
  );
}
