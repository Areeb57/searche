'use client';

import { useState } from 'react';
import { ChevronDown, Globe } from 'lucide-react';
import SourceCard from './SourceCard';
import styles from './SearchResults.module.css';

export default function SearchResults({ sources }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  const visible = expanded ? sources : sources.slice(0, 2);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <Globe size={14} className={styles.headerIcon} />
        <span className={styles.headerLabel}>
          {sources.length} source{sources.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className={styles.cards}>
        {visible.map(src => (
          <SourceCard key={src.id} source={src} />
        ))}
      </div>

      {sources.length > 2 && (
        <button
          className={styles.showMore}
          onClick={() => setExpanded(v => !v)}
        >
          <ChevronDown
            size={14}
            style={{ transform: expanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
          />
          {expanded ? 'Show fewer' : `Show ${sources.length - 2} more`}
        </button>
      )}
    </div>
  );
}
