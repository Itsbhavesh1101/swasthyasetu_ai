"use client";

import Link from "next/link";
import { FormEvent, useEffect, useRef, useState } from "react";
import type { DocumentItem, DocumentState } from "../lib/documents/contracts";
import { ErrorState, LoadingState, Panel } from "./ui-primitives";

export function DocumentVault() {
  const [items, setItems] = useState<DocumentItem[]>();
  const [anonymous, setAnonymous] = useState(false);
  const [failed, setFailed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [revision, setRevision] = useState(0);
  const listHeading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    let active = true;
    void fetch("/api/patient/documents", { cache: "no-store" })
      .then(async (response) => ({ response, body: (await response.json()) as DocumentState }))
      .then(({ response, body }) => {
        if (!active) return;
        if (response.status === 401 || body.state === "ANONYMOUS") setAnonymous(true);
        else if (!response.ok || body.state !== "AUTHENTICATED") setFailed(true);
        else setItems(body.items);
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [revision]);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const form = event.currentTarget;
    setBusy(true);
    setMessage("");
    try {
      const response = await fetch("/api/patient/documents", {
        method: "POST",
        body: new FormData(form),
      });
      if (!response.ok) {
        setMessage(
          response.status === 413
            ? "That file is larger than 10 MB."
            : "Choose a valid PDF, JPEG, or PNG file.",
        );
        return;
      }
      form.reset();
      setMessage("Document uploaded securely.");
      setRevision((value) => value + 1);
    } catch {
      setMessage("The document could not be uploaded. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  if (anonymous)
    return (
      <Panel>
        <h2>Sign in to use your document vault</h2>
        <p>Your files are protected by your patient account.</p>
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
  if (!items) return <LoadingState label="Opening your private document vault." />;
  return (
    <div className="page-stack">
      <form className="panel document-upload" onSubmit={upload}>
        <h2>Upload a health document</h2>
        <p>PDF, JPEG, or PNG. Maximum size 10 MB.</p>
        <label>
          Choose document
          <input
            accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
            name="file"
            required
            type="file"
          />
        </label>
        {message ? (
          <p aria-live="polite" className="form-message">
            {message}
          </p>
        ) : null}
        <button className="button button--primary" disabled={busy} type="submit">
          {busy ? "Uploading…" : "Upload document"}
        </button>
      </form>
      <section className="panel" aria-labelledby="document-list-title">
        <h2 id="document-list-title" ref={listHeading} tabIndex={-1}>
          Your documents
        </h2>
        {items.length === 0 ? (
          <p>No documents uploaded yet.</p>
        ) : (
          <ul className="document-list">
            {items.map((item) => (
              <li key={item.documentId}>
                <div>
                  <strong>{item.displayName}</strong>
                  <small>{Math.ceil(item.byteSize / 1024)} KB</small>
                </div>
                <div className="inline-actions">
                  <a
                    className="button button--secondary"
                    href={`/api/patient/documents/${item.documentId}/content`}
                  >
                    Download
                  </a>
                  <button
                    className="button button--secondary"
                    type="button"
                    onClick={async () => {
                      if (!window.confirm(`Delete ${item.displayName}?`)) return;
                      const response = await fetch(`/api/patient/documents/${item.documentId}`, {
                        method: "DELETE",
                      });
                      if (response.ok) {
                        setMessage("Document deleted.");
                        setRevision((value) => value + 1);
                        listHeading.current?.focus();
                      } else setMessage("The document could not be deleted.");
                    }}
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
