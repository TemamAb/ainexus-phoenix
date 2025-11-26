import type { Metadata } from "next";
import "./globals.css"; // CRITICAL: Imports the theme

export const metadata: Metadata = {
  title: "QuantumNex | Mission Control",
  description: "Institutional DeFi Autonomy Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-grafana-bg text-white min-h-screen selection:bg-grafana-blue selection:text-white">
        {children}
      </body>
    </html>
  );
}
