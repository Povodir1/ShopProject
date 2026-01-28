/**
 * Validators
 * Utility functions for validating input data
 */

/**
 * Validate email address
 * @param {string} email - Email to validate
 * @returns {Object} Validation result with isValid and error
 */
export function validateEmail(email) {
  if (!email) {
    return { isValid: false, error: 'Email is required' };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Invalid email format' };
  }

  if (email.length > 255) {
    return { isValid: false, error: 'Email is too long' };
  }

  return { isValid: true, error: null };
}

/**
 * Validate quantity
 * @param {number} quantity - Quantity to validate
 * @param {Object} options - Validation options
 * @returns {Object} Validation result
 */
export function validateQuantity(quantity, options = {}) {
  const {
    min = 1,
    max = 100,
    required = true
  } = options;

  if (quantity === null || quantity === undefined) {
    if (required) {
      return { isValid: false, error: 'Quantity is required' };
    }
    return { isValid: true, error: null };
  }

  const numQuantity = Number(quantity);

  if (isNaN(numQuantity)) {
    return { isValid: false, error: 'Quantity must be a number' };
  }

  if (!Number.isInteger(numQuantity)) {
    return { isValid: false, error: 'Quantity must be a whole number' };
  }

  if (numQuantity < min) {
    return { isValid: false, error: `Quantity must be at least ${min}` };
  }

  if (numQuantity > max) {
    return { isValid: false, error: `Quantity cannot exceed ${max}` };
  }

  return { isValid: true, error: null };
}

/**
 * Validate UUID v4
 * @param {string} uuid - UUID to validate
 * @returns {Object} Validation result
 */
export function validateUUID(uuid) {
  if (!uuid) {
    return { isValid: false, error: 'ID is required' };
  }

  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  if (!uuidRegex.test(uuid)) {
    return { isValid: false, error: 'Invalid ID format' };
  }

  return { isValid: true, error: null };
}

/**
 * Validate required field
 * @param {*} value - Value to validate
 * @param {string} fieldName - Field name for error message
 * @returns {Object} Validation result
 */
export function validateRequired(value, fieldName = 'Field') {
  if (value === null || value === undefined || value === '') {
    return { isValid: false, error: `${fieldName} is required` };
  }

  return { isValid: true, error: null };
}

/**
 * Validate string length
 * @param {string} value - String to validate
 * @param {Object} options - Validation options
 * @returns {Object} Validation result
 */
export function validateLength(value, options = {}) {
  const {
    min = 0,
    max = Infinity,
    fieldName = 'Field',
    required = false
  } = options;

  if (!value) {
    if (required) {
      return { isValid: false, error: `${fieldName} is required` };
    }
    return { isValid: true, error: null };
  }

  const str = String(value);

  if (str.length < min) {
    return { isValid: false, error: `${fieldName} must be at least ${min} characters` };
  }

  if (str.length > max) {
    return { isValid: false, error: `${fieldName} cannot exceed ${max} characters` };
  }

  return { isValid: true, error: null };
}

/**
 * Validate price
 * @param {number} price - Price to validate
 * @param {Object} options - Validation options
 * @returns {Object} Validation result
 */
export function validatePrice(price, options = {}) {
  const {
    min = 0,
    max = Infinity,
    required = true
  } = options;

  if (price === null || price === undefined) {
    if (required) {
      return { isValid: false, error: 'Price is required' };
    }
    return { isValid: true, error: null };
  }

  const numPrice = Number(price);

  if (isNaN(numPrice)) {
    return { isValid: false, error: 'Price must be a number' };
  }

  if (numPrice < min) {
    return { isValid: false, error: `Price must be at least ${min}` };
  }

  if (numPrice > max) {
    return { isValid: false, error: `Price cannot exceed ${max}` };
  }

  // Check for reasonable decimal places (max 2 for currency)
  const decimalPlaces = (numPrice.toString().split('.')[1] || '').length;
  if (decimalPlaces > 2) {
    return { isValid: false, error: 'Price cannot have more than 2 decimal places' };
  }

  return { isValid: true, error: null };
}

/**
 * Validate URL
 * @param {string} url - URL to validate
 * @returns {Object} Validation result
 */
export function validateURL(url) {
  if (!url) {
    return { isValid: true, error: null }; // URL is optional
  }

  try {
    new URL(url);
    return { isValid: true, error: null };
  } catch (error) {
    return { isValid: false, error: 'Invalid URL format' };
  }
}

/**
 * Validate search query
 * @param {string} query - Search query to validate
 * @returns {Object} Validation result
 */
export function validateSearchQuery(query) {
  if (!query) {
    return { isValid: true, error: null }; // Empty search is allowed
  }

  return validateLength(query, { min: 2, max: 100, fieldName: 'Search query' });
}

/**
 * Validate phone number (basic validation)
 * @param {string} phone - Phone number to validate
 * @returns {Object} Validation result
 */
export function validatePhone(phone) {
  if (!phone) {
    return { isValid: true, error: null }; // Phone is optional
  }

  // Remove common formatting
  const cleaned = phone.replace(/[\s\-\(\)]/g, '');

  // Basic check: 10-15 digits
  const phoneRegex = /^\d{10,15}$/;

  if (!phoneRegex.test(cleaned)) {
    return { isValid: false, error: 'Invalid phone number format' };
  }

  return { isValid: true, error: null };
}

/**
 * Validate form data object
 * @param {Object} data - Form data to validate
 * @param {Object} schema - Validation schema
 * @returns {Object} Validation result with errors object
 */
export function validateForm(data, schema) {
  const errors = {};
  let isValid = true;

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];

    for (const rule of rules) {
      const result = rule(value);

      if (!result.isValid) {
        errors[field] = result.error;
        isValid = false;
        break; // Stop at first error per field
      }
    }
  }

  return {
    isValid,
    errors
  };
}

/**
 * Create a required validator
 * @param {string} fieldName - Field name
 * @returns {Function} Validator function
 */
export function required(fieldName) {
  return (value) => validateRequired(value, fieldName);
}

/**
 * Create a min length validator
 * @param {number} length - Minimum length
 * @param {string} fieldName - Field name
 * @returns {Function} Validator function
 */
export function minLength(length, fieldName = 'Field') {
  return (value) => validateLength(value, { min: length, fieldName });
}

/**
 * Create a max length validator
 * @param {number} length - Maximum length
 * @param {string} fieldName - Field name
 * @returns {Function} Validator function
 */
export function maxLength(length, fieldName = 'Field') {
  return (value) => validateLength(value, { max: length, fieldName });
}

/**
 * Create a range validator
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @param {string} fieldName - Field name
 * @returns {Function} Validator function
 */
export function range(min, max, fieldName = 'Field') {
  return (value) => {
    const num = Number(value);
    if (num < min) {
      return { isValid: false, error: `${fieldName} must be at least ${min}` };
    }
    if (num > max) {
      return { isValid: false, error: `${fieldName} cannot exceed ${max}` };
    }
    return { isValid: true, error: null };
  };
}

// Export all validators as object
const validators = {
  validateEmail,
  validateQuantity,
  validateUUID,
  validateRequired,
  validateLength,
  validatePrice,
  validateURL,
  validateSearchQuery,
  validatePhone,
  validateForm,
  required,
  minLength,
  maxLength,
  range
};

export default validators;
