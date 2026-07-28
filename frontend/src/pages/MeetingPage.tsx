/**
 * MeetingPage Component
 *
 * Routes to either the processing status view or the final meeting view.
 */

import { useStore } from "@/lib/store";
import { useMeeting } from "@/hooks/use-meeting";
import { ProcessingStatus } from "@/components/intake/ProcessingStatus";
import { MeetingView } from "@/components/meeting/MeetingView";
import styles from "./MeetingPage.module.css";
import { Loader2 } from "lucide-react";

export function MeetingPage() {
  const activeMeetingId = useStore((s) => s.activeMeetingId);
  const { data: meeting, isLoading } = useMeeting(activeMeetingId);

  if (!activeMeetingId) {
    return null;
  }

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <Loader2 size={32} className={styles.spinner} />
        <p>Loading meeting data...</p>
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className={styles.errorContainer}>
        <p>Meeting not found.</p>
        <button
          className="btn btn-primary"
          onClick={() => useStore.getState().setActiveMeetingId(null)}
        >
          Go Back
        </button>
      </div>
    );
  }

  const isProcessing = ["pending", "downloading", "processing_audio", "transcribing", "summarizing", "embedding"].includes(meeting.status);
  const isFailed = meeting.status === "failed";

  if (isProcessing || isFailed) {
    return (
      <div className={styles.processingContainer}>
        <ProcessingStatus meetingId={activeMeetingId} />
      </div>
    );
  }

  return <MeetingView meetingId={activeMeetingId} />;
}
