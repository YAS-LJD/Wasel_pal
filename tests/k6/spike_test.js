/**
 * tests/k6/spike_test.js — Spike Test
 * Person 4: k6 Load Testing
 *
 * Simulates 100 users hitting the API simultaneously (sudden spike).
 * Tests how the system behaves under sudden extreme load.
 *
 * Run: k6 run tests/k6/spike_test.js
 */

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API      = `${BASE_URL}/api/v1`;
const TOKEN    = __ENV.TOKEN    || "replace-with-valid-jwt";

const HEADERS = {
  "Content-Type":  "application/json",
  "Authorization": `Bearer ${TOKEN}`,
};

const errorRate       = new Rate("spike_error_rate");
const recoveryTrend   = new Trend("spike_recovery_ms", true);

export const options = {
  scenarios: {
    spike: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "10s", target: 5   },   // baseline
        { duration: "5s",  target: 100 },   // sudden spike → 100 users
        { duration: "30s", target: 100 },   // hold the spike
        { duration: "10s", target: 5   },   // drop back to baseline
        { duration: "30s", target: 5   },   // observe recovery
        { duration: "5s",  target: 0   },   // done
      ],
    },
  },

  thresholds: {
    http_req_duration:  ["p(95)<2000"],    // allow up to 2 s under spike
    http_req_failed:    ["rate<0.10"],     // allow up to 10 % errors during spike
    spike_error_rate:   ["rate<0.10"],
  },
};

const REGIONS = ["Ramallah", "Nablus", "Hebron", "Jenin"];

export default function () {
  const region = REGIONS[Math.floor(Math.random() * REGIONS.length)];

  // Mix of the heaviest read endpoints
  group("spike_reads", () => {
    const start = Date.now();

    const responses = http.batch([
      ["GET", `${API}/incidents?region=${region}&limit=20`,   null, { headers: HEADERS }],
      ["GET", `${API}/checkpoints?region=${region}&limit=20`, null, { headers: HEADERS }],
      ["GET", `${API}/stats/checkpoints`,                     null, { headers: HEADERS }],
    ]);

    recoveryTrend.add(Date.now() - start);

    responses.forEach((res, i) => {
      const ok = check(res, {
        [`batch[${i}] not 5xx`]: (r) => r.status < 500,
      });
      errorRate.add(!ok);
    });
  });

  // Some users also try to post reports during the spike
  if (Math.random() < 0.3) {
    group("spike_write", () => {
      const payload = JSON.stringify({
        checkpoint_id: Math.floor(Math.random() * 10) + 1,
        category:      "closure",
        description:   "Spike test report",
        severity:      "high",
      });
      const res = http.post(`${API}/reports`, payload, { headers: HEADERS });
      check(res, { "spike write not 5xx": (r) => r.status < 500 });
    });
  }

  sleep(Math.random() * 0.5);   // 0–500 ms think time
}
