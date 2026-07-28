/**
 * ActionItems Component
 */
import { motion } from "framer-motion";
import { CircleCheck, User, Calendar } from "lucide-react";
import { useReport } from "@/hooks/use-meeting";
import styles from "./ActionItems.module.css";

interface ActionItemsProps { meetingId: string; }

export function ActionItems({ meetingId }: ActionItemsProps) {
  const { data: report, isLoading } = useReport(meetingId);

  if (isLoading) return <div className={styles.loading}>{[...Array(3)].map((_, i) => <div key={i} className="skeleton" style={{ height: 64, width: "100%" }} />)}</div>;
  if (!report?.action_items?.length) return <div className={styles.empty}><p>No action items found in this meeting.</p></div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}><CircleCheck size={16} className={styles.icon} /><h3>{report.action_items.length} Action Item{report.action_items.length !== 1 ? "s" : ""}</h3></div>
      <div className={styles.list}>
        {report.action_items.map((item, i) => (
          <motion.div key={i} className={`glass-card ${styles.item}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
            <p className={styles.task}>{item.task}</p>
            <div className={styles.meta}>
              <span className={styles.metaItem}><User size={12} />{item.owner}</span>
              <span className={styles.metaItem}><Calendar size={12} />{item.deadline}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
