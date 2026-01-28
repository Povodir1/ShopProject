/**
 * LocalStorage Wrapper
 * Handles storage with expiration support
 */

import config from '../config.js';

/**
 * Storage wrapper with TTL support
 */
class Storage {
  constructor() {
    this.prefix = config.storage?.prefix || 'shop_';
    this.storage = window.localStorage;
  }

  /**
   * Get full key with prefix
   * @param {string} key - Storage key
   * @returns {string} Full key with prefix
   */
  getKey(key) {
    return `${this.prefix}${key}`;
  }

  /**
   * Set value in storage with optional expiration
   * @param {string} key - Storage key
   * @param {*} value - Value to store (will be JSON stringified)
   * @param {number} ttl - Time to live in milliseconds
   */
  set(key, value, ttl = null) {
    try {
      const fullKey = this.getKey(key);
      const item = {
        value: JSON.stringify(value),
        expires: ttl ? Date.now() + ttl : null
      };

      this.storage.setItem(fullKey, JSON.stringify(item));
      return true;
    } catch (error) {
      console.error('Storage set error:', error);
      return false;
    }
  }

  /**
   * Get value from storage
   * @param {string} key - Storage key
   * @param {*} defaultValue - Default value if key doesn't exist or expired
   * @returns {*} Stored value or default
   */
  get(key, defaultValue = null) {
    try {
      const fullKey = this.getKey(key);
      const item = this.storage.getItem(fullKey);

      if (!item) {
        return defaultValue;
      }

      const parsed = JSON.parse(item);

      // Check expiration
      if (parsed.expires && parsed.expires < Date.now()) {
        this.remove(key);
        return defaultValue;
      }

      return JSON.parse(parsed.value);
    } catch (error) {
      console.error('Storage get error:', error);
      return defaultValue;
    }
  }

  /**
   * Remove value from storage
   * @param {string} key - Storage key
   * @returns {boolean} Success status
   */
  remove(key) {
    try {
      const fullKey = this.getKey(key);
      this.storage.removeItem(fullKey);
      return true;
    } catch (error) {
      console.error('Storage remove error:', error);
      return false;
    }
  }

  /**
   * Check if key exists and is not expired
   * @param {string} key - Storage key
   * @returns {boolean} True if key exists and is valid
   */
  has(key) {
    return this.get(key) !== null;
  }

  /**
   * Clear all items with prefix or specific key
   * @param {string} key - Optional specific key to clear
   */
  clear(key = null) {
    try {
      if (key) {
        this.remove(key);
        return;
      }

      // Clear all items with prefix
      const keys = Object.keys(this.storage);
      keys.forEach(k => {
        if (k.startsWith(this.prefix)) {
          this.storage.removeItem(k);
        }
      });
    } catch (error) {
      console.error('Storage clear error:', error);
    }
  }

  /**
   * Get all keys with prefix
   * @returns {string[]} Array of keys (without prefix)
   */
  keys() {
    try {
      const allKeys = Object.keys(this.storage);
      return allKeys
        .filter(k => k.startsWith(this.prefix))
        .map(k => k.replace(this.prefix, ''));
    } catch (error) {
      console.error('Storage keys error:', error);
      return [];
    }
  }

  /**
   * Get storage size in bytes
   * @returns {number} Size in bytes
   */
  getSize() {
    try {
      let total = 0;
      const keys = Object.keys(this.storage);

      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          total += this.storage.getItem(key).length + key.length;
        }
      });

      return total;
    } catch (error) {
      console.error('Storage size error:', error);
      return 0;
    }
  }

  /**
   * Check if storage is available
   * @returns {boolean} True if storage is available
   */
  isAvailable() {
    try {
      const testKey = '__storage_test__';
      this.storage.setItem(testKey, 'test');
      this.storage.removeItem(testKey);
      return true;
    } catch (error) {
      return false;
    }
  }
}

// Session Storage wrapper
class SessionStorage {
  constructor() {
    this.prefix = 'shop_';
    this.storage = window.sessionStorage;
  }

  getKey(key) {
    return `${this.prefix}${key}`;
  }

  set(key, value) {
    try {
      const fullKey = this.getKey(key);
      this.storage.setItem(fullKey, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('SessionStorage set error:', error);
      return false;
    }
  }

  get(key, defaultValue = null) {
    try {
      const fullKey = this.getKey(key);
      const item = this.storage.getItem(fullKey);

      if (!item) {
        return defaultValue;
      }

      return JSON.parse(item);
    } catch (error) {
      console.error('SessionStorage get error:', error);
      return defaultValue;
    }
  }

  remove(key) {
    try {
      const fullKey = this.getKey(key);
      this.storage.removeItem(fullKey);
      return true;
    } catch (error) {
      console.error('SessionStorage remove error:', error);
      return false;
    }
  }

  has(key) {
    return this.get(key) !== null;
  }

  clear(key = null) {
    try {
      if (key) {
        this.remove(key);
        return;
      }

      const keys = Object.keys(this.storage);
      keys.forEach(k => {
        if (k.startsWith(this.prefix)) {
          this.storage.removeItem(k);
        }
      });
    } catch (error) {
      console.error('SessionStorage clear error:', error);
    }
  }

  isAvailable() {
    try {
      const testKey = '__session_test__';
      this.storage.setItem(testKey, 'test');
      this.storage.removeItem(testKey);
      return true;
    } catch (error) {
      return false;
    }
  }
}

// Create and export singleton instances
const storage = new Storage();
const sessionStorage = new SessionStorage();

export default storage;
export { sessionStorage };
