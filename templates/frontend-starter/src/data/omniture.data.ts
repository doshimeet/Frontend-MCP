/**
 * Omniture & Adobe Analytics Data Contracts
 */

export interface PageViewPayload {
  pageName: string;
  channel: string;
  reportSuiteId: string;
  userRole?: string;
  timestamp?: string;
}

export interface ActionEventPayload {
  actionName: string;
  category: string;
  label?: string;
  metadata?: Record<string, any>;
}
