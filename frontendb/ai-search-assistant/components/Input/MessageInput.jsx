'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Square, Paperclip, Mic } from 'lucide-react';
import { useApp } from '@/contexts/AppContext';
import styles from './MessageInput.module.css';

export default function MessageInput({ onSend }) {
  const { state } = useApp();
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    const next = Math.min(ta.scrollHeight, 180);
    ta.style.height = next + 'px';
  }, [value]);

  const submit = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || state.isLoading) return;
    onSend(trimmed);
    setValue('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  }, [value, state.isLoading, onSend]);

  function handleKeyDown(e) {
    if (e.key === 'Enter') {
      if (state.settings.enterToSend && !e.shiftKey) {
        e.preventDefault();
        submit();
      }
      // If not enterToSend, plain Enter = newline (default textarea behaviour)
    }
  }

  const ready = value.trim().length > 0 && !state.isLoading;
  const isLoading = state.isLoading;

  return (
    <div className={styles.wrapper}>
      <div className={styles.container}>
        <div className={styles.inputBox}>
          <button
            className={styles.iconBtn}
            aria-label="Attach file"
            title="Attach file"
            disabled={isLoading}
            type="button"
          >
            <Paperclip size={16} />
          </button>

          <textarea
            ref={textareaRef}
            className={styles.textarea}
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything…"
            rows={1}
            disabled={isLoading}
            aria-label="Chat message input"
            aria-multiline="true"
          />

          <button
            className={styles.iconBtn}
            aria-label="Voice input"
            title="Voice input"
            disabled={isLoading}
            type="button"
          >
            <Mic size={16} />
          </button>

          <button
            type="button"
            className={`${styles.sendBtn} ${isLoading ? styles.sendBtnStop : ready ? styles.sendBtnReady : ''}`}
            onClick={isLoading ? undefined : submit}
            disabled={!ready && !isLoading}
            aria-label={isLoading ? 'Stop generating' : 'Send message'}
            title={isLoading ? 'Stop' : 'Send'}
          >
            {isLoading ? <Square size={14} fill="currentColor" /> : <Send size={14} />}
          </button>
        </div>

        <p className={styles.hint}>
          {state.settings.enterToSend
            ? 'Enter to send · Shift + Enter for new line'
            : 'Ctrl + Enter to send · Enter for new line'}
        </p>
      </div>
    </div>
  );
}
