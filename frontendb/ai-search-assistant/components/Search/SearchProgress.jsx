'use client';

import { useState } from 'react';
import { ChevronDown, Check, Loader } from 'lucide-react';
import styles from './SearchProgress.module.css';

export default function SearchProgress({ steps, isActive }) {
  const [expanded, setExpanded] = useState(false);
  const doneCount = steps.filter(s => s.done).length;
  const allDone = doneCount === steps.length;

  return (
    <div className={`${styles.container} ${allDone ? styles.done : ''}`}>
      <button
        className={styles.toggle}
        onClick={() => setExpanded(v => !v)}
        aria-expanded={expanded}
      >
        <div className={styles.toggleLeft}>
          {!allDone ? (
            <Loader size={14} className={styles.spinIcon} />
          ) : (
            <Check size={14} className={styles.doneIcon} />
          )}
          <span className={styles.toggleLabel}>
            {allDone
              ? `Searched ${steps.length} sources`
              : `Searching… (${doneCount}/${steps.length})`}
          </span>
        </div>
        <ChevronDown
          size={14}
          className={`${styles.chevron} ${expanded ? styles.chevronOpen : ''}`}
        />
      </button>

      {expanded && (
        <div className={styles.steps}>
          {steps.map((step, i) => (
            <div key={i} className={`${styles.step} ${step.done ? styles.stepDone : styles.stepPending}`}>
              <div className={styles.stepIcon}>
                {step.done ? (
                  <Check size={11} />
                ) : (
                  <div className={styles.stepDot} />
                )}
              </div>
              <span className={styles.stepLabel}>{step.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
