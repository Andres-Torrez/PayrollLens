import { UploadZone } from "@/components/upload-zone"

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute -right-24 top-20 h-72 w-72 rounded-full bg-[var(--color-signal)]/10 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -left-16 bottom-10 h-64 w-64 rounded-full bg-[#3d6bff]/15 blur-3xl"
      />

      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-10 md:px-10 md:py-14">
        <header className="nf-fade-up flex items-baseline justify-between gap-4">
          <p className="font-[family-name:var(--font-display)] text-2xl font-extrabold tracking-tight text-white md:text-3xl">
            Nomina<span className="text-[var(--color-signal)]">Flow</span>
          </p>
          <p className="text-xs uppercase tracking-[0.2em] text-[var(--color-mist)]">
            Kontaktu · 2026
          </p>
        </header>

        <section className="mt-16 flex flex-1 flex-col justify-center gap-12 md:mt-20 md:gap-16">
          <div className="nf-fade-up-delay max-w-2xl">
            <h1 className="font-[family-name:var(--font-display)] text-4xl font-extrabold leading-[1.05] tracking-tight text-white md:text-6xl">
              La nómina habla.
              <span className="mt-2 block text-[var(--color-signal)]">
                Nosotros verificamos.
              </span>
            </h1>
            <p className="mt-5 max-w-lg text-base leading-relaxed text-[var(--color-mist)] md:text-lg">
              Sube un PDF o imagen. Extraemos trabajador, empresa, brutos,
              netos, fecha e IBAN — y marcamos lo que la IA deja dudoso.
            </p>
          </div>

          <div className="nf-fade-up-delay-2">
            <UploadZone />
          </div>
        </section>
      </div>
    </main>
  )
}
