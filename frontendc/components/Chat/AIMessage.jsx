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
            <div className="message-content">

                {message.searchStep && (
                    <SearchProgress currentStep={message.searchStep} />
                )}

                <div className="message-text ai-text">
                    {message.content}
                </div>

                {message.sources && message.sources.length > 0 && (
                    <SearchResults sources={message.sources} />
                )}

                <MessageActions
                    message={message.content}
                    onRegenerate={onRegenerate}
                />

            </div>
        </div>
    );
}