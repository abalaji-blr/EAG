document.addEventListener('DOMContentLoaded', function() {
  // Get DOM elements
  const searchInput = document.getElementById('search-input');
  const searchButton = document.getElementById('search-button');
  const resultsContainer = document.getElementById('results-container');
  const indexedCount = document.getElementById('indexed-count');
  const buildIndexButton = document.getElementById('build-index');
  
  // Track current search state
  let currentSearchQuery = '';
  let isSearching = false;
  
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
    if (!query || query === currentSearchQuery || isSearching) return;
    
    currentSearchQuery = query;
    isSearching = true;
    showLoadingState();
    
    // Send search request to background script
    chrome.runtime.sendMessage(
      { action: "search", query: query },
      function(results) {
        isSearching = false;
        displayResults(results, query);
      }
    );
  }
  
  // Display search results
  function displayResults(results, query) {
    // Clear previous results and event listeners
    while (resultsContainer.firstChild) {
      resultsContainer.removeChild(resultsContainer.firstChild);
    }
    
    if (!results || results.length === 0) {
      resultsContainer.innerHTML = `
        <div class="empty-state">
          No results found for "${query}"
        </div>
      `;
      return;
    }
    
    // Create a document fragment for better performance
    const fragment = document.createDocumentFragment();
    
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
      
      fragment.appendChild(resultItem);
    });
    
    // Append all results at once
    resultsContainer.appendChild(fragment);
  }
  
  // Open page and highlight matched content
  function openPageAndHighlight(url, query) {
    console.log('Opening page:', url, 'with query:', query);
    try {
      // First create a new window
      chrome.windows.create({ url: url, focused: true }, function(window) {
        if (chrome.runtime.lastError) {
          console.error('Error creating window:', chrome.runtime.lastError);
          return;
        }
        console.log('Window created with ID:', window.id);
        
        // Get the active tab in the new window
        chrome.tabs.query({ active: true, windowId: window.id }, function(tabs) {
          if (chrome.runtime.lastError) {
            console.error('Error querying tabs:', chrome.runtime.lastError);
            return;
          }
          if (tabs.length === 0) {
            console.error('No active tab found');
            return;
          }
          
          const tab = tabs[0];
          console.log('Found active tab:', tab.id);
          
          // Wait for page to load before highlighting
          chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
            console.log('Tab updated:', tabId, 'Status:', info.status);
            if (tabId === tab.id && info.status === 'complete') {
              // Remove listener to avoid multiple calls
              chrome.tabs.onUpdated.removeListener(listener);
              
              // Send highlight message to content script with retry
              let retryCount = 0;
              const maxRetries = 2;
              
              function tryHighlight() {
                console.log('Attempting highlight, retry:', retryCount);
                try {
                  chrome.tabs.sendMessage(tab.id, {
                    action: "highlightText",
                    query: query
                  }, function(response) {
                    if (chrome.runtime.lastError) {
                      console.error('Error sending message:', chrome.runtime.lastError);
                      if (retryCount < maxRetries) {
                        retryCount++;
                        // Use exponential backoff: 200ms, 400ms, 800ms
                        setTimeout(tryHighlight, 200 * Math.pow(2, retryCount - 1));
                      }
                    } else {
                      console.log('Highlight message response:', response);
                      if (response && !response.success) {
                        console.error('Highlighting failed:', response.error);
                      }
                    }
                  });
                } catch (error) {
                  console.error('Error in tryHighlight:', error);
                }
              }
              
              // Initial attempt after a shorter delay
              setTimeout(tryHighlight, 200);
            }
          });
        });
      });
    } catch (error) {
      console.error('Error in openPageAndHighlight:', error);
    }
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
