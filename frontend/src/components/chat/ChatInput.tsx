/**
 * ChatInput Component
 */
import { useState, type FormEvent } from "react";
import { Send } from "lucide-react";
import styles from "./ChatInput.module.css";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value.trim());
    setValue("");
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <input
        className={styles.input}
        placeholder="Ask about this meeting..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={disabled}
        id="chat-input"
      />
      <button type="submit" className={styles.sendBtn} disabled={disabled || !value.trim()} id="chat-send-btn">
        <Send size={16} />
      </button>
    </form>
  );
}
