"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import type { HistoryFactType, HistoryItem, HistoryState } from "../lib/history/contracts";
import { ErrorState, LoadingState, Panel } from "./ui-primitives";
import { HistoryForm } from "./history-form";

const categoryIcons: Record<HistoryFactType, string> = {
  PROBLEM: "🩺",
  MEDICATION: "💊",
  ALLERGY: "⚠️",
  PROCEDURE: "🏥",
  OBSERVATION: "📊",
  INVESTIGATION: "🔬",
};

export function HistoryList() {
  const [items, setItems] = useState<HistoryItem[]>();
  const [anonymous, setAnonymous] = useState(false);
  const [failed, setFailed] = useState(false);
  const [correction, setCorrection] = useState<HistoryItem>();
  const [revision, setRevision] = useState(0);

  const [activeCategory, setActiveCategory] = useState<"ALL" | HistoryFactType | "TESTS">("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [showSuperseded, setShowSuperseded] = useState(true);
  const [targetFactType, setTargetFactType] = useState<HistoryFactType>("PROBLEM");
  const formRef = useRef<HTMLDivElement>(null);

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

  const conditionsCount = items.filter(
    (i) => i.factType === "PROBLEM" && i.verificationState !== "SUPERSEDED",
  ).length;
  const medicationsCount = items.filter(
    (i) => i.factType === "MEDICATION" && i.verificationState !== "SUPERSEDED",
  ).length;
  const allergiesCount = items.filter(
    (i) => i.factType === "ALLERGY" && i.verificationState !== "SUPERSEDED",
  ).length;
  const proceduresCount = items.filter(
    (i) => i.factType === "PROCEDURE" && i.verificationState !== "SUPERSEDED",
  ).length;
  const testsCount = items.filter(
    (i) =>
      (i.factType === "INVESTIGATION" || i.factType === "OBSERVATION") &&
      i.verificationState !== "SUPERSEDED",
  ).length;

  const filteredItems = items.filter((item) => {
    if (activeCategory === "TESTS") {
      if (item.factType !== "INVESTIGATION" && item.factType !== "OBSERVATION") return false;
    } else if (activeCategory !== "ALL") {
      if (item.factType !== activeCategory) return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      const matchLabel = item.label.toLowerCase().includes(q);
      const matchType = item.factType.toLowerCase().includes(q);
      const matchStatus = (item.status ?? "").toLowerCase().includes(q);
      if (!matchLabel && !matchType && !matchStatus) return false;
    }
    if (!showSuperseded && item.verificationState === "SUPERSEDED") {
      return false;
    }
    return true;
  });

  function selectCategory(category: "ALL" | HistoryFactType | "TESTS") {
    setActiveCategory(category);
    if (category !== "ALL" && category !== "TESTS") {
      setTargetFactType(category);
    } else if (category === "TESTS") {
      setTargetFactType("INVESTIGATION");
    }
  }

  function startAdd(type: HistoryFactType) {
    setCorrection(undefined);
    setTargetFactType(type);
    formRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }

  return (
    <div className="page-stack">
      {items.length > 0 ? (
        <div aria-label="Medical history summary" className="history-stats-grid">
          <button
            className={
              activeCategory === "PROBLEM"
                ? "history-stat-card history-stat-card--active"
                : "history-stat-card"
            }
            onClick={() => selectCategory("PROBLEM")}
            type="button"
          >
            <span className="history-stat-number">{conditionsCount}</span>
            <span className="history-stat-label">🩺 Conditions</span>
          </button>
          <button
            className={
              activeCategory === "MEDICATION"
                ? "history-stat-card history-stat-card--active"
                : "history-stat-card"
            }
            onClick={() => selectCategory("MEDICATION")}
            type="button"
          >
            <span className="history-stat-number">{medicationsCount}</span>
            <span className="history-stat-label">💊 Medicines</span>
          </button>
          <button
            className={
              activeCategory === "ALLERGY"
                ? "history-stat-card history-stat-card--active"
                : "history-stat-card"
            }
            onClick={() => selectCategory("ALLERGY")}
            type="button"
          >
            <span className="history-stat-number">{allergiesCount}</span>
            <span className="history-stat-label">⚠️ Allergies</span>
          </button>
          <button
            className={
              activeCategory === "PROCEDURE" || activeCategory === "TESTS"
                ? "history-stat-card history-stat-card--active"
                : "history-stat-card"
            }
            onClick={() => selectCategory("PROCEDURE")}
            type="button"
          >
            <span className="history-stat-number">{proceduresCount + testsCount}</span>
            <span className="history-stat-label">🏥 Procedures & Tests</span>
          </button>
        </div>
      ) : null}

      <section aria-labelledby="history-list-title" className="panel">
        <p className="card-kicker">Longitudinal record</p>
        <div className="history-header-actions">
          <h2 id="history-list-title">Your entries</h2>
          {items.length > 0 ? (
            <div className="inline-actions">
              <button
                className="button button--secondary"
                onClick={() => startAdd("PROBLEM")}
                type="button"
              >
                + Condition
              </button>
              <button
                className="button button--secondary"
                onClick={() => startAdd("MEDICATION")}
                type="button"
              >
                + Medicine
              </button>
              <button
                className="button button--secondary"
                onClick={() => startAdd("ALLERGY")}
                type="button"
              >
                + Allergy
              </button>
            </div>
          ) : null}
        </div>

        {items.length === 0 ? (
          <p>No history entries yet. Use the form below to add your first one.</p>
        ) : (
          <>
            <div aria-label="Filter entries by type" className="category-tabs" role="toolbar">
              <button
                className={
                  activeCategory === "ALL" ? "category-tab category-tab--active" : "category-tab"
                }
                onClick={() => selectCategory("ALL")}
                type="button"
              >
                All <span className="category-tab-count">{items.length}</span>
              </button>
              <button
                className={
                  activeCategory === "PROBLEM"
                    ? "category-tab category-tab--active"
                    : "category-tab"
                }
                onClick={() => selectCategory("PROBLEM")}
                type="button"
              >
                Conditions <span className="category-tab-count">{conditionsCount}</span>
              </button>
              <button
                className={
                  activeCategory === "MEDICATION"
                    ? "category-tab category-tab--active"
                    : "category-tab"
                }
                onClick={() => selectCategory("MEDICATION")}
                type="button"
              >
                Medicines <span className="category-tab-count">{medicationsCount}</span>
              </button>
              <button
                className={
                  activeCategory === "ALLERGY"
                    ? "category-tab category-tab--active"
                    : "category-tab"
                }
                onClick={() => selectCategory("ALLERGY")}
                type="button"
              >
                Allergies <span className="category-tab-count">{allergiesCount}</span>
              </button>
              <button
                className={
                  activeCategory === "PROCEDURE"
                    ? "category-tab category-tab--active"
                    : "category-tab"
                }
                onClick={() => selectCategory("PROCEDURE")}
                type="button"
              >
                Procedures <span className="category-tab-count">{proceduresCount}</span>
              </button>
              <button
                className={
                  activeCategory === "TESTS" ? "category-tab category-tab--active" : "category-tab"
                }
                onClick={() => selectCategory("TESTS")}
                type="button"
              >
                Tests & Observations <span className="category-tab-count">{testsCount}</span>
              </button>
            </div>

            <div className="history-filter-bar">
              <input
                aria-label="Search entries"
                className="history-search-input"
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search entries by name or keyword…"
                type="search"
                value={searchQuery}
              />
              <label className="history-filter-toggle">
                <input
                  checked={showSuperseded}
                  onChange={(e) => setShowSuperseded(e.target.checked)}
                  type="checkbox"
                />
                Show previous versions
              </label>
            </div>

            {filteredItems.length === 0 ? (
              <p>No entries match the selected filter.</p>
            ) : (
              <ul className="history-list">
                {filteredItems.map((item) => (
                  <li
                    className={
                      item.verificationState === "SUPERSEDED"
                        ? "history-item history-item--previous"
                        : "history-item"
                    }
                    key={item.factId}
                  >
                    <div>
                      <p className="card-kicker">
                        {categoryIcons[item.factType]} {item.factType.replaceAll("_", " ")}
                      </p>
                      <h3>{item.label}</h3>
                      <div className="badge-row">
                        {item.status ? (
                          <span
                            className={
                              item.status.toUpperCase() === "ACTIVE"
                                ? "badge badge--active"
                                : item.status.toUpperCase() === "RESOLVED"
                                  ? "badge badge--resolved"
                                  : item.status.toUpperCase() === "STOPPED"
                                    ? "badge badge--stopped"
                                    : "badge badge--historical"
                            }
                          >
                            {item.status}
                          </span>
                        ) : null}
                        <span
                          className={
                            item.verificationState === "SUPERSEDED"
                              ? "badge badge--superseded"
                              : "badge badge--confirmed"
                          }
                        >
                          {item.verificationState === "SUPERSEDED"
                            ? "Archived version"
                            : "Patient reported"}
                        </span>
                      </div>
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
                        onClick={() => {
                          setCorrection(item);
                          formRef.current?.scrollIntoView?.({ behavior: "smooth" });
                        }}
                        type="button"
                      >
                        Correct entry
                      </button>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>

      <div ref={formRef}>
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
          <HistoryForm
            initialFactType={targetFactType}
            key={`new-history-entry-${targetFactType}`}
            onSaved={() => setRevision((value) => value + 1)}
          />
        )}
      </div>
    </div>
  );
}
