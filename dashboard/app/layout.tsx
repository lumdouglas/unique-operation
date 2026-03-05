import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sushi Logistics — Today',
  description: 'Chef cockpit for daily orders and prep',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
