"use client";

import { ExternalLink } from "lucide-react";

export default function SourceCard({ source }) {
    return (
        <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-card"
        >
            <div className="source-card-top">
                <div className="source-favicon">
                    {source.name.charAt(0)}
                </div>

                <div className="source-info">
                    <div className="source-name">
                        {source.name}
                    </div>

                    <div className="source-domain">
                        {source.domain}
                    </div>
                </div>

                <ExternalLink
                    size={16}
                    className="source-external-icon"
                />
            </div>

            <div className="source-title">
                {source.title}
            </div>

            <div className="source-description">
                {source.description}
            </div>
        </a>
    );
}