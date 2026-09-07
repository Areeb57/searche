"use client";

export default function Toggle({
    checked,
    onChange,
    label,
}) {
    return (
        <label className="settings-toggle-row">
            <span>{label}</span>

            <button
                type="button"
                className={`toggle ${checked ? "toggle-active" : ""
                    }`}
                onClick={() => onChange(!checked)}
                aria-pressed={checked}
                aria-label={label}
            >
                <span className="toggle-thumb" />
            </button>
        </label>
    );
}