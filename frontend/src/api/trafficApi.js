// Centralized API layer for frontend-backend communication.
// Keeps the backend base URL in one place and exposes reusable request helpers.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

function buildUrl(endpoint) {
  return `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
}

async function request(endpoint, options = {}) {
  try {
    const response = await fetch(buildUrl(endpoint), options);

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const message =
        typeof payload === "object" && payload && payload.message
          ? payload.message
          : `Request failed with status ${response.status}`;

      throw new Error(message);
    }

    return payload;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }

    throw new Error("An unexpected API error occurred.");
  }
}

// Fetch the current dashboard state from the backend.
export async function getDashboard() {
  return request("/dashboard", {
    method: "GET",
  });
}

// Check whether the backend is running.
export async function getHealth() {
  return request("/health", {
    method: "GET",
  });
}

// Upload one or more videos to the backend.
export async function uploadVideo(formData) {
  return request("/upload", {
    method: "POST",
    body: formData,
  });
}

// Fetch historical analytics from the backend.
export async function getAnalyticsHistory(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/analytics/history${query ? `?${query}` : ""}`, {
    method: "GET",
  });
}

export async function getAnalyticsToday(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/analytics/today${query ? `?${query}` : ""}`, {
    method: "GET",
  });
}

export async function getAnalyticsWeekly(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/analytics/weekly${query ? `?${query}` : ""}`, {
    method: "GET",
  });
}

export async function getAnalyticsMonthly(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/analytics/monthly${query ? `?${query}` : ""}`, {
    method: "GET",
  });
}

export async function exportAnalyticsReport(format, range = "today") {
  const response = await fetch(buildUrl(`/reports/${format}?range=${range}`), {
    method: "GET",
    headers: {
      Accept: format === "pdf" ? "application/pdf" : "text/csv",
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Unable to export ${format.toUpperCase()} report.`);
  }

  const contentDisposition = response.headers.get("content-disposition") || "";
  const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
  const blob = await response.blob();

  return {
    blob,
    filename: filenameMatch?.[1] || `traffic-report-${range}.${format}`,
    contentType: response.headers.get("content-type") || (format === "pdf" ? "application/pdf" : "text/csv"),
  };
}
