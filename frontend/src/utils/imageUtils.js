/**
 * Utility functions for handling image URLs, especially Google Drive links
 */

/**
 * Convert Google Drive sharing URL to direct image URL
 * @param {string} url - The original URL (could be Google Drive sharing URL or regular URL)
 * @returns {string} - Direct image URL that can be used in img src
 */
export const convertToDirectImageUrl = (url) => {
  if (!url) return '/default-course-image.png';
  
  // Check if it's a Google Drive URL
  if (url.includes('drive.google.com')) {
    // Extract file ID from various Google Drive URL formats
    let fileId = null;
    
    // Format 1: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
    const viewMatch = url.match(/\/file\/d\/([a-zA-Z0-9_-]+)/);
    if (viewMatch) {
      fileId = viewMatch[1];
    }
    
    // Format 2: https://drive.google.com/open?id=FILE_ID
    const openMatch = url.match(/[?&]id=([a-zA-Z0-9_-]+)/);
    if (openMatch) {
      fileId = openMatch[1];
    }
    
    // Format 3: Already direct URL https://drive.google.com/uc?id=FILE_ID
    const ucMatch = url.match(/\/uc\?id=([a-zA-Z0-9_-]+)/);
    if (ucMatch) {
      fileId = ucMatch[1];
    }
    
    // Format 4: https://drive.google.com/thumbnail?id=FILE_ID
    const thumbnailMatch = url.match(/\/thumbnail\?id=([a-zA-Z0-9_-]+)/);
    if (thumbnailMatch) {
      return url; // Already in thumbnail format
    }
    
    // Convert to direct image URL if we found a file ID
    if (fileId) {
      // Try the thumbnail format first for better image display
      return `https://drive.google.com/thumbnail?id=${fileId}&sz=w800`;
    }
  }
  
  // For non-Google Drive URLs, return as-is
  return url;
};

/**
 * Get image URL with error handling and fallback
 * @param {string} imageUrl - The image URL (could be thumbnailUrl, thumbnail, or any format)
 * @param {string} fallback - Fallback image URL
 * @returns {string} - Processed image URL
 */
export const getImageUrl = (imageUrl, fallback = '/default-course-image.png') => {
  if (!imageUrl) return fallback;
  
  // Convert Google Drive URLs to direct format
  const directUrl = convertToDirectImageUrl(imageUrl);
  
  return directUrl;
};

/**
 * Handle image error by setting fallback source
 * @param {Event} event - The error event from img onError
 * @param {string} fallback - Fallback image URL
 */
export const handleImageError = (event, fallback = '/default-course-image.png') => {
  if (event.target.src !== fallback) {
    event.target.src = fallback;
  }
};