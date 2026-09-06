'use client';

import { useEffect, useRef } from 'react';
import { useApp } from '@/contexts/AppContext';
import { UserMessage, AIMessage } from './Message';
import TypingIndicator from './TypingIndicator';
import EmptyState from './EmptyState';
import styles from './ChatWindow.module.css';

export default function ChatWindow({ onSuggestion, onRegenerate, streamingMessageId }) {
  const { currentChat, state } = useApp();
  const bottomRef = useRef(null);
  const containerRef = useRef(null);

  const messages = currentChat?.messages || [];
  const isEmpty = messages.length === 0 && !state.isLoading;

  // Auto-scroll to bottom
  useEffect(() => {
    if (!state.settings.autoScroll) return;
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length, state.isLoading, state.settings.autoScroll]);

  // Also scroll during streaming
  useEffect(() => {
    if (!streamingMessageId || !state.settings.autoScroll) return;
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [streamingMessageId, state.settings.autoScroll]);

  return (
    <div
      className={`${styles.container} ${state.settings.compactMode ? styles.compact : ''}`}
      ref={containerRef}
    >
      {isEmpty ? (
        <div className={styles.emptyWrap}>
          <EmptyState onSuggestion={onSuggestion} />
        </div>
      ) : (
        <div className={styles.messages}>
          {messages.map(msg =>
            msg.role === 'user' ? (
              <UserMessage key={msg.id} message={msg} />
            ) : (
              <AIMessage
                key={msg.id}
                message={msg}
                isStreaming={msg.id === streamingMessageId}
                onRegenerate={() => onRegenerate(msg)}
              />
            )
          )}
          {state.isLoading && <TypingIndicator />}
          <div ref={bottomRef} className={styles.anchor} />
        </div>
      )}
    </div>
  );
}
