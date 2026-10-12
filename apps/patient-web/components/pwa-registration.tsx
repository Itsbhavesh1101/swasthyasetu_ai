"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";

export function PwaRegistration() {
  const pathname = usePathname();
  const previousPath = useRef(pathname);

  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;
    void navigator.serviceWorker
      .register("/sw.js", { scope: "/", updateViaCache: "none" })
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    if (previousPath.current === pathname) return;
    previousPath.current = pathname;
    window.requestAnimationFrame(() =>
      document.querySelector<HTMLElement>("#main-content")?.focus(),
    );
  }, [pathname]);

  return null;
}
