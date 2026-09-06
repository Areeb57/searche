'use client';

import { Zap } from 'lucide-react';
import styles from './EmptyState.module.css';

const SUGGESTIONS = [
  { label: 'Research a topic', prompt: 'Research the history and impact of the internet on global communication' },
  { label: 'Compare options', prompt: 'Compare the pros and cons of React, Vue, and Angular for a new web project' },
  { label: 'Explain a concept', prompt: 'Explain how machine learning works in simple terms with practical examples' },
  { label: 'Summarize content', prompt: 'Summarize the key principles of effective software architecture' },
];

export default function EmptyState({ onSuggestion }) {
  return (
    <div className={styles.container}>
      <div className={styles.icon}>
        <Zap size={32} strokeWidth={2} />
      </div>
      <h2 className={styles.heading}>How can I help you?</h2>
      <p className={styles.subheading}>
        Search the web, research topics, compare information,<br className={styles.br} />
        and get organized, accurate answers.
      </p>

      <div className={styles.suggestions}>
        {SUGGESTIONS.map((s) => (
          <button
            key={s.label}
            className={styles.suggestion}
            onClick={() => onSuggestion(s.prompt)}
          >
            <span className={styles.suggLabel}>{s.label}</span>
            <span className={styles.suggPrompt}>{s.prompt}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
