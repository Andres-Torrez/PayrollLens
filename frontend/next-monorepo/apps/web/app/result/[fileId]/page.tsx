"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { ArrowLeft, Loader2, ShieldAlert, ShieldCheck } from "lucide-react"

type Flag = { field: string; reason: string; severity: string }

type ExtractionRecord = {
  id: string
  filename: string
  es_nomina: boolean | null
  nombre_trabajador: string | null
  nombre_empresa: string | null
  ingresos_brutos: number | null
  ingresos_netos: number | null
  fecha_nomina: string | null
  iban: string | null
  overall_confidence: string
  status: string
  validation_flags: Flag[]
  created_at: string
}

const FIELDS: { key: keyof ExtractionRecord; label: string }[] = [
  { key: "nombre_trabajador", label: "Trabajador" },
  { key: "nombre_empresa", label: "Empresa" },
  { key: "ingresos_brutos", label: "Ingresos brutos" },
  { key: "ingresos_netos", label: "Ingresos netos" },
  { key: "fecha_nomina", label: "Fecha / período" },
  { key: "iban", label: "IBAN" },
]

function formatValue(key: string, value: unknown): string {
  if (value === null || value === undefined || value === "") return "—"
  if (typeof value === "number") {
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "EUR",
    }).format(value)
  }
  return String(value)
}

export default function ResultPage() {
  const params = useParams<{ fileId: string }>()
  const fileId = params.fileId

  const [data, setData] = useState<ExtractionRecord | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!fileId) return

    let cancelled = false

    async function load() {
      setLoading(true)
      setError(null)

      try {
        // Prefer saved record (no re-OCR)
        let res = await fetch(`/api/extractions/${fileId}`)

        if (res.status === 404) {
          // Not saved yet → run extract
          res = await fetch(`/api/extract/${fileId}`, { method: "POST" })
          if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            throw new Error(
              typeof err.detail === "string"
                ? err.detail
                : "No se pudo extraer la nómina"
            )
          }
          // Extract returns ValidationResult; reload from DB
          res = await fetch(`/api/extractions/${fileId}`)
        }

        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(
            typeof err.detail === "string"
              ? err.detail
              : "No se encontró el resultado"
          )
        }

        const record = (await res.json()) as ExtractionRecord
        if (!cancelled) setData(record)
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Error al cargar")
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [fileId])

  const flagsByField = new Map<string, Flag[]>()
  if (data?.validation_flags) {
    for (const flag of data.validation_flags) {
      const list = flagsByField.get(flag.field) ?? []
      list.push(flag)
      flagsByField.set(flag.field, list)
    }
  }

  const confidenceColor =
    data?.overall_confidence === "high"
      ? "text-[var(--color-ok)]"
      : data?.overall_confidence === "medium"
        ? "text-[var(--color-warn)]"
        : "text-[var(--color-danger)]"

  return (
    <main className="relative min-h-screen">
      <div className="mx-auto max-w-3xl px-6 py-10 md:px-10 md:py-14">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-[var(--color-mist)] transition hover:text-[var(--color-signal)]"
        >
          <ArrowLeft className="h-4 w-4" />
          Nueva nómina
        </Link>

        <header className="mt-10 nf-fade-up">
          <p className="font-[family-name:var(--font-display)] text-lg font-bold text-white">
            Nomina<span className="text-[var(--color-signal)]">Flow</span>
          </p>
          <h1 className="mt-4 font-[family-name:var(--font-display)] text-3xl font-extrabold tracking-tight text-white md:text-4xl">
            Resultado de extracción
          </h1>
        </header>

        {loading && (
          <div className="mt-16 flex flex-col items-center gap-4 text-[var(--color-mist)]">
            <Loader2 className="h-8 w-8 animate-spin text-[var(--color-signal)]" />
            <p>Cargando datos validados…</p>
          </div>
        )}

        {error && !loading && (
          <div className="mt-12 border border-[var(--color-danger)]/40 bg-[var(--color-ink-soft)] p-6">
            <p className="font-[family-name:var(--font-display)] text-lg text-[var(--color-danger)]">
              No se pudo mostrar el resultado
            </p>
            <p className="mt-2 text-sm text-[var(--color-mist)]">{error}</p>
            <p className="mt-4 text-xs text-[var(--color-mist)]">
              Comprueba que el backend esté en el puerto 8001.
            </p>
          </div>
        )}

        {data && !loading && (
          <div className="mt-10 space-y-8 nf-fade-up-delay">
            <div className="flex flex-wrap items-center gap-4 border-b border-[var(--color-fog)]/10 pb-6">
              <div className="flex items-center gap-2">
                {data.status === "validated" ? (
                  <ShieldCheck className={`h-5 w-5 ${confidenceColor}`} />
                ) : (
                  <ShieldAlert className={`h-5 w-5 ${confidenceColor}`} />
                )}
                <span className={`text-sm font-semibold uppercase tracking-wider ${confidenceColor}`}>
                  {data.overall_confidence} · {data.status}
                </span>
              </div>
              <p className="truncate text-sm text-[var(--color-mist)]">
                {data.filename}
              </p>
            </div>

            <dl className="divide-y divide-[var(--color-fog)]/10">
              {FIELDS.map(({ key, label }) => {
                const flags = flagsByField.get(key) ?? []
                return (
                  <div
                    key={key}
                    className="grid gap-2 py-5 md:grid-cols-[160px_1fr]"
                  >
                    <dt className="text-xs uppercase tracking-[0.16em] text-[var(--color-mist)]">
                      {label}
                    </dt>
                    <dd>
                      <p className="font-[family-name:var(--font-display)] text-lg font-semibold text-white md:text-xl">
                        {formatValue(key, data[key])}
                      </p>
                      {flags.map((f, i) => (
                        <p
                          key={`${f.field}-${i}`}
                          className={`mt-1 text-sm ${
                            f.severity === "error"
                              ? "text-[var(--color-danger)]"
                              : "text-[var(--color-warn)]"
                          }`}
                        >
                          {f.severity === "error" ? "Error" : "Aviso"}: {f.reason}
                        </p>
                      ))}
                    </dd>
                  </div>
                )
              })}
            </dl>

            {data.validation_flags.length === 0 && (
              <p className="text-sm text-[var(--color-ok)]">
                Sin flags: los campos pasaron las reglas de validación.
              </p>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
