/**
 * FileUpload Component
 *
 * Drag-and-drop file upload zone with visual feedback.
 */

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileAudio } from "lucide-react";
import { useProcessUpload } from "@/hooks/use-process-meeting";
import styles from "./FileUpload.module.css";

const ACCEPTED_TYPES: Record<string, string[]> = {
  "audio/*": [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"],
  "video/*": [".mp4", ".webm", ".mkv", ".avi", ".mov"],
};

export function FileUpload() {
  const { mutate, isPending } = useProcessUpload();

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        mutate({ file });
      }
    },
    [mutate],
  );

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } =
    useDropzone({
      onDrop,
      accept: ACCEPTED_TYPES,
      maxFiles: 1,
      disabled: isPending,
    });

  const file = acceptedFiles[0];

  return (
    <div className={styles.wrapper}>
      <div
        {...getRootProps()}
        className={`${styles.dropzone} ${isDragActive ? styles.active : ""} ${isPending ? styles.processing : ""}`}
        id="file-upload-zone"
      >
        <input {...getInputProps()} id="file-upload-input" />

        <AnimatePresence mode="wait">
          {isPending ? (
            <motion.div
              key="processing"
              className={styles.content}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="spinner spinner-lg" />
              <p className={styles.text}>Processing file...</p>
            </motion.div>
          ) : isDragActive ? (
            <motion.div
              key="drag"
              className={styles.content}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
            >
              <Upload size={32} className={styles.iconActive} />
              <p className={styles.text}>Drop your file here!</p>
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              className={styles.content}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <FileAudio size={28} className={styles.icon} />
              <p className={styles.text}>
                Drop an audio or video file here
              </p>
              <p className={styles.hint}>
                MP3, WAV, M4A, MP4, WebM, MKV — or click to browse
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {file && !isPending && (
        <motion.div
          className={styles.fileInfo}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <FileAudio size={14} />
          <span>{file.name}</span>
          <span className={styles.fileSize}>
            {(file.size / (1024 * 1024)).toFixed(1)}MB
          </span>
        </motion.div>
      )}
    </div>
  );
}
