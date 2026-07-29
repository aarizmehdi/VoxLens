/**
 * HomePage Component
 *
 * Landing page with hero section and source intake form.
 */

import { motion, type Variants } from "framer-motion";
import { SourceInput } from "@/components/intake/SourceInput";
import styles from "./HomePage.module.css";

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.1,
    },
  },
};

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 30, filter: "blur(4px)" },
  visible: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: { duration: 1, ease: [0.16, 1, 0.3, 1] },
  },
};

export function HomePage() {
  return (
    <div className={styles.container}>
      <motion.div
        className={styles.hero}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.h1 className={styles.title} variants={itemVariants}>
          Meetings that <span className="gradient-text">make sense</span>
        </motion.h1>
        <motion.p className={styles.subtitle} variants={itemVariants}>
          Upload a meeting recording. VoxLens transcribes, summarizes,
          extracts action items, and lets you chat with your meeting content.
        </motion.p>
      </motion.div>

      <motion.div
        className={styles.intakeWrapper}
        initial={{ opacity: 0, y: 40, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ delay: 0.5, duration: 1, ease: [0.16, 1, 0.3, 1] }}
      >
        <SourceInput />
      </motion.div>

      {/* Seductive background elements */}
      <div className={styles.glowOrb1} />
      <div className={styles.glowOrb2} />
    </div>
  );
}
