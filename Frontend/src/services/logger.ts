/**
 * Logger Service
 * Logs all user actions to the backend for audit trails
 */

const API_BASE_URL = "https://climasense-production.up.railway.app";

export const loggerService = {
  /**
   * Log a user action
   * @param action - Action name (e.g., "city_selected", "prediction_made")
   * @param details - Additional details about the action
   * @param userId - Optional user ID
   */
  async logAction(
    action: string,
    details?: Record<string, any>,
    userId?: number
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/log-action`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          action,
          details: JSON.stringify(details || {}),
          user_id: userId,
        }),
      });

      if (!response.ok) {
        console.warn("Failed to log action:", action);
      }
    } catch (error) {
      console.error("Error logging action:", error);
      // Don't throw - logging failures shouldn't break the app
    }
  },

  /**
   * Log page view
   */
  logPageView(page: string, userId?: number): Promise<void> {
    return this.logAction("page_viewed", { page }, userId);
  },

  /**
   * Log city selection
   */
  logCitySelected(city: string, userId?: number): Promise<void> {
    return this.logAction("city_selected", { city }, userId);
  },

  /**
   * Log mode change
   */
  logModeChanged(mode: string, userId?: number): Promise<void> {
    return this.logAction("mode_changed", { mode }, userId);
  },

  /**
   * Log comparison
   */
  logComparison(city1: string, city2: string, mode: string, userId?: number): Promise<void> {
    return this.logAction("cities_compared", { city1, city2, mode }, userId);
  },

  /**
   * Log anomaly detection
   */
  logAnomalyDetection(city: string, userId?: number): Promise<void> {
    return this.logAction("anomaly_checked", { city }, userId);
  },

  /**
   * Log forecast
   */
  logForecast(city: string, days: number, userId?: number): Promise<void> {
    return this.logAction("forecast_generated", { city, days }, userId);
  },

  /**
   * Log data download
   */
  logDownload(type: string, userId?: number): Promise<void> {
    return this.logAction("data_downloaded", { type }, userId);
  },

  /**
   *Log filter applied
   */
  logFilterApplied(filter: string, value: any, userId?: number): Promise<void> {
    return this.logAction("filter_applied", { filter, value }, userId);
  },
};
