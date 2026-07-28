/**
 * UrlInput Component
 *
 * YouTube URL input field with gradient border animation and validation.
 */

import { useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { Link2, ArrowRight, Loader2 } from "lucide-react";
import { useProcessUrl } from "@/hooks/use-process-meeting";
import styles from "./UrlInput.module.css";

export function UrlInput() {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const { mutate, isPending } = useProcessUrl();

  const isValidUrl = (value: string) => {
    // Matches standard youtube.com/watch, youtu.be, and youtube.com/shorts with strict 11-char ID
    const youtubeRegex = /^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=|shorts\/))([\w-]{11})(?:\S+)?$/;
    return youtubeRegex.test(value.trim());
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (!url.trim()) {
      setError("Please enter a YouTube URL");
      return;
    }

    if (!isValidUrl(url)) {
      setError("Please enter a valid YouTube URL");
      return;
    }

    mutate(
      { url: url.trim() },
      {
        onError: (err) => setError(err.message),
      },
    );
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={`${styles.inputWrapper} ${url && isValidUrl(url) ? styles.valid : ""}`}>
        <div className={styles.inputIcon}>
          <Link2 size={18} />
        </div>
        <input
          id="youtube-url-input"
          type="url"
          className={styles.input}
          placeholder="Paste a YouTube URL..."
          value={url}
          onChange={(e) => {
            setUrl(e.target.value);
            setError("");
          }}
          disabled={isPending}
          autoComplete="off"
        />
        <motion.button
          type="submit"
          className={styles.submitBtn}
          disabled={isPending || !url.trim()}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          id="process-url-btn"
        >
          {isPending ? (
            <Loader2 size={18} className={styles.spinner} />
          ) : (
            <ArrowRight size={18} />
          )}
        </motion.button>
      </div>

      {error && (
        <motion.p
          className={styles.error}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {error}
        </motion.p>
      )}
    </form>
  );
}
