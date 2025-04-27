console.log('Content script loaded successfully');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Content script received message:', request);
  if (request.action === "extractContent") {
    // Extract meaningful content from the page
    const content = extractPageContent();
    sendResponse({ content });
  } else if (request.action === "highlightText") {
    console.log('Highlighting text:', request.query);
    try {
      // Highlight text on page
      highlightText(request.query);
      console.log('Highlighting completed successfully');
      sendResponse({ success: true });
    } catch (error) {
      console.error('Error during highlighting:', error);
      sendResponse({ success: false, error: error.message });
    }
  }
  return true;
});

// Extract content from page
function extractPageContent() {
  // Get the main content (skip navigation, footers, etc.)
  const article = document.querySelector('article');
  const main = document.querySelector('main');
  const contentDiv = document.querySelector('#content');
  
  // Try to get the most relevant content container
  let contentElement = article || main || contentDiv || document.body;
  
  // Extract text content, removing script elements
  const scripts = contentElement.querySelectorAll('script, style');
  scripts.forEach(script => script.remove());
  
  // Get text with some structure preserved
  const title = document.title || '';
  const headings = Array.from(contentElement.querySelectorAll('h1, h2, h3'))
    .map(h => h.textContent.trim())
    .join(' | ');
    
  const paragraphs = Array.from(contentElement.querySelectorAll('p'))
    .map(p => p.textContent.trim())
    .join('\n\n');
  
  // Combine content with importance weighting
  return `${title}\n${headings}\n\n${paragraphs}`;
}

// Highlight matching text on page
function highlightText(searchText) {
  console.log('Starting highlight with text:', searchText);
  console.log('Search text length:', searchText.length);
  console.log('Search text type:', typeof searchText);
  
  if (!searchText) {
    console.log('No search text provided');
    return;
  }
  
  // Remove previous highlights
  const oldHighlights = document.querySelectorAll('.nomic-search-highlight');
  console.log('Removing', oldHighlights.length, 'old highlights');
  oldHighlights.forEach(h => {
    const parent = h.parentNode;
    parent.replaceChild(document.createTextNode(h.textContent), h);
    parent.normalize();
  });
  
  // Perform new highlighting
  const escapedText = escapeRegExp(searchText);
  console.log('Escaped search text:', escapedText);
  
  const searchRegex = new RegExp(escapedText, 'gi');
  console.log('Created regex:', searchRegex);
  
  const textNodes = getTextNodes(document.body);
  console.log('Found', textNodes.length, 'text nodes to search');
  
  let foundMatch = false;
  let matchCount = 0;
  
  textNodes.forEach((node, index) => {
    try {
      const nodeText = node.textContent;
      console.log(`Checking node ${index + 1}/${textNodes.length}:`, nodeText.substring(0, 50) + '...');
      
      const matches = nodeText.match(searchRegex);
      if (matches) {
        console.log(`Found ${matches.length} matches in node ${index + 1}`);
        console.log('Matches:', matches);
      }
      
      if (!matches) return;
      
      const splits = nodeText.split(searchRegex);
      if (splits.length === 1) return;
      
      console.log('Found match in node:', nodeText.substring(0, 50) + '...');
      matchCount += matches.length;
      
      const fragment = document.createDocumentFragment();
      
      for (let i = 0; i < splits.length; i++) {
        // Add text before match
        fragment.appendChild(document.createTextNode(splits[i]));
        
        // Add highlighted match (except after last split)
        if (i < splits.length - 1) {
          const highlightSpan = document.createElement('span');
          highlightSpan.textContent = matches[i];
          highlightSpan.className = 'nomic-search-highlight';
          fragment.appendChild(highlightSpan);
          
          if (!foundMatch) {
            foundMatch = true;
            console.log('Scrolling to first match');
            // Scroll to first match with smooth animation
            setTimeout(() => {
              highlightSpan.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center',
                inline: 'center'
              });
            }, 100);
          }
        }
      }
      
      // Replace original node with fragment
      node.parentNode.replaceChild(fragment, node);
    } catch (error) {
      console.error('Error processing text node:', error);
    }
  });
  
  console.log('Highlighting complete. Found', matchCount, 'total matches');
  if (matchCount === 0) {
    console.log('No matches found for search text:', searchText);
  }
}

// Helper: Get all text nodes under an element
function getTextNodes(element) {
  console.log('Starting to get text nodes from element:', element.tagName);
  const textNodes = [];
  try {
    const walker = document.createTreeWalker(
      element, 
      NodeFilter.SHOW_TEXT, 
      { 
        acceptNode: function(node) {
          // Skip empty or whitespace-only nodes
          if (!node.textContent || !node.textContent.trim()) {
            return NodeFilter.FILTER_REJECT;
          }
          // Skip nodes that are children of script or style tags
          if (node.parentNode && 
              (node.parentNode.tagName === 'SCRIPT' || 
               node.parentNode.tagName === 'STYLE')) {
            return NodeFilter.FILTER_REJECT;
          }
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );
    
    let node;
    let count = 0;
    while (node = walker.nextNode()) {
      textNodes.push(node);
      count++;
      if (count % 100 === 0) {
        console.log('Processed', count, 'text nodes so far...');
      }
    }
    console.log('Total text nodes found:', count);
    
    // Log some sample text nodes for debugging
    if (count > 0) {
      console.log('Sample text nodes:');
      for (let i = 0; i < Math.min(3, textNodes.length); i++) {
        console.log('Node', i + 1, ':', textNodes[i].textContent.substring(0, 50) + '...');
      }
    }
  } catch (error) {
    console.error('Error in getTextNodes:', error);
  }
  return textNodes;
}

// Helper: Escape special characters in regex
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Update the highlight styles
const style = document.createElement('style');
style.textContent = `
  .nomic-search-highlight {
    background-color: #FFEB3B !important;
    color: #000000 !important;
    padding: 2px 4px;
    border-radius: 3px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    font-weight: bold;
    animation: highlight-pulse 1s ease-in-out;
  }

  @keyframes highlight-pulse {
    0% { background-color: #FFEB3B; }
    50% { background-color: #FFC107; }
    100% { background-color: #FFEB3B; }
  }
`;
document.head.appendChild(style);
