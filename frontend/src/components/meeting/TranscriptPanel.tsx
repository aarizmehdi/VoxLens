/**
 * TranscriptPanel Component
 *
 * Scrollable transcript with clickable timestamps and search.
 */

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Search, Copy, Check } from "lucide-react";
import { useTranscript } from "@/hooks/use-meeting";
import { formatTimestamp } from "@/lib/utils";
import styles from "./TranscriptPanel.module.css";

interface TranscriptPanelProps {
  meetingId: string;
}

export function TranscriptPanel({ meetingId }: TranscriptPanelProps) {
  const { data: transcript, isLoading } = useTranscript(meetingId);
  const [search, setSearch] = useState("");
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const filteredChunks = useMemo(() => {
    if (!transcript?.chunks) return [];
    if (!search.trim()) return transcript.chunks;
    const q = search.toLowerCase();
    return transcript.chunks.filter((c) => c.text.toLowerCase().includes(q));
  }, [transcript?.chunks, search]);

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  if (isLoading) {
    return (
      <div className={styles.loading}>
        {[...Array(6)].map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 48, width: "100%" }} />
        ))}
      </div>
    );
  }

  if (!transcript?.chunks?.length) {
    return (
      <div className={styles.empty}>
        <p>Transcript not available yet.</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Search bar */}
      <div className={styles.searchBar}>
        <Search size={16} className={styles.searchIcon} />
        <input
          className={styles.searchInput}
          placeholder="Search transcript..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          id="transcript-search"
        />
        <span className={styles.count}>
          {filteredChunks.length} segment{filteredChunks.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Transcript segments */}
      <div className={styles.segments}>
        {filteredChunks.map((chunk, i) => (
          <motion.div
            key={chunk.id}
            className={styles.segment}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: Math.min(i * 0.02, 0.3) }}
          >
            <span className={styles.timestamp}>
              {formatTimestamp(chunk.start_time)}
            </span>
            <p className={styles.text}>{chunk.text}</p>
            <button
              className={styles.copyBtn}
              onClick={() => handleCopy(chunk.text, i)}
              title="Copy text"
            >
              {copiedIdx === i ? <Check size={14} /> : <Copy size={14} />}
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
