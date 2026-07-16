"use client"

import { useCallback, useState } from "react"
import { useRouter } from "next/navigation"
import { useDropzone } from "react-dropzone"
import { Upload, Loader2, AlertCircle, FileText } from "lucide-react"
import { toast } from "sonner"

type Status = "idle" | "dragging" | "uploading" | "processing" | "error"

export function UploadZone() {
  const router = useRouter()
  const [status, setStatus] = useState<Status>("idle")
  const [fileName, setFileName] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (!file) return

      setFileName(file.name)
      setStatus("uploading")
      setError(null)

      const formData = new FormData()
      formData.append("file", file)

      try {
        const uploadRes = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        })

        if (!uploadRes.ok) {
          const err = await uploadRes.json().catch(() => ({}))
          throw new Error(
            typeof err.detail === "string"
              ? err.detail
              : "Error al subir el archivo"
          )
        }

        const upload = await uploadRes.json()
        setStatus("processing")
        toast.message("Archivo recibido", {
          description: "Extrayendo y validando con IA…",
        })

        const extractRes = await fetch(`/api/extract/${upload.file_id}`, {
          method: "POST",
        })

        if (!extractRes.ok) {
          const err = await extractRes.json().catch(() => ({}))
          throw new Error(
            typeof err.detail === "string"
              ? err.detail
              : "Error en la extracción OCR"
          )
        }

        toast.success("Extracción lista")
        router.push(`/result/${upload.file_id}`)
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Error inesperado"
        setStatus("error")
        setError(message)
        toast.error("No se pudo completar", { description: message })
      }
    },
    [router]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    disabled: status === "uploading" || status === "processing",
    onDragEnter: () => setStatus("dragging"),
    onDragLeave: () => setStatus("idle"),
  })

  const busy = status === "uploading" || status === "processing"
  const active = isDragActive || status === "dragging"

  return (
    <div className="w-full max-w-xl">
      <div
        {...getRootProps()}
        className={[
          "relative overflow-hidden border px-8 py-14 text-center transition-all duration-300",
          "cursor-pointer outline-none",
          active
            ? "border-[var(--color-signal)] bg-[var(--color-ink-soft)] scale-[1.01]"
            : status === "error"
              ? "border-[var(--color-danger)]/60 bg-[var(--color-ink-soft)]"
              : "border-[var(--color-fog)]/20 bg-[var(--color-ink-soft)]/80 hover:border-[var(--color-signal)]/50",
          busy ? "pointer-events-none" : "",
        ].join(" ")}
        style={busy ? { animation: "nf-pulse-ring 1.8s ease-out infinite" } : undefined}
      >
        <input {...getInputProps()} />

        {busy && <div className="nf-scan-line top-0" aria-hidden />}

        <div className="relative z-10 flex flex-col items-center gap-4">
          {busy ? (
            <Loader2 className="h-10 w-10 animate-spin text-[var(--color-signal)]" />
          ) : status === "error" ? (
            <AlertCircle className="h-10 w-10 text-[var(--color-danger)]" />
          ) : (
            <Upload className="h-10 w-10 text-[var(--color-signal)]" />
          )}

          {status === "idle" || status === "dragging" ? (
            <>
              <p className="font-[family-name:var(--font-display)] text-xl font-semibold text-white">
                {active ? "Suelta la nómina" : "Arrastra o elige un archivo"}
              </p>
              <p className="text-sm text-[var(--color-mist)]">
                PDF · JPEG · PNG · máx. 10 MB
              </p>
            </>
          ) : null}

          {status === "uploading" && (
            <>
              <p className="font-[family-name:var(--font-display)] text-xl font-semibold text-white">
                Subiendo…
              </p>
              <p className="flex items-center gap-2 text-sm text-[var(--color-mist)]">
                <FileText className="h-3.5 w-3.5" />
                {fileName}
              </p>
            </>
          )}

          {status === "processing" && (
            <>
              <p className="font-[family-name:var(--font-display)] text-xl font-semibold text-white">
                Extrayendo y validando…
              </p>
              <p className="text-sm text-[var(--color-mist)]">
                OCR + reglas de coherencia. Un momento.
              </p>
            </>
          )}

          {status === "error" && (
            <>
              <p className="font-[family-name:var(--font-display)] text-xl font-semibold text-[var(--color-danger)]">
                Algo falló
              </p>
              <p className="max-w-sm text-sm text-[var(--color-mist)]">{error}</p>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  setStatus("idle")
                  setError(null)
                  setFileName(null)
                }}
                className="mt-2 border border-[var(--color-fog)]/30 px-4 py-2 text-sm text-white transition hover:border-[var(--color-signal)] hover:text-[var(--color-signal)]"
              >
                Intentar de nuevo
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
