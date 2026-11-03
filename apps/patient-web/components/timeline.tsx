"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { TimelineItem, TimelineState } from "../lib/timeline/contracts";
import { ErrorState, LoadingState, Panel } from "./ui-primitives";

async function timelinePage(next?: string) {
  const response = await fetch(
    `/api/patient/timeline${next ? `?cursor=${encodeURIComponent(next)}` : ""}`,
    { cache: "no-store" },
  );
  return { response, body: (await response.json()) as TimelineState };
}

export function Timeline() {
  const [items, setItems] = useState<TimelineItem[]>();
  const [cursor, setCursor] = useState<string>();
  const [anonymous, setAnonymous] = useState(false);
  const [failed, setFailed] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);

  async function load(next?: string) {
    const { response, body } = await timelinePage(next);
    if (response.status === 401 || body.state === "ANONYMOUS") return setAnonymous(true);
    if (!response.ok || body.state !== "AUTHENTICATED") return setFailed(true);
    setItems((current) => (next ? [...(current ?? []), ...body.items] : [...body.items]));
    setCursor(body.nextCursor);
  }

  useEffect(() => {
    let active = true;
    void timelinePage().then(({ response, body }) => {
      if (!active) return;
      if (response.status === 401 || body.state === "ANONYMOUS") setAnonymous(true);
      else if (!response.ok || body.state !== "AUTHENTICATED") setFailed(true);
      else {
        setItems([...body.items]);
        setCursor(body.nextCursor);
      }
    });
    return () => {
      active = false;
    };
  }, []);

  if (anonymous)
    return (
      <Panel>
        <h2>Sign in to view your timeline</h2>
        <Link className="action-link action-link--primary" href="/login">
          Sign in <span aria-hidden="true">→</span>
        </Link>
      </Panel>
    );
  if (failed) return <ErrorState onRetry={() => window.location.reload()} />;
  if (!items) return <LoadingState label="Building your medical timeline." />;
  return (
    <section aria-labelledby="timeline-title" className="panel">
      <h2 id="timeline-title">Timeline entries</h2>
      {items.length === 0 ? (
        <p>Your timeline will grow as you add history and complete health journeys.</p>
      ) : (
        <ol className="history-list timeline-list">
          {items.map((entry) => (
            <li className="history-item" key={entry.entryId}>
              <div>
                <p className="card-kicker">{entry.category}</p>
                <h3>{entry.label}</h3>
                <p>{entry.detail.toLowerCase()}</p>
                <time dateTime={entry.occurredAt}>
                  {new Date(entry.occurredAt).toLocaleString()}
                </time>
              </div>
            </li>
          ))}
        </ol>
      )}
      {cursor ? (
        <button
          className="button button--secondary"
          disabled={loadingMore}
          onClick={async () => {
            setLoadingMore(true);
            await load(cursor);
            setLoadingMore(false);
          }}
          type="button"
        >
          {loadingMore ? "Loading…" : "Load earlier entries"}
        </button>
      ) : null}
    </section>
  );
}
