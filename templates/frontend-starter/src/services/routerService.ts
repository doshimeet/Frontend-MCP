/**
 * RouterService
 * Helper utilities for dynamic routing and navigation event dispatching.
 */

import { omnitureService } from "./omnitureService";

export const routerService = {
  navigate(url: string): void {
    if (typeof window !== "undefined") {
      omnitureService.trackAction({
        actionName: "Navigation",
        category: "User Interaction",
        label: url,
      });
      window.location.href = url;
    }
  },

  getCurrentRoute(): string {
    if (typeof window !== "undefined") {
      return window.location.pathname;
    }
    return "/";
  },
};
