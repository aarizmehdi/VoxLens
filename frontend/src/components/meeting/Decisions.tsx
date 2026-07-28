/**
 * Decisions Component
 */
import { motion } from "framer-motion";
import { Gavel } from "lucide-react";
import { useReport } from "@/hooks/use-meeting";
import styles from "./Decisions.module.css";

interface DecisionsProps { meetingId: string; }

export function Decisions({ meetingId }: DecisionsProps) {
  const { data: report, isLoading } = useReport(meetingId);

  if (isLoading) return <div className={styles.loading}>{[...Array(3)].map((_, i) => <div key={i} className="skeleton" style={{ height: 40, width: "100%" }} />)}</div>;
  if (!report?.decisions?.length) return <div className={styles.empty}><p>No key decisions recorded in this meeting.</p></div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}><Gavel size={16} className={styles.icon} /><h3>{report.decisions.length} Decision{report.decisions.length !== 1 ? "s" : ""}</h3></div>
      <div className={styles.list}>
        {report.decisions.map((decision, i) => (
          <motion.div key={i} className={`glass-card ${styles.item}`} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}>
            <div className={styles.bullet} />
            <p>{decision}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
