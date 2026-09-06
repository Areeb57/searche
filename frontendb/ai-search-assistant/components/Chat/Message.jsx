'use client';

import { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { renderMarkdown } from '@/lib/markdown';
import MessageActions from './MessageActions';
import SearchProgress from '@/components/Search/SearchProgress';
import SearchResults from '@/components/Search/SearchResults';
import styles from './Message.module.css';

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/* ─── User Message ─────────────────────────────────────────── */
export function UserMessage({ message }) {
  const { state } = useApp();
  return (
    <div className={styles.userMessage}>
      <div className={styles.userBubble}>
        <p className={styles.userText}>{message.content}</p>
      </div>
      {state.settings.showTimestamps && message.timestamp && (
        <time className={styles.timestamp}>{formatTime(message.timestamp)}</time>
      )}
    </div>
  );
}

/* ─── AI Message ───────────────────────────────────────────── */
export function AIMessage({ message, isStreaming, onRegenerate }) {
  const { state } = useApp();
  const [hovered, setHovered] = useState(false);
  const html = renderMarkdown(message.content || '');

  return (
    <div
      className={styles.aiMessage}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className={styles.aiAvatar} aria-hidden="true">M</div>

      <div className={styles.aiContent}>
        {message.searchProgress && (
          <SearchProgress
            steps={message.searchProgress.steps}
            isActive={isStreaming}
          />
        )}

        <div
          className={styles.aiText}
          dangerouslySetInnerHTML={{ __html: html }}
        />

        {isStreaming && <span className={styles.cursor} aria-hidden="true" />}

        {!isStreaming && message.sources && message.sources.length > 0 && (
          <SearchResults sources={message.sources} />
        )}

        {!isStreaming && (
          <div
            className={styles.actionsWrap}
            style={{ opacity: hovered ? 1 : 0 }}
          >
            <MessageActions content={message.content} onRegenerate={onRegenerate} />
          </div>
        )}

        {state.settings.showTimestamps && message.timestamp && (
          <time className={styles.timestamp}>{formatTime(message.timestamp)}</time>
        )}
      </div>
    </div>
  );
}
