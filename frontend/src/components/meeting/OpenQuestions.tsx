/**
 * OpenQuestions Component
 */
import { motion } from "framer-motion";
import { HelpCircle } from "lucide-react";
import { useReport } from "@/hooks/use-meeting";
import styles from "./OpenQuestions.module.css";

interface OpenQuestionsProps { meetingId: string; }

export function OpenQuestions({ meetingId }: OpenQuestionsProps) {
  const { data: report, isLoading } = useReport(meetingId);

  if (isLoading) return <div className={styles.loading}>{[...Array(3)].map((_, i) => <div key={i} className="skeleton" style={{ height: 40, width: "100%" }} />)}</div>;
  if (!report?.open_questions?.length) return <div className={styles.empty}><p>No open questions or follow-ups identified.</p></div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}><HelpCircle size={16} className={styles.icon} /><h3>{report.open_questions.length} Open Question{report.open_questions.length !== 1 ? "s" : ""}</h3></div>
      <div className={styles.list}>
        {report.open_questions.map((question, i) => (
          <motion.div key={i} className={`glass-card ${styles.item}`} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}>
            <HelpCircle size={14} className={styles.qIcon} />
            <p>{question}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
