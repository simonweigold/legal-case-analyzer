// Centralized backend URL resolution
// Order of precedence:
// 1. Vite env vars: import.meta.env.VITE_BACKEND_URL or VITE_API_BASE_URL
// 2. Global window.__BACKEND_URL__ (can be injected by hosting environment)
// 3. If running on localhost: use same host with port 8000
// 4. Fallback to http://localhost:8000

interface BackendConfig {
  baseUrl: string;
}

function sanitize(url: string): string {
  return url.replace(/\/$/, '');
}

export function getBackendBaseUrl(): string {
  try {
    // Vite env variables
    const viteUrl = (import.meta as any).env?.VITE_BACKEND_URL || (import.meta as any).env?.VITE_API_BASE_URL;
    if (viteUrl && typeof viteUrl === 'string') {
      return sanitize(viteUrl);
    }

    // Global override
    if (typeof window !== 'undefined' && (window as any).__BACKEND_URL__) {
      return sanitize((window as any).__BACKEND_URL__);
    }

    // Derive from current location if same-origin dev
    if (typeof window !== 'undefined' && window.location.hostname && window.location.hostname.includes('localhost')) {
      return `http://${window.location.hostname}:8000`;
    }
  } catch (e) {
    // Ignore and fallback
  }
  return 'http://localhost:8000';
}

export const backendConfig: BackendConfig = {
  baseUrl: getBackendBaseUrl(),
};

// Optional helper to rebuild at runtime (e.g., after injecting window.__BACKEND_URL__)
export function refreshBackendConfig(): void {
  backendConfig.baseUrl = getBackendBaseUrl();
}
