// List of domains to skip (confidential/sensitive sites)
const SKIP_DOMAINS = [
  'mail.google.com',
  'gmail.com',
  'web.whatsapp.com',
  'drive.google.com',
  'docs.google.com',
  'accounts.google.com',
  'login',
  'signin',
  'banking',
  'account',
  'wallet',
  'paypal',
  'venmo',
  'myaccount'
];

// Check if URL should be skipped
function shouldSkipUrl(url) {
  const urlObj = new URL(url);
  const domain = urlObj.hostname;
  
  return SKIP_DOMAINS.some(skipDomain => 
    domain.includes(skipDomain) || url.includes(skipDomain)
  );
}

// Track completed page visits to avoid processing a page multiple times
const processedUrls = new Set();

// Listen for page navigation completion
chrome.webNavigation.onCompleted.addListener(details => {
  // Only process main frame (not iframes)
  if (details.frameId !== 0) return;
  
  const url = details.url;
  
  // Skip extension pages, local files, etc.
  if (!url.startsWith('http')) return;
  
  // Skip if already processed
  if (processedUrls.has(url)) return;
  
  // Skip confidential sites
  if (shouldSkipUrl(url)) {
    console.log(`Skipping confidential site: ${url}`);
    return;
  }
  
  // Mark as processed
  processedUrls.add(url);
  
  // Tell content script to extract page content
  chrome.tabs.sendMessage(
    details.tabId, 
    { action: "extractContent" },
    response => {
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
        return;
      }
      
      if (response && response.content) {
        // Process the content and update the index
        processPageContent(url, response.content);
      }
    }
  );
});

// Process page content and update index
async function processPageContent(url, content) {
  try {
    // Here we would send content to Python backend for embedding and indexing
    // For demo purposes, we'll just store in Chrome storage
    
    // Get existing data
    chrome.storage.local.get(['pages'], function(result) {
      const pages = result.pages || [];
      
      // Add new page (in real implementation, we'd store embeddings)
      pages.push({
        url: url,
        content: content.substring(0, 10000), // Limit storage for demo
        timestamp: Date.now()
      });
      
      // Save back to storage
      chrome.storage.local.set({pages: pages}, function() {
        console.log(`Indexed page: ${url}`);
      });
    });
  } catch (error) {
    console.error('Error processing content:', error);
  }
}

// Handle search requests from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "search") {
    // In a real implementation, this would query the FAISS index
    searchPages(request.query).then(sendResponse);
    return true; // Keep the message channel open for async response
  }
});

// Search function
async function searchPages(query) {
  return new Promise((resolve) => {
    chrome.storage.local.get(['pages'], function(result) {
      const pages = result.pages || [];
      
      // Basic keyword search for demo (would be semantic in real implementation)
      const results = pages.filter(page => 
        page.content.toLowerCase().includes(query.toLowerCase())
      ).map(page => ({
        url: page.url,
        snippet: extractSnippet(page.content, query, 200)
      }));
      
      resolve(results);
    });
  });
}

// Extract a snippet from content containing the query
function extractSnippet(content, query, snippetLength) {
  const lowerContent = content.toLowerCase();
  const lowerQuery = query.toLowerCase();
  
  const queryIndex = lowerContent.indexOf(lowerQuery);
  if (queryIndex === -1) return content.substring(0, snippetLength);
  
  const startIndex = Math.max(0, queryIndex - snippetLength / 2);
  const endIndex = Math.min(content.length, queryIndex + query.length + snippetLength / 2);
  
  return content.substring(startIndex, endIndex);
}
