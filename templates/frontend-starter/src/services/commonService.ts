/**
 * CommonService
 * Reusable HTTP utilities, API error wrappers, and data transformations.
 */

import { loggerService } from "./LoggerService";

export class ApiError extends Error {
  constructor(public statusCode: number, message: string, public details?: any) {
    super(message);
    this.name = "ApiError";
  }
}

export const commonService = {
  async get<T>(url: string, headers: Record<string, string> = {}): Promise<T> {
    try {
      const response = await fetch(url, { headers });
      if (!response.ok) {
        throw new ApiError(response.status, `Request to ${url} failed with status ${response.status}`);
      }
      return (await response.json()) as T;
    } catch (error) {
      loggerService.error(`[CommonService] GET ${url} error`, error);
      throw error;
    }
  },

  async post<T>(url: string, body: any, headers: Record<string, string> = {}): Promise<T> {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...headers },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        throw new ApiError(response.status, `POST to ${url} failed with status ${response.status}`);
      }
      return (await response.json()) as T;
    } catch (error) {
      loggerService.error(`[CommonService] POST ${url} error`, error);
      throw error;
    }
  },
};
