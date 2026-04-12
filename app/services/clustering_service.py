import math
from datetime import datetime, timedelta


def _haversine_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return distance in metres between two lat/lng points."""
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi  = math.radians(lat2 - lat1)
    dlam  = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class ClusteringService:
    MAX_DISTANCE_M  = 500          # metres
    MAX_TIME_DIFF_H = 2            # hours
    MIN_CLUSTER_SIZE = 3           # reports needed to auto-create incident

    def cluster_reports(self, reports: list[dict]) -> list[dict]:
        """
        Group reports by proximity + category + time window.
        Returns list of clusters; each cluster with size >= MIN_CLUSTER_SIZE
        should trigger an incident.
        """
        visited = [False] * len(reports)
        clusters = []

        for i, anchor in enumerate(reports):
            if visited[i]:
                continue

            cluster = [anchor]
            visited[i] = True
            anchor_time = anchor.get("created_at") or datetime.utcnow()

            for j, candidate in enumerate(reports):
                if visited[j] or i == j:
                    continue

                # Must be same category
                if candidate.get("category") != anchor.get("category"):
                    continue

                # Must be within 2 hours
                cand_time = candidate.get("created_at") or datetime.utcnow()
                if abs((cand_time - anchor_time).total_seconds()) > self.MAX_TIME_DIFF_H * 3600:
                    continue

                # Must be within 500 metres
                dist = _haversine_meters(
                    anchor["latitude"], anchor["longitude"],
                    candidate["latitude"], candidate["longitude"],
                )
                if dist <= self.MAX_DISTANCE_M:
                    cluster.append(candidate)
                    visited[j] = True

            clusters.append({
                "reports": cluster,
                "size": len(cluster),
                "should_create_incident": len(cluster) >= self.MIN_CLUSTER_SIZE,
                "category": anchor.get("category"),
                "latitude": anchor["latitude"],
                "longitude": anchor["longitude"],
            })

        return clusters