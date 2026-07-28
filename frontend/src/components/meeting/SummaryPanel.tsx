/**
 * SummaryPanel Component
 *
 * Displays the meeting summary, bullet points, and key takeaways.
 */

import { motion } from "framer-motion";
import { Sparkles, Lightbulb, List } from "lucide-react";
import { useReport } from "@/hooks/use-meeting";
import styles from "./SummaryPanel.module.css";

interface SummaryPanelProps {
  meetingId: string;
}

export function SummaryPanel({ meetingId }: SummaryPanelProps) {
  const { data: report, isLoading } = useReport(meetingId);

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <div className="skeleton" style={{ height: 80, width: "100%" }} />
        <div className="skeleton" style={{ height: 120, width: "100%" }} />
        <div className="skeleton" style={{ height: 80, width: "100%" }} />
      </div>
    );
  }

  if (!report) {
    return (
      <div className={styles.empty}>
        <p>Summary not available yet. Check back once processing is complete.</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Overview */}
      {report.summary && (
        <motion.div
          className={`glass-card ${styles.section}`}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className={styles.sectionHeader}>
            <Sparkles size={16} className={styles.iconAccent} />
            <h3>Overview</h3>
          </div>
          <p className={styles.summaryText}>{report.summary}</p>
        </motion.div>
      )}

      {/* Key Points */}
      {report.bullet_points && report.bullet_points.length > 0 && (
        <motion.div
          className={`glass-card ${styles.section}`}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className={styles.sectionHeader}>
            <List size={16} className={styles.iconAccent} />
            <h3>Key Points</h3>
          </div>
          <ul className={styles.list}>
            {report.bullet_points.map((point, i) => (
              <motion.li
                key={i}
                className={styles.listItem}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 + i * 0.05 }}
              >
                {point}
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Key Takeaways */}
      {report.key_takeaways && report.key_takeaways.length > 0 && (
        <motion.div
          className={`glass-card ${styles.section}`}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className={styles.sectionHeader}>
            <Lightbulb size={16} className={styles.iconWarn} />
            <h3>Key Takeaways</h3>
          </div>
          <ul className={styles.list}>
            {report.key_takeaways.map((takeaway, i) => (
              <motion.li
                key={i}
                className={`${styles.listItem} ${styles.takeaway}`}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.35 + i * 0.05 }}
              >
                {takeaway}
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}
    </div>
  );
}
