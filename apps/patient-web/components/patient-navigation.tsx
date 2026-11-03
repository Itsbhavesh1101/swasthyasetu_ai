"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigationItems = [
  { href: "/", icon: "H", label: "Home" },
  { href: "/dashboard", icon: "D", label: "Dashboard" },
  { href: "/profile", icon: "P", label: "Profile" },
  { href: "/history", icon: "+", label: "History" },
  { href: "/timeline", icon: "T", label: "Timeline" },
  { href: "/documents", icon: "F", label: "Documents" },
  { href: "/encounter", icon: "J", label: "Health journey" },
  { href: "/guidance", icon: "G", label: "Home guidance" },
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
          <span aria-hidden="true" className="navigation-icon">
            {item.icon}
          </span>
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
}
