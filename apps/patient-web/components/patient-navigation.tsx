"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigationItems = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/login", label: "Sign in" },
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
