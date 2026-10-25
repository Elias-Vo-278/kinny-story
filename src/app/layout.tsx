import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
    title: "Kinny Story — Find your next chapter",
    description: "A quiet corner for curious minds. Explore original stories, save your favorites, and find your next chapter.",
};
export default function RootLayout({ children, }: Readonly<{
    children: React.ReactNode;
}>) {
    return (<html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>);
}
