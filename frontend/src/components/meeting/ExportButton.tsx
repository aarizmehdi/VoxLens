/**
 * ExportButton Component
 */
import { useState } from "react";
import { Download, Check, Loader2 } from "lucide-react";
import { exportMeeting } from "@/lib/api";

interface ExportButtonProps { meetingId: string; }

export function ExportButton({ meetingId }: ExportButtonProps) {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const result = await exportMeeting(meetingId);
      // Create downloadable file
      const blob = new Blob([result.markdown], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename;
      a.click();
      URL.revokeObjectURL(url);
      setDone(true);
      setTimeout(() => setDone(false), 2000);
    } catch (e) {
      console.error("Export failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button className="btn btn-secondary" onClick={handleExport} disabled={loading} id="export-btn">
      {loading ? <Loader2 size={16} className="spinner" /> : done ? <Check size={16} /> : <Download size={16} />}
      {done ? "Downloaded!" : "Export"}
    </button>
  );
}
