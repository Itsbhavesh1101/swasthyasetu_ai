"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import type { EngineeringDemoResult } from "../../lib/demo/contracts";

export function EngineeringResult({ intakeId }: Readonly<{ intakeId: string }>) {
  const [result, setResult] = useState<EngineeringDemoResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    void fetch(`/api/engineering-demo/intakes/${encodeURIComponent(intakeId)}/result`, {
      cache: "no-store",
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) throw new Error("unavailable");
        return (await response.json()) as EngineeringDemoResult;
      })
      .then(setResult)
      .catch((reason: unknown) => {
        if (!(reason instanceof DOMException && reason.name === "AbortError"))
          setError("The synthetic preview is unavailable. Your intake draft remains saved.");
      });
    return () => controller.abort();
  }, [intakeId]);

  if (error)
    return (
      <section className="state-panel" role="alert">
        <div>
          <h1>Preview unavailable</h1>
          <p>{error}</p>
          <Link className="action-link action-link--primary" href={`/intake/${intakeId}/review`}>
            Return to intake
          </Link>
        </div>
      </section>
    );
  if (!result) return <p role="status">Building the offline synthetic preview…</p>;
  if (result.status === "ABSTAINED")
    return (
      <div className="page-stack page-stack--narrow">
        <header className="page-header">
          <p className="eyebrow">Engineering-only demo</p>
          <h1>No fixture matched</h1>
          <p>{result.notice}</p>
        </header>
        <Link className="action-link action-link--primary" href={`/intake/${intakeId}/review`}>
          Return to intake
        </Link>
      </div>
    );
  return (
    <div className="page-stack page-stack--narrow">
      <header className="page-header">
        <p className="eyebrow">P8–P10 offline synthetic path</p>
        <h1>Synthetic result preview</h1>
        <p>{result.notice}</p>
      </header>
      <section className="content-card" aria-labelledby="extraction-heading">
        <h2 id="extraction-heading">Deterministic extraction</h2>
        <dl className="review-list">
          <div>
            <dt>Fixture label</dt>
            <dd>Synthetic pain</dd>
          </div>
          <div>
            <dt>Verification</dt>
            <dd>AI extracted, unconfirmed</dd>
          </div>
        </dl>
      </section>
      <section className="content-card" aria-labelledby="safety-heading">
        <h2 id="safety-heading">Synthetic safety mechanics</h2>
        <p>
          <strong>Not a medical assessment.</strong> These are engineering tokens only.
        </p>
        <dl className="review-list">
          <div>
            <dt>Route token</dt>
            <dd>
              <code>{result.safety_decision?.route}</code>
            </dd>
          </div>
          <div>
            <dt>Self-care blocked</dt>
            <dd>{result.safety_decision?.blocks_self_care ? "Yes" : "No"}</dd>
          </div>
        </dl>
      </section>
      <section className="content-card" aria-labelledby="summary-heading">
        <h2 id="summary-heading">Source-backed draft</h2>
        <p>Patient-reported source · unverified · clinician review required before any use.</p>
        {result.summary_sections.map((section) => (
          <p key={section.section_id}>
            <strong>{section.section_id.replaceAll("_", " ")}:</strong> Synthetic pain
          </p>
        ))}
      </section>
      <Link className="action-link action-link--secondary" href={`/intake/${intakeId}/review`}>
        Return to intake
      </Link>
    </div>
  );
}
