export default function SettingsSection({
    title,
    description,
    children,
}) {
    return (
        <section className="settings-section">
            <div className="settings-section-heading">
                <h3>{title}</h3>

                {description && (
                    <p>{description}</p>
                )}
            </div>

            <div className="settings-section-content">
                {children}
            </div>
        </section>
    );
}