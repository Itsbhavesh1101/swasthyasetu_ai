"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigationItems = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/profile", label: "Profile" },
  { href: "/history", label: "History" },
  { href: "/timeline", label: "Timeline" },
  { href: "/documents", label: "Documents" },
  { href: "/encounter", label: "Health journey" },
  { href: "/guidance", label: "Home guidance" },
] as const;

export function PatientNavigation() {
  const pathname = usePathname();

  return (
    <nav aria-label="Patient navigation" className="patient-navigation">
      {navigationItems.map((item) => (
        <Link
          aria-current={pathname === item.href ? "page" : undefined}
          className="navigation-link"
          href={item.href}
          key={item.href}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
