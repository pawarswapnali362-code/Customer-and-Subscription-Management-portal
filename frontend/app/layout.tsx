import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = {
  title: "Cliently · Customer portal",
  description: "Customer, product, subscription, payment, activation and issue management.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
