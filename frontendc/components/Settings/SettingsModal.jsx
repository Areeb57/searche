"use client";

import { X } from "lucide-react";
import SettingsSection from "./SettingsSection";
import Toggle from "./Toggle";

export default function SettingsModal({
    open,
    onClose,
    theme,
    onThemeChange,
    enterToSend,
    onEnterToSendChange,
    streaming,
    onStreamingChange,
}) {
    if (!open) {
        return null;
    }

    return (
        <div
            className="settings-overlay"
            onClick={onClose}
        >
            <div
                className="settings-modal"
                onClick={(event) =>
                    event.stopPropagation()
                }
            >
                <div className="settings-header">
                    <div>
                        <h2>Settings</h2>
                        <p>
                            Customize your AI Search experience.
                        </p>
                    </div>

                    <button
                        type="button"
                        className="icon-button"
                        onClick={onClose}
                        aria-label="Close settings"
                    >
                        <X size={19} />
                    </button>
                </div>

                <div className="settings-body">
                    <SettingsSection
                        title="Appearance"
                        description="Choose how the application looks."
                    >
                        <div className="theme-options">
                            <button
                                type="button"
                                className={`theme-option ${theme === "light"
                                        ? "selected"
                                        : ""
                                    }`}
                                onClick={() =>
                                    onThemeChange("light")
                                }
                            >
                                <span className="theme-preview light-preview" />
                                <span>Light</span>
                            </button>

                            <button
                                type="button"
                                className={`theme-option ${theme === "dark"
                                        ? "selected"
                                        : ""
                                    }`}
                                onClick={() =>
                                    onThemeChange("dark")
                                }
                            >
                                <span className="theme-preview dark-preview" />
                                <span>Dark</span>
                            </button>

                            <button
                                type="button"
                                className={`theme-option ${theme === "system"
                                        ? "selected"
                                        : ""
                                    }`}
                                onClick={() =>
                                    onThemeChange("system")
                                }
                            >
                                <span className="theme-preview system-preview">
                                    <span />
                                </span>
                                <span>System</span>
                            </button>
                        </div>
                    </SettingsSection>

                    <SettingsSection
                        title="Chat"
                        description="Control how messages are sent and displayed."
                    >
                        <div className="settings-options">
                            <Toggle
                                label="Enter to send"
                                checked={enterToSend}
                                onChange={
                                    onEnterToSendChange
                                }
                            />

                            <Toggle
                                label="Streaming responses"
                                checked={streaming}
                                onChange={
                                    onStreamingChange
                                }
                            />
                        </div>
                    </SettingsSection>

                    <SettingsSection
                        title="About"
                        description="AI Search Assistant frontend prototype."
                    >
                        <div className="about-settings">
                            <div>
                                <strong>AI Search Assistant</strong>
                                <span>Frontend Prototype</span>
                            </div>

                            <span>Version 1.0</span>
                        </div>
                    </SettingsSection>
                </div>
            </div>
        </div>
    );
}