/**
 * Formatters
 * Utility functions for formatting display values
 */

import config from '../config.js';

/**
 * Format price with currency
 * @param {number} price - Price value
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted price
 */
export function formatPrice(price, currency = null) {
  const currencyCode = currency || config.currency.default;
  const locale = config.currency.locale;

  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  } catch (error) {
    console.error('Price format error:', error);
    return `${currencyCode} ${price.toFixed(2)}`;
  }
}

/**
 * Format date to locale string
 * @param {Date|string|number} date - Date to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date
 */
export function formatDate(date, options = {}) {
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  };

  const mergedOptions = { ...defaultOptions, ...options };

  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    return new Intl.DateTimeFormat(config.currency.locale, mergedOptions).format(dateObj);
  } catch (error) {
    console.error('Date format error:', error);
    return String(date);
  }
}

/**
 * Format date and time
 * @param {Date|string|number} date - Date to format
 * @returns {string} Formatted date and time
 */
export function formatDateTime(date) {
  return formatDate(date, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Format relative time (e.g., "2 hours ago")
 * @param {Date|string|number} date - Date to format
 * @returns {string} Relative time string
 */
export function formatRelativeTime(date) {
  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    const now = new Date();
    const diffMs = now - dateObj;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) {
      return 'just now';
    } else if (diffMins < 60) {
      return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      return formatDate(dateObj);
    }
  } catch (error) {
    console.error('Relative time format error:', error);
    return String(date);
  }
}

/**
 * Truncate text to max length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @param {string} suffix - Suffix to add (default: '...')
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength, suffix = '...') {
  if (!text || text.length <= maxLength) {
    return text || '';
  }

  return text.substr(0, maxLength - suffix.length) + suffix;
}

/**
 * Format number with thousands separator
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export function formatNumber(num) {
  try {
    return new Intl.NumberFormat(config.currency.locale).format(num);
  } catch (error) {
    console.error('Number format error:', error);
    return String(num);
  }
}

/**
 * Format percentage
 * @param {number} value - Value (0-100)
 * @param {number} decimals - Decimal places
 * @returns {string} Formatted percentage
 */
export function formatPercentage(value, decimals = 1) {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Format file size
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size
 */
export function formatFileSize(bytes) {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(unitIndex === 0 ? 0 : 2)} ${units[unitIndex]}`;
}

/**
 * Format quantity
 * @param {number} quantity - Quantity value
 * @returns {string} Formatted quantity
 */
export function formatQuantity(quantity) {
  return formatNumber(quantity);
}

/**
 * Format stock status
 * @param {number} stock - Stock quantity
 * @param {boolean} isAvailable - Availability flag
 * @returns {string} Stock status text
 */
export function formatStockStatus(stock, isAvailable) {
  if (!isAvailable) {
    return 'Unavailable';
  }

  if (stock === 0) {
    return 'Out of stock';
  }

  if (stock < 10) {
    return `Only ${stock} left`;
  }

  return 'In stock';
}

/**
 * Pluralize word based on count
 * @param {number} count - Count value
 * @param {string} singular - Singular form
 * @param {string} plural - Plural form
 * @returns {string} Correct form
 */
export function pluralize(count, singular, plural = null) {
  if (count === 1) {
    return singular;
  }
  return plural || `${singular}s`;
}

/**
 * Format a list of items
 * @param {Array} items - Array of items
 * @param {string} conjunction - Conjunction (default: 'and')
 * @returns {string} Formatted list
 */
export function formatList(items, conjunction = 'and') {
  if (!items || items.length === 0) {
    return '';
  }

  if (items.length === 1) {
    return String(items[0]);
  }

  if (items.length === 2) {
    return `${items[0]} ${conjunction} ${items[1]}`;
  }

  const allButLast = items.slice(0, -1).join(', ');
  const last = items[items.length - 1];

  return `${allButLast}, ${conjunction} ${last}`;
}

// Export all formatters as object
const formatters = {
  formatPrice,
  formatDate,
  formatDateTime,
  formatRelativeTime,
  truncateText,
  formatNumber,
  formatPercentage,
  formatFileSize,
  formatQuantity,
  formatStockStatus,
  pluralize,
  formatList
};

export default formatters;
