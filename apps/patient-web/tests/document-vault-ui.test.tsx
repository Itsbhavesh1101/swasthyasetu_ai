import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import DocumentsPage from "../app/documents/page";

beforeEach(() => vi.unstubAllGlobals());
afterEach(() => vi.restoreAllMocks());

it("shows an accessible empty vault and uploads a selected document", async () => {
  const user = userEvent.setup();
  const fetchSpy = vi
    .fn()
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", items: [] }))
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", item: {} }, { status: 201 }))
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", items: [] }));
  vi.stubGlobal("fetch", fetchSpy);
  render(<DocumentsPage />);
  expect(await screen.findByText(/no documents uploaded yet/i)).toBeVisible();
  const input = screen.getByLabelText(/choose document/i) as HTMLInputElement;
  await user.upload(input, new File(["%PDF-x"], "report.pdf", { type: "application/pdf" }));
  expect(input.files).toHaveLength(1);
  // jsdom keeps a required file input invalid after userEvent populates its FileList.
  // Submit the form directly so this test exercises the React upload boundary.
  fireEvent.submit(input.form!);
  expect(fetchSpy).toHaveBeenCalledTimes(2);
  expect(await screen.findByText(/uploaded securely/i)).toBeVisible();
  await waitFor(() => expect(fetchSpy).toHaveBeenCalledTimes(3));
});

it("lists, downloads, and explicitly confirms deletion before returning focus", async () => {
  const user = userEvent.setup();
  const documentId = "3f0bb868-b00b-41c6-9335-f9c8b96ce7b3";
  const fetchSpy = vi
    .fn()
    .mockResolvedValueOnce(
      Response.json({
        state: "AUTHENTICATED",
        items: [
          {
            documentId,
            displayName: "report.pdf",
            mimeType: "application/pdf",
            byteSize: 2048,
            createdAt: "2026-11-03T14:00:00Z",
          },
        ],
      }),
    )
    .mockResolvedValueOnce(new Response(null, { status: 204 }))
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", items: [] }));
  vi.stubGlobal("fetch", fetchSpy);
  const confirm = vi.spyOn(window, "confirm").mockReturnValue(true);
  render(<DocumentsPage />);

  expect(await screen.findByText("report.pdf")).toBeVisible();
  expect(screen.getByRole("link", { name: "Download" })).toHaveAttribute(
    "href",
    `/api/patient/documents/${documentId}/content`,
  );
  await user.click(screen.getByRole("button", { name: "Delete" }));

  expect(confirm).toHaveBeenCalledWith("Delete report.pdf?");
  expect(await screen.findByText("Document deleted.")).toBeVisible();
  expect(screen.getByRole("heading", { name: "Your documents" })).toHaveFocus();
  await waitFor(() => expect(fetchSpy).toHaveBeenCalledTimes(3));
});
