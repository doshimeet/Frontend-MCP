/**
 * Enterprise Application Configuration
 * Centralized environment, authentication, and corporate telemetry settings.
 * Strict boolean parser prevents auth redirect loops in headless E2E testing.
 */

function parseBoolean(val: string | undefined, defaultVal: boolean = true): boolean {
  if (val === undefined || val === '') return defaultVal;
  const lower = val.trim().toLowerCase();
  return lower === 'true' || lower === '1';
}

export interface AppConfig {
  appName: string;
  version: string;
  mode: 'internal' | 'external';
  msal: {
    enabled: boolean;
    clientId: string;
    authority: string;
    redirectUri: string;
  };
  telemetry: {
    appInsightsConnectionString: string;
    adobeReportSuiteId: string;
    enabled: boolean;
  };
}

export const appConfig: AppConfig = {
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'wbg-enterprise-portal',
  version: '1.0.0',
  mode: (process.env.NEXT_PUBLIC_APP_MODE as 'internal' | 'external') || 'internal',
  msal: {
    enabled: parseBoolean(process.env.NEXT_AZURE_MSAL_AUTH, true),
    clientId: process.env.NEXT_PUBLIC_MSAL_CLIENT_ID || '00000000-0000-0000-0000-000000000000',
    authority: process.env.NEXT_PUBLIC_MSAL_AUTHORITY || 'https://login.microsoftonline.com/common',
    redirectUri: process.env.NEXT_PUBLIC_MSAL_REDIRECT_URI || '/',
  },
  telemetry: {
    appInsightsConnectionString: process.env.NEXT_PUBLIC_APPINSIGHTS_CONNECTION_STRING || '',
    adobeReportSuiteId: process.env.NEXT_PUBLIC_ADOBE_RSID || 'wbg-global-operations',
    enabled: process.env.NODE_ENV === 'production',
  },
};
