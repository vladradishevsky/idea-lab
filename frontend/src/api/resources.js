import { apiRequest } from "./client";

export function getApiRoot(options) {
  return apiRequest("/api/", options);
}

export function getHealthStatus(options) {
  return apiRequest("/api/health/", options);
}

export function getSourceSystems(options) {
  return apiRequest("/api/source-systems/", options);
}
