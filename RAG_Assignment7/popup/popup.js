document.addEventListener('DOMContentLoaded', function() {
  // Get DOM elements
  const searchInput = document.getElementById('search-input');
  const searchButton = document.getElementById('search-button');
  const resultsContainer = document.getElementById('results-container');
  const indexedCount = document.getElementById('indexed-count');
  const buildIndexButton = document.getElementById('build-index');
  
  // Update indexed page count
  updateIndexedCount();
  
  // Add event listeners
  searchButton.addEventListener('click', performSearch);
  searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') performSearch();
  });
  
  buildIndexButton.addEventListener('click', function() {
    showMessage('Building index in background...');
    // In a real implementation, this would trigger the Python index builder
  });
  
  // Focus search input on popup open
  searchInput.focus();
  
  // Perform search function
  function performSearch() {
    const query = searchInput.value.trim();
    if (!query) return;
    
    showLoadingState();
    
    // Send search request to background script
    chrome.runtime.sendMessage(
      { action: "search", query: query },
      function(results) {
        displayResults(results, query);
      }
    );
  }
  
  // Display search results
  function displayResults(results, query) {
    resultsContainer.innerHTML = '';
    
    if (!results || results.length === 0) {
      resultsContainer.innerHTML = `
        <div class="empty-state">
          No results found for "${query}"
        </div>
      `;
      return;
    }
    
    // Create result items
    results.forEach(result => {
      const resultItem = document.createElement('div');
      resultItem.className = 'result-item';
      
      // Get page title from URL
      const urlObj = new URL(result.url);
      const title = urlObj.hostname + urlObj.pathname;
      
      resultItem.innerHTML = `
        <div class="result-title">${title}</div>
        <div class="result-url">${result.url}</div>
        <div class="result-snippet">${result.snippet}</div>
      `;
      
      // Add click handler to open the page
      resultItem.addEventListener('click', function() {
        openPageAndHighlight(result.url, query);
      });
      
      resultsContainer.appendChild(resultItem);
    });
  }
  
  // Open page and highlight matched content
  function openPageAndHighlight(url, query) {
    chrome.tabs.create({ url: url, active: true }, function(tab) {
      // Wait for page to load before highlighting
      chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
        if (tabId === tab.id && info.status === 'complete') {
          // Remove listener to avoid multiple calls
          chrome.tabs.onUpdated.removeListener(listener);
          
          // Send highlight message to content script
          setTimeout(() => {
            chrome.tabs.sendMessage(tab.id, {
              action: "highlightText",
              query: query
            });
          }, 500);
        }
      });
    });
  }
  
  // Show loading state
  function showLoadingState() {
    resultsContainer.innerHTML = `
      <div class="empty-state">
        Searching...
      </div>
    `;
  }
  
  // Show message
  function showMessage(message) {
    resultsContainer.innerHTML = `
      <div class="empty-state">
        ${message}
      </div>
    `;
  }
  
  // Update indexed count
  function updateIndexedCount() {
    chrome.storage.local.get(['pages'], function(result) {
      const pages = result.pages || [];
      indexedCount.textContent = pages.length;
    });
  }
});
