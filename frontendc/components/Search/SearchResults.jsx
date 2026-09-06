"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

import SourceCard from "./SourceCard";

export default function SearchResults({
    sources = [],
}) {
    const [expanded, setExpanded] = useState(true);

    if (sources.length === 0) {
        return null;
    }

    return (
        <div className="search-results">
            <button
                className="search-results-header"
                onClick={() => setExpanded(!expanded)}
            >
                <div>
                    <strong>Sources</strong>
                    <span>
                        {sources.length} sources found
                    </span>
                </div>

                <ChevronDown
                    size={17}
                    className={`search-chevron ${expanded ? "expanded" : ""
                        }`}
                />
            </button>

            {expanded && (
                <div className="source-list">
                    {sources.map((source) => (
                        <SourceCard
                            key={source.id}
                            source={source}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}