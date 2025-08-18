/**
 * Browser Compatibility Utilities
 * Handles Edge and other browser-specific compatibility issues
 */

// Detect Microsoft Edge
export const isEdge = () => {
  return /Edge\/|Edg\//.test(navigator.userAgent);
};

// Detect Internet Explorer (legacy Edge)
export const isIE = () => {
  return /Trident\/|MSIE/.test(navigator.userAgent);
};

// Get Edge-compatible fetch options
export const getEdgeCompatibleFetchOptions = (options = {}) => {
  const baseOptions = {
    credentials: 'same-origin',
    cache: 'no-cache',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cache-Control': 'no-cache',
      ...options.headers
    },
    ...options
  };

  // For Edge, add additional headers to prevent caching issues
  if (isEdge() || isIE()) {
    baseOptions.headers['Pragma'] = 'no-cache';
    baseOptions.headers['Expires'] = '0';
  }

  return baseOptions;
};

// Enhanced fetch for Edge compatibility
export const edgeCompatibleFetch = async (url, options = {}) => {
  const compatOptions = getEdgeCompatibleFetchOptions(options);
  
  try {
    const response = await fetch(url, compatOptions);
    
    // Edge-specific error handling
    if (!response.ok && isEdge()) {
      // Edge sometimes doesn't properly expose error details
      console.warn(`Edge fetch warning: ${response.status} ${response.statusText} for ${url}`);
    }
    
    return response;
  } catch (error) {
    // Enhanced error reporting for Edge
    if (isEdge() || isIE()) {
      console.error('Edge fetch error:', {
        url,
        error: error.message,
        browser: navigator.userAgent
      });
    }
    throw error;
  }
};

// Check if browser supports modern features
export const checkBrowserSupport = () => {
  const support = {
    fetch: typeof fetch !== 'undefined',
    promise: typeof Promise !== 'undefined',
    asyncAwait: (async () => {})().constructor.name === 'AsyncFunction',
    localStorage: typeof Storage !== 'undefined',
    json: typeof JSON !== 'undefined'
  };

  const unsupported = Object.keys(support).filter(key => !support[key]);
  
  if (unsupported.length > 0) {
    console.error('Unsupported browser features:', unsupported);
    return false;
  }

  return true;
};

// Show browser compatibility warning
export const showBrowserWarning = () => {
  if (!checkBrowserSupport()) {
    const message = `Your browser may not support all features of this application. Please use a modern version of Chrome, Firefox, Safari, or Edge.`;
    console.warn(message);
    
    // Only show alert if absolutely necessary (critical features missing)
    if (!window.fetch || !window.Promise) {
      alert(message);
    }
  }
};

export default {
  isEdge,
  isIE,
  getEdgeCompatibleFetchOptions,
  edgeCompatibleFetch,
  checkBrowserSupport,
  showBrowserWarning
};