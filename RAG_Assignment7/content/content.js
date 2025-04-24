// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extractContent") {
    // Extract meaningful content from the page
    const content = extractPageContent();
    sendResponse({ content });
  } else if (request.action === "highlightText") {
    // Highlight text on page
    highlightText(request.query);
    sendResponse({ success: true });
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
  if (!searchText) return;
  
  // Remove previous highlights
  const oldHighlights = document.querySelectorAll('.nomic-search-highlight');
  oldHighlights.forEach(h => {
    const parent = h.parentNode;
    parent.replaceChild(document.createTextNode(h.textContent), h);
    parent.normalize();
  });
  
  // Perform new highlighting
  const searchRegex = new RegExp(escapeRegExp(searchText), 'gi');
  const textNodes = getTextNodes(document.body);
  
  let foundMatch = false;
  
  textNodes.forEach(node => {
    const matches = node.textContent.match(searchRegex);
    if (!matches) return;
    
    const splits = node.textContent.split(searchRegex);
    if (splits.length === 1) return;
    
    const fragment = document.createDocumentFragment();
    
    for (let i = 0; i < splits.length; i++) {
      // Add text before match
      fragment.appendChild(document.createTextNode(splits[i]));
      
      // Add highlighted match (except after last split)
      if (i < splits.length - 1) {
        const highlightSpan = document.createElement('span');
        highlightSpan.textContent = matches[i];
        highlightSpan.className = 'nomic-search-highlight';
        highlightSpan.style.backgroundColor = '#FFFF00';
        highlightSpan.style.color = '#000000';
        fragment.appendChild(highlightSpan);
        
        if (!foundMatch) {
          foundMatch = true;
          // Scroll to first match
          setTimeout(() => {
            highlightSpan.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 100);
        }
      }
    }
    
    // Replace original node with fragment
    node.parentNode.replaceChild(fragment, node);
  });
}

// Helper: Get all text nodes under an element
function getTextNodes(element) {
  const textNodes = [];
  const walker = document.createTreeWalker(
    element, 
    NodeFilter.SHOW_TEXT, 
    { acceptNode: node => node.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT }
  );
  
  let node;
  while (node = walker.nextNode()) {
    textNodes.push(node);
  }
  
  return textNodes;
}

// Helper: Escape special characters in regex
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Add CSS for highlights
const style = document.createElement('style');
style.textContent = `
  .nomic-search-highlight {
    background-color: #FFFF00 !important;
    color: #000000 !important;
    padding: 2px;
    border-radius: 2px;
  }
`;
document.head.appendChild(style);
