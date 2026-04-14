/**
 * tests/k6/load_test.js — Normal Load Test
 * Person 4: k6 Load Testing
 *
 * Scenarios:
 *   read_heavy  — Heavy read on incidents list
 *   write_heavy — Concurrent report submissions
 *   mixed       — Read + write combined
 *
 * Run: k6 run tests/k6/load_test.js
 * With env vars:
 *   k6 run -e BASE_URL=http://localhost:8000 -e TOKEN=<jwt> tests/k6/load_test.js
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// ── Configuration ──────────────────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API      = `${BASE_URL}/api/v1`;
const TOKEN    = __ENV.TOKEN    || "replace-with-valid-jwt";

const HEADERS = {
  "Content-Type":  "application/json",
  "Authorization": `Bearer ${TOKEN}`,
};

// ── Custom Metrics ─────────────────────────────────────────────────────────
const errorRate      = new Rate("error_rate");
const reportDuration = new Trend("report_submit_duration", true);
const incidentReads  = new Counter("incident_reads_total");

// ── Test Options ───────────────────────────────────────────────────────────
export const options = {
  scenarios: {
    // 1. Heavy read: simulate many users reading incident data
    read_heavy: {
      executor:    "ramping-vus",
      startVUs:    0,
      stages: [
        { duration: "30s", target: 20 },   // ramp up
        { duration: "1m",  target: 20 },   // sustain
        { duration: "20s", target: 0  },   // ramp down
      ],
      exec: "readHeavy",
      tags: { scenario: "read_heavy" },
    },

    // 2. Write-heavy: many users submitting reports simultaneously
    write_heavy: {
      executor:    "ramping-vus",
      startTime:   "30s",   // start after read_heavy ramps up
      startVUs:    0,
      stages: [
        { duration: "20s", target: 10 },
        { duration: "1m",  target: 10 },
        { duration: "20s", target: 0  },
      ],
      exec: "writeHeavy",
      tags: { scenario: "write_heavy" },
    },

    // 3. Mixed: realistic blend of reads and writes
    mixed: {
      executor:    "constant-vus",
      vus:         15,
      duration:    "2m",
      startTime:   "1m30s",
      exec: "mixedLoad",
      tags: { scenario: "mixed" },
    },
  },

  thresholds: {
    http_req_duration:           ["p(95)<500", "p(99)<1000"],
    http_req_failed:             ["rate<0.05"],       // < 5 % errors
    error_rate:                  ["rate<0.05"],
    report_submit_duration:      ["p(95)<800"],
  },
};

// ── Helper: random Palestinian region ────────────────────────────────────
const REGIONS = ["Ramallah", "Nablus", "Hebron", "Jenin", "Tulkarm", "Bethlehem", "Jericho"];
function randomRegion() {
  return REGIONS[Math.floor(Math.random() * REGIONS.length)];
}

// ── Scenario: read_heavy ──────────────────────────────────────────────────
export function readHeavy() {
  group("read_incidents", () => {
    const region = randomRegion();
    const res = http.get(
      `${API}/incidents?region=${region}&page=1&limit=20`,
      { headers: HEADERS }
    );
    const ok = check(res, {
      "incidents status 200": (r) => r.status === 200,
      "incidents has items":  (r) => {
        try { return Array.isArray(JSON.parse(r.body)); } catch { return false; }
      },
    });
    errorRate.add(!ok);
    incidentReads.add(1);
  });

  group("read_checkpoints", () => {
    const res = http.get(
      `${API}/checkpoints?page=1&limit=20`,
      { headers: HEADERS }
    );
    check(res, { "checkpoints status 200": (r) => r.status === 200 });
  });

  sleep(1);
}

// ── Scenario: write_heavy ─────────────────────────────────────────────────
export function writeHeavy() {
  group("submit_report", () => {
    const payload = JSON.stringify({
      checkpoint_id: Math.floor(Math.random() * 10) + 1,
      category:      "delay",
      description:   `k6 load test report at ${new Date().toISOString()}`,
      severity:      "medium",
    });

    const start = Date.now();
    const res   = http.post(`${API}/reports`, payload, { headers: HEADERS });
    reportDuration.add(Date.now() - start);

    const ok = check(res, {
      "report created (201 or 200)": (r) => r.status === 201 || r.status === 200,
    });
    errorRate.add(!ok);
  });

  sleep(0.5);
}

// ── Scenario: mixed ───────────────────────────────────────────────────────
export function mixedLoad() {
  // 70 % reads, 30 % writes
  if (Math.random() < 0.7) {
    readHeavy();
  } else {
    writeHeavy();
  }
}
