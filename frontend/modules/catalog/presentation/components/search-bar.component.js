/**
 * Search Bar Component
 * Product search input with debounce
 */

import eventBus from '/core/event-bus.js';
import config from '/core/config.js';
import storage from '/core/shared/storage.js';

export class SearchBarComponent {
  /**
   * @param {HTMLElement} container - Container element
   * @param {Object} options - Component options
   */
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      placeholder: 'Search products...',
      debounceDelay: config.ui.searchDebounceDelay,
      showRecentSearches: true,
      ...options
    };
    this.element = null;
    this.searchInput = null;
    this.debounceTimer = null;
    this.recentSearches = this.loadRecentSearches();
  }

  /**
   * Render the search bar
   * @returns {HTMLElement} Search bar element
   */
  render() {
    const wrapper = document.createElement('div');
    wrapper.className = 'search-bar';

    const form = document.createElement('form');
    form.className = 'search-bar-form';
    form.setAttribute('role', 'search');

    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group';

    const searchIcon = this.createSearchIcon();

    this.searchInput = document.createElement('input');
    this.searchInput.type = 'search';
    this.searchInput.className = 'input search-bar-input';
    this.searchInput.placeholder = this.options.placeholder;
    this.searchInput.setAttribute('aria-label', 'Search products');
    this.searchInput.autocomplete = 'off';

    const clearButton = this.createClearButton();
    const submitButton = this.createSubmitButton();

    inputGroup.appendChild(searchIcon);
    inputGroup.appendChild(this.searchInput);
    inputGroup.appendChild(clearButton);
    inputGroup.appendChild(submitButton);

    form.appendChild(inputGroup);
    wrapper.appendChild(form);

    // Add recent searches dropdown
    if (this.options.showRecentSearches) {
      const recentDropdown = this.createRecentSearchesDropdown();
      wrapper.appendChild(recentDropdown);
    }

    this.attachEventListeners(form);
    this.element = wrapper;
    return wrapper;
  }

  /**
   * Create search icon
   * @returns {HTMLElement} SVG icon
   */
  createSearchIcon() {
    const wrapper = document.createElement('span');
    wrapper.className = 'search-bar-icon';
    wrapper.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.35-4.35"></path>
      </svg>
    `;
    return wrapper;
  }

  /**
   * Create clear button
   * @returns {HTMLElement} Button element
   */
  createClearButton() {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn-icon search-bar-clear';
    button.style.display = 'none';
    button.setAttribute('aria-label', 'Clear search');
    button.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    `;
    return button;
  }

  /**
   * Create submit button
   * @returns {HTMLElement} Button element
   */
  createSubmitButton() {
    const button = document.createElement('button');
    button.type = 'submit';
    button.className = 'btn btn-primary search-bar-submit';
    button.setAttribute('aria-label', 'Search');
    button.innerHTML = 'Search';
    return button;
  }

  /**
   * Create recent searches dropdown
   * @returns {HTMLElement} Dropdown element
   */
  createRecentSearchesDropdown() {
    const dropdown = document.createElement('div');
    dropdown.className = 'search-bar-recent';
    dropdown.style.display = 'none';

    const list = document.createElement('ul');
    list.className = 'search-bar-recent-list';

    if (this.recentSearches.length > 0) {
      this.recentSearches.forEach(query => {
        const item = document.createElement('li');
        item.className = 'search-bar-recent-item';

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'search-bar-recent-button';
        button.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          <span>${this.escapeHtml(query)}</span>
        `;
        button.addEventListener('click', () => this.performSearch(query));

        item.appendChild(button);
        list.appendChild(item);
      });
    }

    dropdown.appendChild(list);
    return dropdown;
  }

  /**
   * Attach event listeners
   * @param {HTMLElement} form - Form element
   */
  attachEventListeners(form) {
    // Form submit
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const query = this.searchInput.value.trim();
      if (query) {
        this.performSearch(query);
      }
    });

    // Input change (debounced)
    this.searchInput.addEventListener('input', () => {
      this.onInputChange();
    });

    // Clear button
    const clearBtn = form.querySelector('.search-bar-clear');
    clearBtn.addEventListener('click', () => {
      this.clear();
    });

    // Focus/blur for recent searches
    this.searchInput.addEventListener('focus', () => {
      this.showRecentSearches();
    });

    this.searchInput.addEventListener('blur', () => {
      // Delay hiding to allow clicking on recent items
      setTimeout(() => {
        this.hideRecentSearches();
      }, 200);
    });
  }

  /**
   * Handle input change with debounce
   */
  onInputChange() {
    const value = this.searchInput.value;
    const clearBtn = this.element.querySelector('.search-bar-clear');

    // Show/hide clear button
    clearBtn.style.display = value ? 'flex' : 'none';

    // Debounce search
    clearTimeout(this.debounceTimer);

    if (value.trim().length >= 2) {
      this.debounceTimer = setTimeout(() => {
        this.performSearch(value.trim());
      }, this.options.debounceDelay);
    } else if (value.trim().length === 0) {
      // Clear search if input is empty
      this.onSearch('');
    }
  }

  /**
   * Perform search
   * @param {string} query - Search query
   */
  performSearch(query) {
    if (!query || query.trim().length < 2) {
      return;
    }

    // Update input value
    this.searchInput.value = query;

    // Save to recent searches
    this.addToRecentSearches(query);

    // Hide recent searches
    this.hideRecentSearches();

    // Publish search event
    this.onSearch(query);
  }

  /**
   * Handle search
   * @param {string} query - Search query
   */
  onSearch(query) {
    eventBus.publish('catalog:search', {
      query: query || null
    });
  }

  /**
   * Add query to recent searches
   * @param {string} query - Search query
   */
  addToRecentSearches(query) {
    // Remove if already exists
    const index = this.recentSearches.indexOf(query);
    if (index > -1) {
      this.recentSearches.splice(index, 1);
    }

    // Add to beginning
    this.recentSearches.unshift(query);

    // Keep only last 10
    this.recentSearches = this.recentSearches.slice(0, 10);

    // Save to storage
    storage.set('search_history', this.recentSearches);

    // Update dropdown
    this.updateRecentSearchesDropdown();
  }

  /**
   * Load recent searches from storage
   * @returns {Array} Recent searches
   */
  loadRecentSearches() {
    return storage.get('search_history', []);
  }

  /**
   * Show recent searches dropdown
   */
  showRecentSearches() {
    const dropdown = this.element.querySelector('.search-bar-recent');
    const hasValue = this.searchInput.value.trim().length > 0;

    if (dropdown && this.recentSearches.length > 0 && !hasValue) {
      dropdown.style.display = 'block';
    }
  }

  /**
   * Hide recent searches dropdown
   */
  hideRecentSearches() {
    const dropdown = this.element.querySelector('.search-bar-recent');
    if (dropdown) {
      dropdown.style.display = 'none';
    }
  }

  /**
   * Update recent searches dropdown
   */
  updateRecentSearchesDropdown() {
    const oldDropdown = this.element.querySelector('.search-bar-recent');
    if (oldDropdown) {
      oldDropdown.remove();
    }

    const newDropdown = this.createRecentSearchesDropdown();
    this.element.appendChild(newDropdown);
  }

  /**
   * Clear search input
   */
  clear() {
    this.searchInput.value = '';
    this.searchInput.focus();
    this.onInputChange();
    this.onSearch('');
  }

  /**
   * Focus on search input
   */
  focus() {
    if (this.searchInput) {
      this.searchInput.focus();
    }
  }

  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Destroy the component
   */
  destroy() {
    clearTimeout(this.debounceTimer);

    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }

    this.element = null;
    this.searchInput = null;
  }
}

export default SearchBarComponent;
