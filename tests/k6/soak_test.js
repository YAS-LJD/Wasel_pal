/**
 * tests/k6/soak_test.js — Soak Test (30 minutes)
 * Person 4: k6 Load Testing
 *
 * Applies sustained moderate load for 30 minutes to detect:
 *   - Memory leaks
 *   - DB connection pool exhaustion
 *   - Redis connection drift
 *   - Gradual performance degradation
 *
 * Run: k6 run tests/k6/soak_test.js
 * (Takes ~35 minutes end-to-end including ramp-up/down)
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API      = `${BASE_URL}/api/v1`;
const TOKEN    = __ENV.TOKEN    || "replace-with-valid-jwt";

const HEADERS = {
  "Content-Type":  "application/json",
  "Authorization": `Bearer ${TOKEN}`,
};

// ── Custom Metrics ─────────────────────────────────────────────────────────
const errorRate        = new Rate("soak_error_rate");
const p95Trend         = new Trend("soak_p95_duration", true);
const totalRequests    = new Counter("soak_total_requests");

// ── Options ────────────────────────────────────────────────────────────────
export const options = {
  scenarios: {
    soak: {
      executor:  "constant-vus",
      vus:       20,
      duration:  "35m",   // 2.5 min ramp + 30 min sustain + 2.5 min ramp down
    },
  },

  stages: [
    { duration: "2m30s", target: 20 },   // ramp up
    { duration: "30m",   target: 20 },   // sustain for 30 minutes
    { duration: "2m30s", target: 0  },   // ramp down
  ],

  thresholds: {
    http_req_duration:  ["p(95)<600", "p(99)<1200"],
    http_req_failed:    ["rate<0.02"],    // < 2 % throughout the soak
    soak_error_rate:    ["rate<0.02"],
  },
};

// ── Data Helpers ───────────────────────────────────────────────────────────
const REGIONS     = ["Ramallah", "Nablus", "Hebron", "Jenin", "Tulkarm", "Bethlehem"];
const CATEGORIES  = ["delay", "closure", "accident", "military_activity"];
const SEVERITIES  = ["low", "medium", "high"];

function randomItem(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randomId(max = 10) { return Math.floor(Math.random() * max) + 1; }

// ── Main VU function ───────────────────────────────────────────────────────
export default function () {
  const region = randomItem(REGIONS);
  const roll   = Math.random();

  if (roll < 0.30) {
    // ── Read incidents (30 %) ─────────────────────────────────────────────
    group("read_incidents", () => {
      const start = Date.now();
      const res   = http.get(
        `${API}/incidents?region=${region}&page=1&limit=10`,
        { headers: HEADERS }
      );
      p95Trend.add(Date.now() - start);
      totalRequests.add(1);
      const ok = check(res, {
        "incidents 200":     (r) => r.status === 200,
        "incidents body ok": (r) => r.body && r.body.length > 0,
      });
      errorRate.add(!ok);
    });

  } else if (roll < 0.55) {
    // ── Read checkpoints (25 %) ───────────────────────────────────────────
    group("read_checkpoints", () => {
      const start = Date.now();
      const res   = http.get(
        `${API}/checkpoints?region=${region}&limit=10`,
        { headers: HEADERS }
      );
      p95Trend.add(Date.now() - start);
      totalRequests.add(1);
      const ok = check(res, { "checkpoints 200": (r) => r.status === 200 });
      errorRate.add(!ok);
    });

  } else if (roll < 0.70) {
    // ── Read stats (15 %) ─────────────────────────────────────────────────
    group("read_stats", () => {
      const res = http.get(`${API}/stats/checkpoints`, { headers: HEADERS });
      totalRequests.add(1);
      const ok = check(res, { "stats 200": (r) => r.status === 200 });
      errorRate.add(!ok);
    });

  } else if (roll < 0.85) {
    // ── Submit report (15 %) ──────────────────────────────────────────────
    group("submit_report", () => {
      const payload = JSON.stringify({
        checkpoint_id: randomId(10),
        category:      randomItem(CATEGORIES),
        description:   `Soak test report — ${new Date().toISOString()}`,
        severity:      randomItem(SEVERITIES),
      });
      const start = Date.now();
      const res   = http.post(`${API}/reports`, payload, { headers: HEADERS });
      p95Trend.add(Date.now() - start);
      totalRequests.add(1);
      const ok = check(res, { "report 201/200": (r) => r.status === 200 || r.status === 201 });
      errorRate.add(!ok);
    });

  } else if (roll < 0.93) {
    // ── Weather API (8 %) — exercises cache + external call ───────────────
    group("weather_api", () => {
      const res = http.get(
        `${API}/external/weather/${region}`,
        { headers: HEADERS }
      );
      totalRequests.add(1);
      const ok = check(res, {
        "weather not 5xx": (r) => r.status < 500,
      });
      errorRate.add(!ok);
    });

  } else {
    // ── Predict endpoint (7 %) ────────────────────────────────────────────
    group("predict_region", () => {
      const res = http.get(
        `${API}/predict/region/${region}`,
        { headers: HEADERS }
      );
      totalRequests.add(1);
      const ok = check(res, {
        "predict not 5xx": (r) => r.status < 500,
      });
      errorRate.add(!ok);
    });
  }

  // Realistic think time: 1–3 seconds
  sleep(1 + Math.random() * 2);
}

// ── Summary hook ──────────────────────────────────────────────────────────
export function handleSummary(data) {
  const p95 = data.metrics.http_req_duration?.values?.["p(95)"] || 0;
  const p99 = data.metrics.http_req_duration?.values?.["p(99)"] || 0;
  const err = (data.metrics.http_req_failed?.values?.rate || 0) * 100;
  const tot = data.metrics.soak_total_requests?.values?.count || 0;

  console.log("\n========= SOAK TEST SUMMARY =========");
  console.log(`Total requests : ${tot}`);
  console.log(`P95 latency    : ${p95.toFixed(1)} ms`);
  console.log(`P99 latency    : ${p99.toFixed(1)} ms`);
  console.log(`Error rate     : ${err.toFixed(2)} %`);
  console.log("=====================================\n");

  return {
    stdout: JSON.stringify(data, null, 2),
  };
}
