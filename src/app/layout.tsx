import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CleanCheckpoint | Verified service checkpoints on GenLayer",
  description: "Checkpoint-based cleaning service escrow with exception-only semantic consensus.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
