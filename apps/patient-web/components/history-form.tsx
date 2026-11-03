"use client";

import { FormEvent, useState } from "react";

import type { HistoryFactType, HistoryItem, HistoryPayload } from "../lib/history/contracts";

const labels: Record<HistoryFactType, string> = {
  PROBLEM: "Condition",
  MEDICATION: "Medicine",
  ALLERGY: "Allergy",
  PROCEDURE: "Procedure",
  OBSERVATION: "Observation",
  INVESTIGATION: "Investigation or test",
};

function text(data: FormData, name: string) {
  const value = String(data.get(name) ?? "").trim();
  return value || undefined;
}

function instant(data: FormData, name: string) {
  const value = text(data, name);
  return value ? new Date(value).toISOString() : undefined;
}

function payload(data: FormData, factType: HistoryFactType): HistoryPayload {
  const result: HistoryPayload = { fact_type: factType };
  const add = (name: string, value: string | undefined) => {
    if (value !== undefined) result[name] = value;
  };
  if (factType === "PROBLEM") {
    add("label", text(data, "label"));
    add("status", text(data, "status"));
    add("onset", text(data, "onset"));
    add("resolution", text(data, "resolution"));
  } else if (factType === "MEDICATION") {
    add("name", text(data, "label"));
    add("status", text(data, "status"));
    add("dose", text(data, "dose"));
    add("dose_unit", text(data, "unit"));
    add("frequency", text(data, "frequency"));
    add("indication", text(data, "notes"));
  } else if (factType === "ALLERGY") {
    add("substance", text(data, "label"));
    add("status", text(data, "status"));
    add("reaction", text(data, "notes"));
    add("severity", text(data, "severity"));
  } else if (factType === "PROCEDURE") {
    add("name", text(data, "label"));
    add("performed_at", instant(data, "performedAt"));
    add("facility", text(data, "facility"));
    add("notes", text(data, "notes"));
  } else if (factType === "OBSERVATION") {
    add("observation_type", text(data, "label"));
    add("text_value", text(data, "observationValue"));
    add("unit", text(data, "unit"));
  } else {
    add("investigation_type", text(data, "label"));
    add("status", text(data, "status"));
    add("performed_at", instant(data, "performedAt"));
    add("result_summary", text(data, "notes"));
  }
  return result;
}

export function HistoryForm({
  correction,
  onCancel,
  onSaved,
}: Readonly<{
  correction?: HistoryItem;
  onCancel?: () => void;
  onSaved: () => void;
}>) {
  const [factType, setFactType] = useState<HistoryFactType>(correction?.factType ?? "PROBLEM");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const form = event.currentTarget;
    setBusy(true);
    setMessage("");
    const body = payload(new FormData(form), factType);
    const url = correction
      ? `/api/patient/history/${correction.factId}/supersede`
      : "/api/patient/history";
    try {
      const result = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!result.ok) {
        setMessage(
          result.status === 409
            ? "This entry changed. Reload your history and try again."
            : "The entry could not be saved. Check the details and try again.",
        );
        return;
      }
      form.reset();
      setMessage(correction ? "The corrected entry has been saved." : "The entry has been added.");
      onSaved();
    } catch {
      setMessage("The entry could not be saved. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  const needsStatus = ["PROBLEM", "MEDICATION", "ALLERGY", "INVESTIGATION"].includes(factType);
  return (
    <form className="history-form panel" onSubmit={submit}>
      <div>
        <p className="card-kicker">{correction ? "Correct an entry" : "Add to your history"}</p>
        <h2>{correction ? `Replace “${correction.label}”` : "Record health information"}</h2>
        <p>Enter information you know. You can correct it later without erasing its history.</p>
      </div>
      <div className="form-grid">
        <label>
          Category
          <select
            disabled={Boolean(correction)}
            name="factType"
            onChange={(event) => setFactType(event.target.value as HistoryFactType)}
            value={factType}
          >
            {Object.entries(labels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label>
          {labels[factType]} name
          <input defaultValue={correction?.label ?? ""} maxLength={256} name="label" required />
        </label>
        {needsStatus ? (
          <label>
            Status
            {factType === "PROBLEM" || factType === "MEDICATION" ? (
              <select defaultValue={correction?.status ?? "ACTIVE"} name="status" required>
                <option value="ACTIVE">Active</option>
                <option value="HISTORICAL">Historical</option>
                {factType === "PROBLEM" ? (
                  <option value="RESOLVED">Resolved</option>
                ) : (
                  <option value="STOPPED">Stopped</option>
                )}
                <option value="UNKNOWN">Unknown</option>
              </select>
            ) : (
              <input
                defaultValue={correction?.status ?? "ACTIVE"}
                maxLength={64}
                name="status"
                required
              />
            )}
          </label>
        ) : null}
        {factType === "PROBLEM" ? (
          <>
            <label>
              Started on (optional)
              <input name="onset" type="date" />
            </label>
            <label>
              Resolved on (optional)
              <input name="resolution" type="date" />
            </label>
          </>
        ) : null}
        {factType === "MEDICATION" ? (
          <>
            <label>
              Dose (optional)
              <input inputMode="decimal" name="dose" />
            </label>
            <label>
              Dose unit (optional)
              <input maxLength={128} name="unit" />
            </label>
            <label>
              How often (optional)
              <input maxLength={128} name="frequency" />
            </label>
          </>
        ) : null}
        {factType === "ALLERGY" ? (
          <label>
            Severity (optional)
            <input maxLength={128} name="severity" />
          </label>
        ) : null}
        {factType === "PROCEDURE" || factType === "INVESTIGATION" ? (
          <label>
            When (optional)
            <input name="performedAt" type="datetime-local" />
          </label>
        ) : null}
        {factType === "PROCEDURE" ? (
          <label>
            Facility (optional)
            <input maxLength={256} name="facility" />
          </label>
        ) : null}
        {factType === "OBSERVATION" ? (
          <>
            <label>
              Value
              <input maxLength={2000} name="observationValue" required />
            </label>
            <label>
              Unit (optional)
              <input maxLength={128} name="unit" />
            </label>
          </>
        ) : null}
        {!["PROBLEM", "OBSERVATION"].includes(factType) ? (
          <label>
            {factType === "ALLERGY" ? "Reaction" : factType === "MEDICATION" ? "Reason" : "Notes"}{" "}
            (optional)
            <textarea maxLength={2000} name="notes" rows={3} />
          </label>
        ) : null}
      </div>
      {message ? (
        <p aria-live="polite" className="form-message">
          {message}
        </p>
      ) : null}
      <div className="inline-actions">
        <button className="button button--primary" disabled={busy} type="submit">
          {busy ? "Saving…" : correction ? "Save correction" : "Add entry"}
        </button>
        {onCancel ? (
          <button className="button button--secondary" onClick={onCancel} type="button">
            Cancel
          </button>
        ) : null}
      </div>
    </form>
  );
}
