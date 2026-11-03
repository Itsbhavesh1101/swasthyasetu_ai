import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "SwasthyaSetu Patient",
    short_name: "SwasthyaSetu",
    description:
      "A private patient health hub for personal history, documents, intake, and wellness guidance.",
    start_url: "/dashboard",
    scope: "/",
    display: "standalone",
    background_color: "#f5f7f2",
    theme_color: "#176448",
    lang: "en",
    icons: [
      { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
      {
        src: "/icons/icon-maskable-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
