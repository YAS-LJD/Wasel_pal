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

const errorRate     = new Rate("soak_error_rate");
const p95Trend      = new Trend("soak_p95_duration", true);
const totalRequests = new Counter("soak_total_requests");

export const options = {
  scenarios: {
    soak: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "2m30s", target: 20 },
        { duration: "30m",   target: 20 },
        { duration: "2m30s", target: 0  },
      ],
      gracefulRampDown: "30s",
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<600", "p(99)<1200"],
    http_req_failed:   ["rate<0.02"],
    soak_error_rate:   ["rate<0.02"],
  },
};

const REGIONS    = ["Ramallah", "Nablus", "Hebron", "Jenin", "Tulkarm", "Bethlehem"];
const CATEGORIES = ["delay", "closure", "accident", "other"];
const SEVERITIES = ["low", "medium", "high"];

function randomItem(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randomId(max = 10) { return Math.floor(Math.random() * max) + 1; }

export default function () {
  const region = randomItem(REGIONS);
  const roll   = Math.random();

  if (roll < 0.30) {
    group("read_incidents", () => {
      const start = Date.now();
      const res = http.get(`${API}/incidents?region=${region}&page=1&limit=10`, { headers: HEADERS });
      p95Trend.add(Date.now() - start);
      totalRequests.add(1);
      const ok = check(res, { "incidents 200": (r) => r.status === 200 });
      errorRate.add(!ok);
    });
  } else if (roll < 0.55) {
    group("read_checkpoints", () => {
      const start = Date.now();
      const res = http.get(`${API}/checkpoints?region=${region}&limit=10`, { headers: HEADERS });
      p95Trend.add(Date.now() - start);
      totalRequests.add(1);
      const ok = check(res, { "checkpoints 200": (r) => r.status === 200 });
      errorRate.add(!ok);
    });
  } else if (roll < 0.70) {
    group("read_stats", () => {
      const res = http.get(`${API}/stats/checkpoints`, { headers: HEADERS });
      totalRequests.add(1);
      const ok = check(res, { "stats 200": (r) => r.status === 200 });
      errorRate.add(!ok);
    });
  } else if (roll < 0.85) {
    group("submit_report", () => {
      const payload = JSON.stringify({
        latitude:    31.9 + (Math.random() - 0.5) * 0.1,
        longitude:   35.2 + (Math.random() - 0.5) * 0.1,
        category:    randomItem(CATEGORIES),
        description: `Soak test report — ${new Date().toISOString()}`,
      });
      const start = Date.now();
      const res = http.post(`${API}/reports`, payload, { headers: HEADERS });
      p95Trend.add(Date.now() - start);
      totalRequests.add(1);
      const ok = check(res, { "report 201/200": (r) => r.status === 200 || r.status === 201 });
      errorRate.add(!ok);
    });
  } else if (roll < 0.93) {
    group("weather_api", () => {
      const res = http.get(`${API}/external/weather/${region}`, { headers: HEADERS });
      totalRequests.add(1);
      const ok = check(res, { "weather not 5xx": (r) => r.status < 500 });
      errorRate.add(!ok);
    });
  } else {
    group("predict_region", () => {
      const res = http.get(`${API}/predict/region/${region}`, { headers: HEADERS });
      totalRequests.add(1);
      const ok = check(res, { "predict not 5xx": (r) => r.status < 500 });
      errorRate.add(!ok);
    });
  }

  sleep(1 + Math.random() * 2);
}

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

  return { stdout: JSON.stringify(data, null, 2) };
}