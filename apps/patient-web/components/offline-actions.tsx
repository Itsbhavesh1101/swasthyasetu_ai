"use client";

import Link from "next/link";

export function OfflineActions() {
  return (
    <div className="inline-actions">
      <button
        className="button button--primary"
        onClick={() => window.location.reload()}
        type="button"
      >
        Try again
      </button>
      <Link className="action-link action-link--secondary" href="/">
        Return home
      </Link>
    </div>
  );
}
