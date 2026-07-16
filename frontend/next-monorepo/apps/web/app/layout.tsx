import type { Metadata } from "next"
import { Syne, DM_Sans } from "next/font/google"
import { Toaster } from "sonner"

import "./globals.css"

const display = Syne({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "600", "700", "800"],
})

const body = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600", "700"],
})

export const metadata: Metadata = {
  title: "NominaFlow — Extracción inteligente de nóminas",
  description:
    "Sube una nómina, la IA extrae los datos y validamos lo que falla.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className={`${display.variable} ${body.variable}`}>
      <body className="nf-grid-bg min-h-screen font-[family-name:var(--font-body)] text-[var(--color-fog)] antialiased">
        {children}
        <Toaster
          theme="dark"
          position="top-right"
          toastOptions={{
            style: {
              background: "#141c2e",
              border: "1px solid #2a3548",
              color: "#c8d0dc",
            },
          }}
        />
      </body>
    </html>
  )
}
