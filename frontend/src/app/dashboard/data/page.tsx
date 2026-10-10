"use client";

import { useRef, useState, type DragEvent } from "react";
import { useApp } from "@/components/providers";
import { Callout, Card, DataTable, Kpi, KpiGrid, PageHeader, PageSkeleton, Spinner } from "@/components/ui";
import { api, type Metrics, type Row } from "@/lib/api";
import { fmt } from "@/lib/format";

const REQUIRED = ["Order ID", "Order Date", "Region", "Category", "Sub-Category", "Product ID", "Product Name", "Sales", "Quantity", "Profit"];
const OPTIONAL = ["Ship Date", "Ship Mode", "Segment", "State", "Discount", "Unit Price", "Lead Time (Days)"];

export default function DataPage() {
  const { dataset: data, bump } = useApp();
  const [busy, setBusy] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [result, setResult] = useState<Metrics | null>(null);
  const [dragging, setDragging] = useState(false);
  const input = useRef<HTMLInputElement>(null);

  const run = async (label: string, fn: () => Promise<{ metrics: Metrics }>) => {
    setBusy(label);
    setActionError(null);
    setResult(null);
    try {
      const res = await fn();
      setResult(res.metrics);
      bump();
    } catch (e) {
      setActionError((e as Error).message);
    } finally {
      setBusy(null);
    }
  };

  const upload = (file: File) => {
    const form = new FormData();
    form.append("file", file);
    run(`Uploading ${file.name} and retraining`, () => api.post("/dataset/upload", form));
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) upload(f);
  };

  const columns = data ? data.columns.map((c) => ({ key: c, label: c })) : [];

  return (
    <>
      <PageHeader eyebrow="Model" title="Data" description="Upload your Superstore export (.xlsx or .csv). Every dashboard and the forecasting model are rebuilt from it automatically." />
      {!data && <PageSkeleton />}
      {data && (
        <div className="stack">
          <KpiGrid>
            <Kpi label="Active dataset" value={data.kind === "sample" ? "Sample" : "Uploaded"} hint={data.filename} />
            <Kpi label="Rows" value={fmt.int(data.rows)} hint={`${data.columns.length} columns`} />
            <Kpi label="Date range" value={`${data.min_date.slice(0, 4)}–${data.max_date.slice(0, 4)}`} hint={`${data.min_date} → ${data.max_date}`} />
            <Kpi label="Series" value={`${data.products * data.regions}`} hint={`${data.products} products × ${data.regions} regions`} />
          </KpiGrid>

          <div className="grid-2">
            <Card title="Upload dataset" subtitle="Validated, stored on the server, and used to retrain the model">
              <div
                className={`dropzone ${dragging ? "drag" : ""}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
                onClick={() => !busy && input.current?.click()}
                role="button"
                tabIndex={0}
                aria-disabled={!!busy}
                onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && !busy && input.current?.click()}
              >
                <span className="dropzone-icon">
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                    <path d="M12 16V4m0 0-4 4m4-4 4 4M5 20h14" />
                  </svg>
                </span>
                <strong>Drop a file or click to browse</strong>
                <span>.xlsx or .csv, up to 350 MB</span>
                <input
                  ref={input}
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  hidden
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) upload(f);
                    e.target.value = "";
                  }}
                />
              </div>
              <div className="row-actions">
                <button className="btn secondary" disabled={!!busy || data.kind === "sample"} onClick={() => run("Restoring sample data", () => api.post("/dataset/reset"))}>
                  Restore sample data
                </button>
                {busy && <Spinner label={busy} />}
              </div>
              {actionError && (
                <div style={{ marginTop: 14 }}>
                  <Callout tone="danger">{actionError}</Callout>
                </div>
              )}
              {result && (
                <div style={{ marginTop: 14 }}>
                  <Callout tone="success">
                    Model retrained. Holdout R² <strong>{result.test_r2.toFixed(3)}</strong> · MAE <strong>{result.mae.toFixed(2)}</strong> · MAPE <strong>{result.mape.toFixed(1)}%</strong>
                  </Callout>
                </div>
              )}
            </Card>

            <Card title="Expected schema" subtitle="Same columns as superstore_dataset.xlsx in the notebook">
              <div className="stack" style={{ gap: 16 }}>
                <div>
                  <span className="section-label">Required</span>
                  <div className="col-list">
                    {REQUIRED.map((c) => (
                      <code key={c}>{c}</code>
                    ))}
                  </div>
                </div>
                <div>
                  <span className="section-label">Optional</span>
                  <div className="col-list">
                    {OPTIONAL.map((c) => (
                      <code key={c}>{c}</code>
                    ))}
                  </div>
                </div>
                <p className="prose-sm">Missing optional columns are derived where possible (lead time from ship date, unit price from sales ÷ quantity) or filled with defaults. Training needs at least six months of history.</p>
              </div>
            </Card>
          </div>

          <Card title="Preview" subtitle="First rows of the active dataset">
            <DataTable<Row> rows={data.preview} columns={columns} pageSize={8} />
          </Card>
        </div>
      )}
    </>
  );
}
