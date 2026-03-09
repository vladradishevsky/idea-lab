import { apiRequest } from "./client";

export function getApiRoot(options) {
  return apiRequest("/api/", options);
}

export function getDashboardAggregates(options) {
  return apiRequest("/api/dashboard/aggregates/", options);
}

export function getHealthStatus(options) {
  return apiRequest("/api/health/", options);
}

export function getStages(query = {}, options) {
  const searchParams = new URLSearchParams();

  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }

    searchParams.set(key, String(value));
  });

  const suffix = searchParams.toString() ? `?${searchParams.toString()}` : "";
  return apiRequest(`/api/stages/${suffix}`, options);
}

export function getNextQuickFilterStage(options) {
  return getStages({ page_size: 1 }, options);
}

export function getSourceSystems(options) {
  return apiRequest("/api/source-systems/", options);
}
