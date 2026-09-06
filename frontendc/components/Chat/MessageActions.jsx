"use client";

import {
    Copy,
    RotateCcw,
    ThumbsUp,
    ThumbsDown,
    MoreHorizontal,
} from "lucide-react";

export default function MessageActions({
    message,
    onRegenerate,
}) {
    async function handleCopy() {
        try {
            await navigator.clipboard.writeText(message);
        } catch (error) {
            console.error("Could not copy message:", error);
        }
    }

    return (
        <div className="message-actions">
            <button
                onClick={handleCopy}
                aria-label="Copy response"
                title="Copy"
            >
                <Copy size={15} />
            </button>

            <button
                onClick={onRegenerate}
                aria-label="Regenerate response"
                title="Regenerate"
            >
                <RotateCcw size={15} />
            </button>

            <button
                aria-label="Like response"
                title="Like"
            >
                <ThumbsUp size={15} />
            </button>

            <button
                aria-label="Dislike response"
                title="Dislike"
            >
                <ThumbsDown size={15} />
            </button>

            <button
                aria-label="More response options"
                title="More"
            >
                <MoreHorizontal size={15} />
            </button>
        </div>
    );
}