export default function UserMessage({ message }) {
    return (
        <div className="message user-message">
            <div className="message-content">
                <div className="message-text">
                    {message.content}
                </div>
            </div>
        </div>
    );
}