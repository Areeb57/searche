"use client";

import { Check, Circle, ChevronDown } from "lucide-react";
import { useState } from "react";

const steps = [
    "Searching multiple sources",
    "Reading relevant pages",
    "Comparing information",
    "Generating answer",
];

export default function SearchProgress({ currentStep = 3 }) {
    const [expanded, setExpanded] = useState(true);

    return (
        <div className="search-progress">
            <button
                className="search-progress-header"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="search-progress-title">
                    <span className="search-status-dot" />
                    <span>Researching your question...</span>
                </div>

                <ChevronDown
                    size={17}
                    className={`search-chevron ${expanded ? "expanded" : ""
                        }`}
                />
            </button>

            {expanded && (
                <div className="search-progress-steps">
                    {steps.map((step, index) => {
                        const stepNumber = index + 1;

                        const completed = stepNumber < currentStep;
                        const active = stepNumber === currentStep;

                        return (
                            <div
                                className={`search-step ${active ? "active" : ""
                                    }`}
                                key={step}
                            >
                                <div className="search-step-icon">
                                    {completed ? (
                                        <Check size={14} />
                                    ) : active ? (
                                        <span className="search-loading-dot" />
                                    ) : (
                                        <Circle size={10} />
                                    )}
                                </div>

                                <span>{step}</span>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}