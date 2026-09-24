/**
 * LoggerService
 * Standardized corporate logging with severity levels and metadata tracking.
 */

type LogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR";

class LoggerService {
  private formatMessage(level: LogLevel, message: string, meta?: any): string {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level}] ${message} ${meta ? JSON.stringify(meta) : ""}`;
  }

  debug(message: string, meta?: any): void {
    if (process.env.NODE_ENV !== "production") {
      console.debug(this.formatMessage("DEBUG", message, meta));
    }
  }

  info(message: string, meta?: any): void {
    console.info(this.formatMessage("INFO", message, meta));
  }

  warn(message: string, meta?: any): void {
    console.warn(this.formatMessage("WARN", message, meta));
  }

  error(message: string, error?: any): void {
    console.error(this.formatMessage("ERROR", message, error));
  }
}

export const loggerService = new LoggerService();
