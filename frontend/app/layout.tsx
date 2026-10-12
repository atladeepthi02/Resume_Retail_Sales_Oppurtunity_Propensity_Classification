import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Retail Sales Opportunity Propensity',
  description: 'Retail sales analytics dashboard for propensity classification',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
