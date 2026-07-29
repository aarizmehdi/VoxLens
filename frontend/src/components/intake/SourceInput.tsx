/**
 * SourceInput Component
 *
 * Combined hero-level input panel with URL field and file upload.
 */

import { FileUpload } from "./FileUpload";
import styles from "./SourceInput.module.css";

export function SourceInput() {
  return (
    <div className={styles.container}>
      <FileUpload />
    </div>
  );
}
