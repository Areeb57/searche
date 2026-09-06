'use client';

import { useState } from 'react';
import { Copy, RefreshCw, ThumbsUp, ThumbsDown, Check } from 'lucide-react';
import styles from './MessageActions.module.css';

export default function MessageActions({ content, onRegenerate }) {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState(null); // null | 'up' | 'down'

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(content);
    } catch {
      const el = document.createElement('textarea');
      el.value = content;
      el.style.position = 'fixed';
      el.style.opacity = '0';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className={styles.actions}>
      <button
        className={`${styles.btn} ${copied ? styles.btnSuccess : ''}`}
        onClick={handleCopy}
        aria-label={copied ? 'Copied!' : 'Copy message'}
        title={copied ? 'Copied!' : 'Copy'}
      >
        {copied ? <Check size={13} /> : <Copy size={13} />}
      </button>

      <button
        className={styles.btn}
        onClick={onRegenerate}
        aria-label="Regenerate response"
        title="Regenerate"
      >
        <RefreshCw size={13} />
      </button>

      <div className={styles.divider} />

      <button
        className={`${styles.btn} ${liked === 'up' ? styles.btnActive : ''}`}
        onClick={() => setLiked(v => (v === 'up' ? null : 'up'))}
        aria-label="Good response"
        aria-pressed={liked === 'up'}
        title="Good response"
      >
        <ThumbsUp size={13} />
      </button>

      <button
        className={`${styles.btn} ${liked === 'down' ? styles.btnActive : ''}`}
        onClick={() => setLiked(v => (v === 'down' ? null : 'down'))}
        aria-label="Bad response"
        aria-pressed={liked === 'down'}
        title="Bad response"
      >
        <ThumbsDown size={13} />
      </button>
    </div>
  );
}
