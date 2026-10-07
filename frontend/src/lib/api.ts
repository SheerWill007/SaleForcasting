"use client";

import { useEffect, useState } from "react";

export type Row = Record<string, string | number | null>;

export interface Kpis {
  total_sales: number;
  total_profit: number;
  total_quantity: number;
  total_orders: number;
  avg_discount: number;
  avg_lead_time: number;
  profit_margin: number;
}

export interface Group {
  name: string;
  sales: number;
  profit: number;
  quantity: number;
  orders: number;
}

export interface Overview {
  kpis: Kpis;
  yoy: { period_end: string; current: Kpis; previous: Kpis; change: Record<keyof Kpis, number | null> } | null;
  trend: { month: string; sales: number; profit: number; quantity: number; orders: number }[];
  by_category: Group[];
  by_region: Group[];
  top_products: Group[];
}

export interface Insights {
  by_subcategory: (Group & { category: string })[];
  by_state: (Group & { region: string })[];
  by_segment: Group[];
  by_ship_mode: Group[];
  products: { product: string; category: string; sub_category: string; sales: number; profit: number; quantity: number; orders: number; margin: number }[];
  demand_variability: { name: string; std: number }[];
  variability_median: number;
  order_scatter: { sales: number; profit: number }[];
}

export interface FilterOptions {
  regions: string[];
  categories: string[];
  segments: string[];
  products: { id: string; name: string }[];
  min_date: string;
  max_date: string;
}

export interface Metrics {
  train_r2: number;
  test_r2: number;
  mae: number;
  rmse: number;
  mape: number;
  gap: number;
  cv_ridge_r2: number;
  cv_gbr_r2: number;
  train_rows: number;
  test_rows: number;
  test_start: string;
  test_end: string;
}

export interface ModelInfo {
  metrics: Metrics;
  feature_importance: { feature: string; importance: number }[];
  trained_at: string;
  features: string[];
  ensemble: { ridge: number; gbr: number };
}

export interface Evaluation {
  by_month: { YearMonth: string; actual: number; predicted: number; error: number; abs_error: number }[];
  error_histogram: { bin: string; count: number }[];
  rows: { month: string; product: string; region: string; actual: number; predicted: number; error: number }[];
}

export interface Forecast {
  history: { month: string; actual: number; sales: number }[];
  forecast: { month: string; predicted: number; lower: number; upper: number; expected_sales: number }[];
  detail: { month: string; product_id: string; product: string; category: string; region: string; predicted: number; lower: number; upper: number; expected_sales: number }[];
  totals: { units: number; sales: number; last_year_units: number; last_year_sales: number };
}

export interface Inventory {
  service_level: number;
  z: number;
  month: string | null;
  rows: {
    product_id: string;
    product: string;
    category: string;
    region: string;
    predicted: number;
    daily_demand: number;
    lead_time: number;
    sigma: number;
    demand_cv: number;
    safety_stock: number;
    reorder_point: number;
  }[];
}

export interface DatasetInfo {
  filename: string;
  kind: "sample" | "upload";
  fingerprint: string;
  rows: number;
  columns: string[];
  min_date: string;
  max_date: string;
  products: number;
  regions: number;
  preview: Row[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

if (typeof window !== "undefined" && !API_BASE && !window.location.hostname.includes("localhost")) {
  console.error(
    "NEXT_PUBLIC_API_URL is not set. The frontend cannot reach the API in production. " +
    "Set NEXT_PUBLIC_API_URL to your Render backend URL (e.g., https://your-app.onrender.com) and rebuild."
  );
}

type Params = Record<string, string | number | string[] | undefined | null>;

export function buildQuery(params: Params = {}): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === "") continue;
    if (Array.isArray(v)) v.forEach((x) => q.append(k, x));
    else q.append(k, String(v));
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* not JSON */
    }
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  get: <T,>(path: string, params?: Params) => fetch(`${API_BASE}/api${path}${buildQuery(params)}`).then((r) => handle<T>(r)),
  post: <T,>(path: string, body?: FormData) => fetch(`${API_BASE}/api${path}`, { method: "POST", body }).then((r) => handle<T>(r)),
};

/** Fetch `path` whenever the serialized params change. `version` forces a refetch. */
export function useApi<T>(path: string, params?: Params, version = 0) {
  const key = path + buildQuery(params);
  const [state, setState] = useState<{ data: T | null; error: string | null; loading: boolean }>({
    data: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    api
      .get<T>(path, params)
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((e: Error) => alive && setState({ data: null, error: e.message, loading: false }));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, version]);

  return state;
}
