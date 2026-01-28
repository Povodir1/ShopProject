/**
 * Category Tree Component
 * Displays category tree navigation
 */

import eventBus from '/core/event-bus.js';

export class CategoryTreeComponent {
  /**
   * @param {Array<Category>} categories - Category tree
   * @param {HTMLElement} container - Container element
   * @param {Object} options - Component options
   */
  constructor(categories, container, options = {}) {
    this.categories = categories;
    this.container = container;
    this.options = {
      selectedCategoryId: null,
      expandAll: false,
      showProductCount: false,
      ...options
    };
    this.element = null;
    this.expandedCategories = new Set();
  }

  /**
   * Render the category tree
   * @returns {HTMLElement} Tree element
   */
  render() {
    const wrapper = document.createElement('div');
    wrapper.className = 'category-tree';

    if (this.categories.length === 0) {
      wrapper.innerHTML = '<p class="text-muted body-small">No categories available</p>';
      this.element = wrapper;
      return wrapper;
    }

    const list = document.createElement('ul');
    list.className = 'category-tree-list';
    list.setAttribute('role', 'tree');

    this.categories.forEach(category => {
      list.appendChild(this.renderCategory(category, 0));
    });

    // Add "All Categories" option at the top
    const allItem = this.renderAllCategoriesItem();
    list.insertBefore(allItem, list.firstChild);

    wrapper.appendChild(list);

    // Add clear filter button if category is selected
    if (this.options.selectedCategoryId) {
      const clearBtn = this.renderClearButton();
      wrapper.appendChild(clearBtn);
    }

    this.attachEventListeners(wrapper);
    this.element = wrapper;
    return wrapper;
  }

  /**
   * Render "All Categories" item
   * @returns {HTMLElement} List item
   */
  renderAllCategoriesItem() {
    const li = document.createElement('li');
    li.className = 'category-tree-item';

    const button = document.createElement('button');
    button.className = `category-tree-button ${!this.options.selectedCategoryId ? 'active' : ''}`;
    button.setAttribute('role', 'treeitem');
    button.setAttribute('data-category-id', '');
    button.innerHTML = `
      <span class="category-tree-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>
      </span>
      <span class="category-tree-label">All Categories</span>
    `;

    li.appendChild(button);
    return li;
  }

  /**
   * Render a single category
   * @param {Category} category - Category entity
   * @param {number} level - Nesting level
   * @returns {HTMLElement} List item
   */
  renderCategory(category, level) {
    const li = document.createElement('li');
    li.className = 'category-tree-item';
    li.setAttribute('role', 'treeitem');
    li.setAttribute('aria-level', level + 1);

    const hasChildren = category.hasChildren();
    const isExpanded = this.expandedCategories.has(category.id) || this.options.expandAll;
    const isSelected = this.options.selectedCategoryId === category.id;

    const button = document.createElement('button');
    button.className = `category-tree-button ${isSelected ? 'active' : ''}`;
    button.setAttribute('data-category-id', category.id);
    button.setAttribute('aria-expanded', hasChildren ? String(isExpanded) : 'false');

    // Add expand/collapse icon if has children
    let iconHtml = '';
    if (hasChildren) {
      iconHtml = `
        <span class="category-tree-expand ${isExpanded ? 'expanded' : ''}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </span>
      `;
    } else {
      iconHtml = `
        <span class="category-tree-expand">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
          </svg>
        </span>
      `;
    }

    button.innerHTML = `
      ${iconHtml}
      <span class="category-tree-label">${this.escapeHtml(category.name)}</span>
    `;

    li.appendChild(button);

    // Render children if category has children and is expanded
    if (hasChildren && isExpanded) {
      const childList = document.createElement('ul');
      childList.className = 'category-tree-children';
      childList.setAttribute('role', 'group');

      category.children.forEach(child => {
        childList.appendChild(this.renderCategory(child, level + 1));
      });

      li.appendChild(childList);
    }

    return li;
  }

  /**
   * Render clear filter button
   * @returns {HTMLElement} Button element
   */
  renderClearButton() {
    const button = document.createElement('button');
    button.className = 'btn btn-ghost btn-small category-tree-clear';
    button.textContent = 'Clear Filter';
    button.addEventListener('click', () => this.onClearFilter());
    return button;
  }

  /**
   * Attach event listeners
   * @param {HTMLElement} wrapper - Wrapper element
   */
  attachEventListeners(wrapper) {
    wrapper.querySelectorAll('.category-tree-button').forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const categoryId = button.getAttribute('data-category-id');
        this.onCategoryClick(categoryId, button);
      });
    });
  }

  /**
   * Handle category click
   * @param {string} categoryId - Category ID (empty for "All Categories")
   * @param {HTMLElement} button - Clicked button element
   */
  onCategoryClick(categoryId, button) {
    const category = this.findCategory(categoryId);

    // If category has children, toggle expand/collapse
    if (category && category.hasChildren()) {
      if (this.expandedCategories.has(categoryId)) {
        this.expandedCategories.delete(categoryId);
      } else {
        this.expandedCategories.add(categoryId);
      }
    }

    // Update selection
    this.options.selectedCategoryId = categoryId || null;

    // Publish event
    eventBus.publish('catalog:category-changed', {
      categoryId: categoryId || null,
      category: category || null
    });

    // Re-render
    this.update();
  }

  /**
   * Handle clear filter click
   */
  onClearFilter() {
    this.options.selectedCategoryId = null;
    eventBus.publish('catalog:category-changed', {
      categoryId: null,
      category: null
    });
    this.update();
  }

  /**
   * Find category by ID in tree
   * @param {string} categoryId - Category ID to find
   * @returns {Category|null} Found category or null
   */
  findCategory(categoryId) {
    if (!categoryId) return null;

    for (const category of this.categories) {
      const found = this.searchInTree(category, categoryId);
      if (found) return found;
    }

    return null;
  }

  /**
   * Search for category in tree
   * @param {Category} category - Current category
   * @param {string} targetId - Target category ID
   * @returns {Category|null} Found category or null
   */
  searchInTree(category, targetId) {
    if (category.id === targetId) {
      return category;
    }

    for (const child of category.children) {
      const found = this.searchInTree(child, targetId);
      if (found) return found;
    }

    return null;
  }

  /**
   * Set selected category
   * @param {string|null} categoryId - Category ID or null to clear selection
   */
  setSelectedCategory(categoryId) {
    this.options.selectedCategoryId = categoryId;

    // Expand parent categories
    if (categoryId) {
      this.expandPathTo(categoryId);
    }

    this.update();
  }

  /**
   * Expand tree path to category
   * @param {string} categoryId - Target category ID
   */
  expandPathTo(categoryId) {
    // This would need parent references to work properly
    // For now, we'll just expand all
    this.options.expandAll = true;
  }

  /**
   * Update the component
   */
  update() {
    if (this.element && this.element.parentNode) {
      const newElement = this.render();
      this.element.parentNode.replaceChild(newElement, this.element);
      this.element = newElement;
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
    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
    this.element = null;
    this.expandedCategories.clear();
  }
}

export default CategoryTreeComponent;
