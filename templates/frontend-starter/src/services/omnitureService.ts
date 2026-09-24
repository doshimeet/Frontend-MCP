/**
 * OmnitureService
 * Corporate event tracking service for Adobe Analytics.
 */

import { PageViewPayload, ActionEventPayload } from "../data/omniture.data";
import { loggerService } from "./LoggerService";

class OmnitureService {
  trackPageView(payload: PageViewPayload): void {
    loggerService.info("[AdobeAnalytics] PageView", payload);
    // In production, dispatches to window.s.t()
    if (typeof window !== "undefined" && (window as any).s) {
      try {
        (window as any).s.pageName = payload.pageName;
        (window as any).s.channel = payload.channel;
        (window as any).s.t();
      } catch (err) {
        loggerService.warn("Omniture tracking error", err);
      }
    }
  }

  trackAction(payload: ActionEventPayload): void {
    loggerService.info("[AdobeAnalytics] Action", payload);
    // In production, dispatches to window.s.tl()
    if (typeof window !== "undefined" && (window as any).s) {
      try {
        (window as any).s.tl(true, "o", payload.actionName);
      } catch (err) {
        loggerService.warn("Omniture action error", err);
      }
    }
  }
}

export const omnitureService = new OmnitureService();
