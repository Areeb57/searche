"use client";

import MessageActions from "./MessageActions";
import SearchProgress from "../Search/SearchProgress";
import SearchResults from "../Search/SearchResults";

export default function AIMessage({
    message,
    onRegenerate,
}) {
    return (
        <div className="message ai-message">
            <div className="message-avatar ai-avatar">
                AI
            </div>

            <div className="message-content">
                <div className="message-role">
                    AI Search
                </div>

                {message.searchStep && (
                    <SearchProgress
                        currentStep={message.searchStep || 4}
                    />
                )}

                <div className="message-text ai-text">
                    {message.content}
                </div>

                {message.sources && (
                    <SearchResults
                        sources={message.sources}
                    />
                )}

                <MessageActions
                    message={message.content}
                    onRegenerate={onRegenerate}
                />
            </div>
        </div>
    );
}