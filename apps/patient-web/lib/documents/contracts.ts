export type DocumentItem = {
  documentId: string;
  displayName: string;
  mimeType: string;
  byteSize: number;
  createdAt: string;
};

export type DocumentState =
  { state: "AUTHENTICATED"; items: DocumentItem[] } | { state: "ANONYMOUS" };
