'use client';

import { useEffect, useRef } from 'react';
import { X, Sun, Moon, Monitor } from 'lucide-react';
import { useApp } from '@/contexts/AppContext';
import styles from './SettingsModal.module.css';

export default function SettingsModal({ onClose }) {
  const { state, updateSettings } = useApp();
  const { settings } = state;
  const modalRef = useRef(null);

  // Close on Escape
  useEffect(() => {
    function handleKey(e) {
      if (e.key === 'Escape') onClose();
    }
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  // Focus trap
  useEffect(() => {
    modalRef.current?.focus();
  }, []);

  function set(key, value) {
    updateSettings({ [key]: value });
  }

  return (
    <div className={styles.overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div
        className={styles.modal}
        role="dialog"
        aria-modal="true"
        aria-label="Settings"
        tabIndex={-1}
        ref={modalRef}
      >
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.title}>Settings</h2>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close settings">
            <X size={18} />
          </button>
        </div>

        <div className={styles.body}>
          {/* Appearance */}
          <Section title="Appearance">
            <div className={styles.themeRow}>
              {[
                { value: 'light', icon: <Sun size={16} />, label: 'Light' },
                { value: 'dark', icon: <Moon size={16} />, label: 'Dark' },
                { value: 'system', icon: <Monitor size={16} />, label: 'System' },
              ].map(opt => (
                <button
                  key={opt.value}
                  className={`${styles.themeBtn} ${settings.theme === opt.value ? styles.themeBtnActive : ''}`}
                  onClick={() => set('theme', opt.value)}
                  aria-pressed={settings.theme === opt.value}
                >
                  {opt.icon}
                  <span>{opt.label}</span>
                </button>
              ))}
            </div>
          </Section>

          {/* Chat */}
          <Section title="Chat">
            <Toggle
              label="Enter to send"
              description="Press Enter to send a message (Shift+Enter for new line)"
              checked={settings.enterToSend}
              onChange={v => set('enterToSend', v)}
            />
            <Toggle
              label="Show timestamps"
              description="Display the time next to each message"
              checked={settings.showTimestamps}
              onChange={v => set('showTimestamps', v)}
            />
            <Toggle
              label="Auto-scroll"
              description="Automatically scroll to the latest message"
              checked={settings.autoScroll}
              onChange={v => set('autoScroll', v)}
            />
          </Section>

          {/* Interface */}
          <Section title="Interface">
            <Toggle
              label="Compact mode"
              description="Reduce spacing between messages for more content on screen"
              checked={settings.compactMode}
              onChange={v => set('compactMode', v)}
            />
          </Section>
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className={styles.section}>
      <h3 className={styles.sectionTitle}>{title}</h3>
      <div className={styles.sectionContent}>{children}</div>
    </div>
  );
}

function Toggle({ label, description, checked, onChange }) {
  return (
    <label className={styles.toggleRow}>
      <div className={styles.toggleInfo}>
        <span className={styles.toggleLabel}>{label}</span>
        {description && <span className={styles.toggleDesc}>{description}</span>}
      </div>
      <div
        className={`${styles.toggle} ${checked ? styles.toggleOn : ''}`}
        onClick={() => onChange(!checked)}
        role="switch"
        aria-checked={checked}
        tabIndex={0}
        onKeyDown={e => (e.key === ' ' || e.key === 'Enter') && onChange(!checked)}
      >
        <div className={styles.toggleThumb} />
      </div>
    </label>
  );
}
