export default function UserMessage({ message }) {
    return (
        <div className="message user-message">
            <div className="message-avatar user-avatar">
                U
            </div>

            <div className="message-content">
                <div className="message-role">
                    You
                </div>

                <div className="message-text">
                    {message.content}
                </div>
            </div>
        </div>
    );
}