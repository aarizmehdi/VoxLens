/**
 * Header Component
 *
 * App header with VoxLens branding, navigation, and new meeting action.
 */

import { motion } from "framer-motion";
import { Plus, PanelLeft } from "lucide-react";
import { useStore } from "@/lib/store";
import styles from "./Header.module.css";

export function Header() {
  const activeMeetingId = useStore((s) => s.activeMeetingId);
  const setActiveMeetingId = useStore((s) => s.setActiveMeetingId);
  const toggleSidebar = useStore((s) => s.toggleSidebar);

  return (
    <motion.header
      className={styles.header}
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      <div className={styles.left}>
        <button
          className={styles.menuToggle}
          onClick={toggleSidebar}
          aria-label="Toggle sidebar"
        >
          <PanelLeft size={20} />
        </button>

        <div
          className={styles.logo}
          onClick={() => setActiveMeetingId(null)}
          role="button"
          tabIndex={0}
        >
          <img src="/logo.png" alt="VoxLens Logo" className={styles.logoImage} />
          <span className={styles.logoText}>VoxLens</span>
        </div>
      </div>

      <div className={styles.right}>
        {activeMeetingId && (
          <button
            id="new-meeting-btn"
            className="btn btn-primary"
            onClick={() => setActiveMeetingId(null)}
          >
            <Plus size={16} />
            <span className={styles.newMeetingText}>New Meeting</span>
          </button>
        )}
      </div>
    </motion.header>
  );
}
