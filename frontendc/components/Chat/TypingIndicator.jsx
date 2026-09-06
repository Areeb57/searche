export default function TypingIndicator() {
    return (
        <div className="typing-container">
            <div className="message-avatar ai-avatar">
                AI
            </div>

            <div className="typing-content">
                <span>Thinking</span>

                <div className="typing-dots">
                    <span />
                    <span />
                    <span />
                </div>
            </div>
        </div>
    );
}