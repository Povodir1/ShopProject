/**
 * Event Bus
 * Publisher/Subscriber pattern for module communication
 * Modules communicate without direct dependencies
 */

class EventBus {
  constructor() {
    // Map of event name -> Set of callbacks
    this.events = new Map();
  }

  /**
   * Subscribe to an event
   * @param {string} eventName - Name of the event
   * @param {Function} callback - Function to call when event is published
   * @returns {Function} Unsubscribe function
   */
  subscribe(eventName, callback) {
    if (!eventName || typeof eventName !== 'string') {
      throw new Error('Event name is required and must be a string');
    }

    if (typeof callback !== 'function') {
      throw new Error('Callback must be a function');
    }

    // Get or create event listeners set
    if (!this.events.has(eventName)) {
      this.events.set(eventName, new Set());
    }

    const listeners = this.events.get(eventName);
    listeners.add(callback);

    // Return unsubscribe function
    return () => {
      this.unsubscribe(eventName, callback);
    };
  }

  /**
   * Unsubscribe from an event
   * @param {string} eventName - Name of the event
   * @param {Function} callback - Function to remove
   */
  unsubscribe(eventName, callback) {
    if (!this.events.has(eventName)) {
      return;
    }

    const listeners = this.events.get(eventName);
    listeners.delete(callback);

    // Clean up empty events
    if (listeners.size === 0) {
      this.events.delete(eventName);
    }
  }

  /**
   * Publish an event
   * @param {string} eventName - Name of the event
   * @param {*} data - Data to pass to subscribers
   */
  publish(eventName, data = null) {
    if (!this.events.has(eventName)) {
      return;
    }

    const listeners = this.events.get(eventName);

    // Create a copy to avoid issues if callbacks modify the set
    const listenersCopy = Array.from(listeners);

    for (const callback of listenersCopy) {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in event listener for "${eventName}":`, error);
      }
    }
  }

  /**
   * Subscribe to an event only once
   * @param {string} eventName - Name of the event
   * @param {Function} callback - Function to call once
   * @returns {Function} Unsubscribe function
   */
  once(eventName, callback) {
    const wrappedCallback = (data) => {
      callback(data);
      this.unsubscribe(eventName, wrappedCallback);
    };

    return this.subscribe(eventName, wrappedCallback);
  }

  /**
   * Clear all listeners for an event or all events
   * @param {string} eventName - Optional event name to clear
   */
  clear(eventName = null) {
    if (eventName) {
      this.events.delete(eventName);
    } else {
      this.events.clear();
    }
  }

  /**
   * Get the number of listeners for an event
   * @param {string} eventName - Name of the event
   * @returns {number} Number of listeners
   */
  listenerCount(eventName) {
    if (!this.events.has(eventName)) {
      return 0;
    }
    return this.events.get(eventName).size;
  }

  /**
   * Get all registered event names
   * @returns {string[]} Array of event names
   */
  getEventNames() {
    return Array.from(this.events.keys());
  }
}

// Create and export singleton instance
const eventBus = new EventBus();

export default eventBus;
