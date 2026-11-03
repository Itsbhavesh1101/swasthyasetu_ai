"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { HistoryItem, HistoryState } from "../lib/history/contracts";
import { ErrorState, LoadingState, Panel } from "./ui-primitives";
import { HistoryForm } from "./history-form";

export function HistoryList() {
  const [items, setItems] = useState<HistoryItem[]>();
  const [anonymous, setAnonymous] = useState(false);
  const [failed, setFailed] = useState(false);
  const [correction, setCorrection] = useState<HistoryItem>();
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    let active = true;
    void fetch("/api/patient/history", { cache: "no-store" })
      .then(async (result) => ({ result, data: (await result.json()) as HistoryState }))
      .then(({ result, data }) => {
        if (!active) return;
        if (result.status === 401 || data.state === "ANONYMOUS") setAnonymous(true);
        else if (!result.ok || data.state !== "AUTHENTICATED") setFailed(true);
        else setItems(data.items);
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [revision]);

  if (anonymous)
    return (
      <Panel>
        <h2>Sign in to view your medical history</h2>
        <p>Your entries are protected by your patient account.</p>
        <Link className="action-link action-link--primary" href="/login">
          Sign in <span aria-hidden="true">→</span>
        </Link>
      </Panel>
    );
  if (failed)
    return (
      <ErrorState
        onRetry={() => {
          setFailed(false);
          setRevision((value) => value + 1);
        }}
      />
    );
  if (!items) return <LoadingState label="Loading your medical history." />;

  return (
    <div className="page-stack">
      <section aria-labelledby="history-list-title" className="panel">
        <p className="card-kicker">Longitudinal record</p>
        <h2 id="history-list-title">Your entries</h2>
        {items.length === 0 ? (
          <p>No history entries yet. Use the form below to add your first one.</p>
        ) : (
          <ul className="history-list">
            {items.map((item) => (
              <li
                className={
                  item.verificationState === "SUPERSEDED"
                    ? "history-item history-item--previous"
                    : "history-item"
                }
                key={item.factId}
              >
                <div>
                  <p className="card-kicker">{item.factType.replaceAll("_", " ")}</p>
                  <h3>{item.label}</h3>
                  <p>
                    {item.status ? `Status: ${item.status.toLowerCase()}. ` : ""}
                    {item.verificationState === "SUPERSEDED"
                      ? "Previous version retained for history."
                      : "Patient confirmed."}
                  </p>
                </div>
                {item.verificationState !== "SUPERSEDED" ? (
                  <button
                    className="button button--secondary"
                    onClick={() => setCorrection(item)}
                    type="button"
                  >
                    Correct entry
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
      {correction ? (
        <HistoryForm
          correction={correction}
          key={correction.factId}
          onCancel={() => setCorrection(undefined)}
          onSaved={() => {
            setCorrection(undefined);
            setRevision((value) => value + 1);
          }}
        />
      ) : (
        <HistoryForm key="new-history-entry" onSaved={() => setRevision((value) => value + 1)} />
      )}
    </div>
  );
}
