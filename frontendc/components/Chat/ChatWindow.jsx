"use client";

import { useEffect, useRef } from "react";

import Message from "./Message";
import TypingIndicator from "./TypingIndicator";

export default function ChatWindow({
    messages,
    isLoading,
    onRegenerate,
    onSuggestion,
}) {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages, isLoading]);

    if (messages.length === 0) {
        return (
            <div className="chat-area">
                <div className="welcome">
                    <div className="welcome-icon">
                        AI
                    </div>

                    <h1>
                        How can I help you?
                    </h1>

                    <p>
                        Search the web, research topics,
                        compare information, and get
                        organized answers.
                    </p>

                    <div className="suggestions">
                        <button
                            className="suggestion-card"
                            onClick={() =>
                                onSuggestion(
                                    "Research a topic and summarize the most useful information"
                                )
                            }
                        >
                            <strong>Research a topic</strong>
                            <span>Find and summarize information</span>
                        </button>

                        <button
                            className="suggestion-card"
                            onClick={() =>
                                onSuggestion(
                                    "Compare the best options and explain the differences"
                                )
                            }
                        >
                            <strong>Compare products</strong>
                            <span>Compare multiple options</span>
                        </button>

                        <button
                            className="suggestion-card"
                            onClick={() =>
                                onSuggestion(
                                    "Find useful information about this topic"
                                )
                            }
                        >
                            <strong>Find information</strong>
                            <span>Search for useful sources</span>
                        </button>

                        <button
                            className="suggestion-card"
                            onClick={() =>
                                onSuggestion(
                                    "Summarize the most important information about this topic"
                                )
                            }
                        >
                            <strong>Summarize something</strong>
                            <span>Turn information into a summary</span>
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="chat-area">
            <div className="messages-container">
                {messages.map((message) => (
                    <Message
                        key={message.id}
                        message={message}
                        onRegenerate={() =>
                            onRegenerate(message.id)
                        }
                    />
                ))}

                {isLoading && <TypingIndicator />}

                <div ref={bottomRef} />
            </div>
        </div>
    );
}