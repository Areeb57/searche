'use client';

import { ExternalLink } from 'lucide-react';
import styles from './SourceCard.module.css';

export default function SourceCard({ source }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className={styles.card}
      aria-label={`Open ${source.name} in new tab`}
    >
      <div className={styles.favicon}>
        <img
          src={`https://www.google.com/s2/favicons?domain=${source.domain}&sz=32`}
          alt=""
          width={16}
          height={16}
          onError={e => { e.target.style.display = 'none'; }}
        />
      </div>
      <div className={styles.content}>
        <p className={styles.name}>{source.name}</p>
        <p className={styles.domain}>{source.domain}</p>
        <p className={styles.title}>{source.title}</p>
        <p className={styles.description}>{source.description}</p>
      </div>
      <div className={styles.openIcon}>
        <ExternalLink size={13} />
      </div>
    </a>
  );
}
