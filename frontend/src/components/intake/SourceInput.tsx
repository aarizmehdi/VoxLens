/**
 * SourceInput Component
 *
 * Combined hero-level input panel with URL field and file upload.
 */

import { UrlInput } from "./UrlInput";
import { FileUpload } from "./FileUpload";
import styles from "./SourceInput.module.css";

export function SourceInput() {
  return (
    <div className={styles.container}>
      <UrlInput />

      <div className={styles.divider}>
        <span className={styles.dividerLine} />
        <span className={styles.dividerText}>or</span>
        <span className={styles.dividerLine} />
      </div>

      <FileUpload />
    </div>
  );
}
