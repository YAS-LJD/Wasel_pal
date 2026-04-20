import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// ── Configuration ──────────────────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API      = `${BASE_URL}/api/v1`;
const TOKEN    = __ENV.TOKEN || "replace-with-valid-jwt";

const HEADERS = {
  "Content-Type": "application/json",
  "Authorization": `Bearer ${TOKEN}`,
};

// ── Metrics ────────────────────────────────────────────────────────────────
const errorRate      = new Rate("error_rate");
const reportDuration = new Trend("report_submit_duration", true);
const incidentReads  = new Counter("incident_reads_total");

// ── Test Options ───────────────────────────────────────────────────────────
export const options = {
  scenarios: {
    read_heavy: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "30s", target: 15 },
        { duration: "1m", target: 15 },
        { duration: "20s", target: 0 },
      ],
      exec: "readHeavy",
    },

    write_heavy: {
      executor: "ramping-vus",
      startTime: "30s",
      startVUs: 0,
      stages: [
        { duration: "20s", target: 5 },
        { duration: "1m", target: 5 },
        { duration: "20s", target: 0 },
      ],
      exec: "writeHeavy",
    },

    mixed: {
      executor: "constant-vus",
      vus: 10,
      duration: "2m",
      startTime: "1m30s",
      exec: "mixedLoad",
    },
  },

  thresholds: {
    http_req_duration: ["p(95)<800"],
    http_req_failed: ["rate<0.1"],
    error_rate: ["rate<0.1"],
  },
};

// ── Data ───────────────────────────────────────────────────────────────────
const REGIONS = ["Ramallah", "Nablus", "Hebron", "Jenin", "Tulkarm", "Bethlehem", "Jericho"];

// ⚠️ IMPORTANT: MUST MATCH FASTAPI ENUM EXACTLY
const CATEGORIES = [
  "checkpoint",
  "road_closure",
  "delay",
  "accident",
  "weather_hazard",
  "other"
];

function randomRegion() {
  return REGIONS[Math.floor(Math.random() * REGIONS.length)];
}

function randomCategory() {
  return CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)];
}

const LOCATIONS = [
  { lat: 31.9038, lng: 35.2034 },
  { lat: 32.2211, lng: 35.2544 },
  { lat: 31.5326, lng: 35.0998 },
  { lat: 32.4647, lng: 35.2956 },
  { lat: 31.7054, lng: 35.2024 },
  { lat: 32.3198, lng: 35.0439 },
  { lat: 31.8569, lng: 35.4588 },
];

function randomLocation() {
  const base = LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)];
  return {
    latitude: base.lat + (Math.random() - 0.5) * 0.01,
    longitude: base.lng + (Math.random() - 0.5) * 0.01,
  };
}

// ── READ ───────────────────────────────────────────────────────────────────
export function readHeavy() {
  group("read_incidents", () => {
    const region = randomRegion();

    const res = http.get(
      `${API}/incidents?region=${region}&page=1&limit=20`,
      { headers: HEADERS }
    );

    const ok = check(res, {
      "status 200": (r) => r.status === 200,
    });

    errorRate.add(!ok);
    incidentReads.add(1);
  });

  group("read_checkpoints", () => {
    const res = http.get(`${API}/checkpoints?page=1&limit=20`, {
      headers: HEADERS,
    });

    check(res, {
      "checkpoints ok": (r) => r.status === 200,
    });
  });

  sleep(1);
}

// ── WRITE ──────────────────────────────────────────────────────────────────
export function writeHeavy() {
  group("submit_report", () => {
    const loc = randomLocation();

    const payload = JSON.stringify({
      latitude: loc.latitude,
      longitude: loc.longitude,
      category: randomCategory(), // ✅ FIXED ENUM MATCH
      description: `k6 load test ${Date.now()}`,
    });

    const start = Date.now();

    const res = http.post(`${API}/reports`, payload, {
      headers: HEADERS,
    });

    reportDuration.add(Date.now() - start);

    const ok = check(res, {
      "report success": (r) => r.status === 200 || r.status === 201,
    });

    errorRate.add(!ok);
  });

  sleep(1);
}

// ── MIXED ──────────────────────────────────────────────────────────────────
export function mixedLoad() {
  if (Math.random() < 0.7) {
    readHeavy();
  } else {
    writeHeavy();
  }
}