"use client";

import { useEffect, useRef } from "react";
import { ArrowUp, Mic, Paperclip, Square } from "lucide-react";

export default function MessageInput({
    value,
    onChange,
    onSend,
    onStop,
    isLoading,
    enterToSend,
}) {
    const textareaRef = useRef(null);

    /*
     * Automatically grow the textarea as the user types.
     */
    useEffect(() => {
        const textarea = textareaRef.current;

        if (!textarea) return;

        textarea.style.height = "auto";

        const newHeight = Math.min(
            textarea.scrollHeight,
            180
        );

        textarea.style.height = `${newHeight}px`;
    }, [value]);

    function handleKeyDown(event) {
        if (event.key !== "Enter") return;

        /*
         * Shift + Enter = new line
         */
        if (event.shiftKey) return;

        /*
         * If Enter-to-send is enabled,
         * Enter sends the message.
         */
        if (enterToSend) {
            event.preventDefault();

            if (value.trim() && !isLoading) {
                onSend();
            }
        }
    }

    return (
        <div className="input-container">
            <div className="message-input">
                <button
                    className="input-icon"
                    type="button"
                    aria-label="Attach file"
                    title="Attach file"
                    disabled={isLoading}
                >
                    <Paperclip size={18} />
                </button>

                <textarea
                    ref={textareaRef}
                    value={value}
                    onChange={(event) => onChange(event.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything..."
                    rows={1}
                    aria-label="Message"
                    disabled={isLoading}
                />

                <button
                    className="input-icon"
                    type="button"
                    aria-label="Voice input"
                    title="Voice input"
                    disabled={isLoading}
                >
                    <Mic size={18} />
                </button>

                {isLoading ? (
                    <button
                        className="send-button stop-button"
                        type="button"
                        onClick={onStop}
                        aria-label="Stop response"
                        title="Stop response"
                    >
                        <Square size={15} fill="currentColor" />
                    </button>
                ) : (
                    <button
                        className="send-button"
                        type="button"
                        onClick={onSend}
                        disabled={!value.trim()}
                        aria-label="Send message"
                        title="Send message"
                    >
                        <ArrowUp size={18} />
                    </button>
                )}
            </div>

            <div className="input-disclaimer">
                AI Search Assistant can make mistakes. Check important
                information.
            </div>
        </div>
    );
}