// app.js

document.addEventListener('DOMContentLoaded', () => {
  // Initialize event listeners for buttons
  document.getElementById('generate-profiles-btn').addEventListener('click', generateProfiles);
  document.getElementById('simulate-conversations-btn').addEventListener('click', simulateConversations);
  document.getElementById('analyze-sentiment-btn').addEventListener('click', analyzeSentiment);
  document.getElementById('reset-button').addEventListener('click', resetApplication);
  
  // Add diagnostic info
  console.log('Initializing application...');
  console.log('API base URL:', API_BASE_URL);
  
  // Initial connection test
  testApiConnection();
  
  // Check initial status
  checkStatus();
  
  // Set up polling for status updates (every 2 seconds)
  setInterval(checkStatus, 2000);
});

// API base URL
const API_BASE_URL = 'http://localhost:3000';

// Check the current status of the backend
async function checkStatus() {
  try {
    console.log('Checking status at:', `${API_BASE_URL}/api/status`);
    const response = await fetch(`${API_BASE_URL}/api/status`, {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      console.error('Status check failed:', response.status, response.statusText);
      updateStatusBanner('Error checking status: ' + response.status, 'error');
      return;
    }
    
    const data = await response.json();
    console.log('Status check successful:', data);
    
    // Update UI based on current state
    updateUIBasedOnStatus(data);
    
    // If an operation is in progress, show the appropriate spinner
    if (data.in_progress) {
      updateStatusBanner(`In progress: ${data.message}`, 'in-progress');
      
      // Show the appropriate spinner
      if (data.step === 'generate_profiles') {
        document.getElementById('profiles-spinner').style.display = 'flex';
      } else if (data.step === 'simulate_conversations') {
        document.getElementById('conversations-spinner').style.display = 'flex';
      } else if (data.step === 'analyze_sentiment') {
        document.getElementById('sentiment-spinner').style.display = 'flex';
      }
    } else if (data.message) {
      updateStatusBanner(data.message, 'success');
    }
    
    // Enable/disable buttons based on the current state
    document.getElementById('simulate-conversations-btn').disabled = !data.has_profiles;
    document.getElementById('analyze-sentiment-btn').disabled = !data.has_conversations;
    
    // Check if we have results and load them if needed
    if (data.has_sentiment && document.getElementById('results-container').style.display === 'none') {
      fetchResults();
    }
  } catch (error) {
    console.error('Error checking status:', error);
    updateStatusBanner('Error connecting to server', 'error');
  }
}

// Update the status banner
function updateStatusBanner(message, type = '') {
  const banner = document.getElementById('status-banner');
  const messageElement = document.getElementById('status-message');
  
  // Remove all classes
  banner.classList.remove('in-progress', 'success', 'error');
  
  // Add the appropriate class
  if (type) {
    banner.classList.add(type);
  }
  
  // Update the message
  messageElement.textContent = message;
}

// Update UI based on current status
function updateUIBasedOnStatus(status) {
  // Profiles section
  if (status.has_profiles) {
    document.getElementById('profiles-spinner').style.display = 'none';
    document.getElementById('profiles-content').style.display = 'block';
    
    // If we don't have the profiles displayed yet, fetch them
    if (document.getElementById('profiles-summary').children.length === 0) {
      fetchAndDisplayProfiles();
    }
  }
  
  // Conversations section
  if (status.has_conversations) {
    document.getElementById('conversations-spinner').style.display = 'none';
    document.getElementById('conversations-content').style.display = 'block';
    
    // If we don't have the sample conversation displayed yet, fetch it
    if (document.getElementById('sample-conversation').innerHTML === '') {
      fetchAndDisplaySampleConversation();
    }
  }
  
  // Sentiment section
  if (status.has_sentiment) {
    document.getElementById('sentiment-spinner').style.display = 'none';
    document.getElementById('sentiment-content').style.display = 'block';
    document.getElementById('results-heading').style.display = 'block';
  }
}

// Generate profiles
async function generateProfiles() {
  try {
    // Show spinner and update status
    document.getElementById('profiles-spinner').style.display = 'flex';
    document.getElementById('profiles-content').style.display = 'none';
    updateStatusBanner('Generating profiles...', 'in-progress');
    
    // Reset UI for subsequent steps
    document.getElementById('conversations-content').style.display = 'none';
    document.getElementById('sentiment-content').style.display = 'none';
    document.getElementById('results-container').style.display = 'none';
    document.getElementById('results-heading').style.display = 'none';
    document.getElementById('conversation-view').style.display = 'none';
    
    // Call the API
    const response = await fetch(`${API_BASE_URL}/api/generate-profiles`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ num_profiles: 10 })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to generate profiles');
    }
    
    const data = await response.json();
    
    // Display profiles
    displayProfiles(data.profiles);
    
    // Update UI
    document.getElementById('profiles-spinner').style.display = 'none';
    document.getElementById('profiles-content').style.display = 'block';
    document.getElementById('simulate-conversations-btn').disabled = false;
    
    updateStatusBanner(data.message, 'success');
  } catch (error) {
    console.error('Error generating profiles:', error);
    document.getElementById('profiles-spinner').style.display = 'none';
    updateStatusBanner(`Error: ${error.message}`, 'error');
  }
}

// Fetch and display profiles
async function fetchAndDisplayProfiles() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/status`);
    if (!response.ok) {
      throw new Error('Failed to fetch status');
    }
    
    const data = await response.json();
    
    if (data.has_profiles) {
      // Get profiles by calling the generate-profiles endpoint with a custom header to get current profiles
      const profilesResponse = await fetch(`${API_BASE_URL}/api/generate-profiles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Get-Current-Only': 'true'
        }
      });
      
      if (profilesResponse.ok) {
        const profilesData = await profilesResponse.json();
        displayProfiles(profilesData.profiles);
      }
    }
  } catch (error) {
    console.error('Error fetching profiles:', error);
  }
}

// Display profiles in the profiles summary section
function displayProfiles(profiles) {
  const container = document.getElementById('profiles-summary');
  container.innerHTML = '';
  
  profiles.forEach(profile => {
    const profileElement = document.createElement('div');
    profileElement.className = 'profile-mini';
    profileElement.innerHTML = `
      <div><strong>${profile.name}</strong>, ${profile.age}</div>
      <div class="small text-muted">${profile.interests.slice(0, 2).join(', ')}${profile.interests.length > 2 ? '...' : ''}</div>
    `;
    container.appendChild(profileElement);
  });
}

// Simulate conversations
async function simulateConversations() {
  try {
    // Show spinner and update status
    document.getElementById('conversations-spinner').style.display = 'flex';
    document.getElementById('conversations-content').style.display = 'none';
    updateStatusBanner('Simulating conversations...', 'in-progress');
    
    // Reset UI for subsequent steps
    document.getElementById('sentiment-content').style.display = 'none';
    document.getElementById('results-container').style.display = 'none';
    document.getElementById('results-heading').style.display = 'none';
    document.getElementById('conversation-view').style.display = 'none';
    
    // Call the API
    const response = await fetch(`${API_BASE_URL}/api/simulate-conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to simulate conversations');
    }
    
    const data = await response.json();
    
    // Display sample conversation
    displaySampleConversation(data.sample_conversation);
    
    // Update UI
    document.getElementById('conversations-spinner').style.display = 'none';
    document.getElementById('conversations-content').style.display = 'block';
    document.getElementById('analyze-sentiment-btn').disabled = false;
    
    updateStatusBanner(data.message, 'success');
  } catch (error) {
    console.error('Error simulating conversations:', error);
    document.getElementById('conversations-spinner').style.display = 'none';
    updateStatusBanner(`Error: ${error.message}`, 'error');
  }
}

// Fetch and display sample conversation
async function fetchAndDisplaySampleConversation() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/simulate-conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Get-Current-Only': 'true'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      displaySampleConversation(data.sample_conversation);
    }
  } catch (error) {
    console.error('Error fetching sample conversation:', error);
  }
}

// Display sample conversation
function displaySampleConversation(sampleConversation) {
  if (!sampleConversation || !sampleConversation.messages) return;
  
  const container = document.getElementById('sample-conversation');
  container.innerHTML = '';
  
  // Create a container for the streamed messages
  const messagesContainer = document.createElement('div');
  messagesContainer.className = 'd-flex flex-column conversation-display';
  container.appendChild(messagesContainer);
  
  // Function to add messages with a delay for visual effect
  function addMessageWithDelay(index) {
    if (index >= sampleConversation.messages.length) return;
    
    const message = sampleConversation.messages[index];
    const colonIndex = message.indexOf(':');
    
    if (colonIndex > 0) {
      const sender = message.substring(0, colonIndex).trim();
      const messageText = message.substring(colonIndex + 1).trim();
      
      const messageElement = document.createElement('div');
      messageElement.className = index % 2 === 0 ? 'message message-left' : 'message message-right';
      messageElement.innerHTML = `
        <div><strong>${sender}</strong></div>
        <div>${messageText}</div>
      `;
      
      messagesContainer.appendChild(messageElement);
      
      // Auto-scroll to the bottom
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Schedule the next message
    setTimeout(() => addMessageWithDelay(index + 1), 300);
  }
  
  // Start the animation
  addMessageWithDelay(0);
}

// Analyze sentiment
async function analyzeSentiment() {
  try {
    // Show spinner and update status
    document.getElementById('sentiment-spinner').style.display = 'flex';
    document.getElementById('sentiment-content').style.display = 'none';
    updateStatusBanner('Analyzing sentiment...', 'in-progress');
    
    // Reset results UI
    document.getElementById('results-container').style.display = 'none';
    document.getElementById('results-heading').style.display = 'none';
    document.getElementById('conversation-view').style.display = 'none';
    
    // Call the API
    const response = await fetch(`${API_BASE_URL}/api/analyze-sentiment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to analyze sentiment');
    }
    
    const data = await response.json();
    
    // Update UI
    document.getElementById('sentiment-spinner').style.display = 'none';
    document.getElementById('sentiment-content').style.display = 'block';
    document.getElementById('results-heading').style.display = 'block';
    
    // Display results
    renderResults(data.results);
    
    updateStatusBanner('Sentiment analysis complete!', 'success');
  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    document.getElementById('sentiment-spinner').style.display = 'none';
    updateStatusBanner(`Error: ${error.message}`, 'error');
  }
}

// Reset the application
async function resetApplication() {
  try {
    updateStatusBanner('Resetting application...', 'in-progress');
    
    // Call the reset API
    const response = await fetch(`${API_BASE_URL}/api/reset`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error('Failed to reset application');
    }
    
    // Reset UI
    document.getElementById('profiles-content').style.display = 'none';
    document.getElementById('conversations-content').style.display = 'none';
    document.getElementById('sentiment-content').style.display = 'none';
    document.getElementById('results-container').style.display = 'none';
    document.getElementById('results-heading').style.display = 'none';
    document.getElementById('conversation-view').style.display = 'none';
    
    // Clear contents
    document.getElementById('profiles-summary').innerHTML = '';
    document.getElementById('sample-conversation').innerHTML = '';
    document.getElementById('results-container').innerHTML = '';
    
    // Reset buttons
    document.getElementById('simulate-conversations-btn').disabled = true;
    document.getElementById('analyze-sentiment-btn').disabled = true;
    
    updateStatusBanner('Application reset. Ready to start again.', 'success');
  } catch (error) {
    console.error('Error resetting application:', error);
    updateStatusBanner(`Error: ${error.message}`, 'error');
  }
}

// Fetch the final results
async function fetchResults() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/results`);
    if (!response.ok) {
      throw new Error('Failed to fetch results');
    }
    
    const data = await response.json();
    renderResults(data.results);
  } catch (error) {
    console.error('Error fetching results:', error);
    updateStatusBanner(`Error: ${error.message}`, 'error');
  }
}

// Render results in the UI
function renderResults(results) {
  const container = document.getElementById('results-container');
  
  // Show results
  container.style.display = 'flex';
  
  // Clear previous content
  container.innerHTML = '';
  
  // Create a card for each user
  for (let userId in results) {
    const userData = results[userId];
    // Check if profile is in 'user' property instead of 'profile'
    const userInfo = userData.user || userData.profile || {};
    const matches = userData.matches || [];
    
    // Create profile card
    const profileCard = document.createElement('div');
    profileCard.className = 'col-md-4 mb-4';
    profileCard.innerHTML = `
      <div class="profile-card">
        <div class="profile-header">
          <h3>${userInfo.name || 'User'}, ${userInfo.age || ''}</h3>
        </div>
        <div class="profile-body">
          <p><strong>Bio:</strong> ${userInfo.bio || 'No bio available'}</p>
          <div class="mb-3">
            <strong>Interests:</strong><br>
            ${(userInfo.interests || []).map(interest => 
              `<span class="interest-tag">${interest}</span>`
            ).join('')}
          </div>
          <div class="mb-3">
            <strong>Personality:</strong>
            <p class="text-muted small">${userInfo.personality || 'Not specified'}</p>
          </div>
          <h5 class="mt-4">Top Matches:</h5>
          <div class="matches-list">
            ${renderMatchesList(matches, userId)}
          </div>
        </div>
      </div>
    `;
    
    container.appendChild(profileCard);
  }
  
  // Add event listeners to all match items
  document.querySelectorAll('.match-item').forEach(item => {
    item.addEventListener('click', handleMatchClick);
  });
}

// Render matches list HTML
function renderMatchesList(matches, userId) {
  if (!matches || matches.length === 0) {
    return '<p>No matches yet.</p>';
  }
  
  return matches.map((match, index) => {
    // Format sentiment score as percentage
    const scorePercent = Math.round((match.sentiment_score || 0) * 100);
    
    return `
      <div class="match-item" 
           data-user-id="${userId}" 
           data-partner-id="${match.partner_id}"
           data-conversation='${JSON.stringify(match.conversation || [])}'>
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <strong>${match.partner_name || 'Unknown User'}</strong>
          </div>
          <div>
            <span class="score-badge">${scorePercent}% Match</span>
          </div>
        </div>
        <div class="mt-1 text-muted small">Click to view conversation and profile</div>
      </div>
    `;
  }).join('');
}

// Handle click on a match item
function handleMatchClick(event) {
  const matchItem = event.currentTarget;
  let conversation = [];
  
  try {
    conversation = JSON.parse(matchItem.dataset.conversation || '[]');
  } catch (error) {
    console.error('Error parsing conversation data:', error);
  }
  
  if (!conversation || conversation.length === 0) {
    document.getElementById('conversation-title').textContent = 'No conversation available';
    document.getElementById('conversation-messages').innerHTML = '<div class="text-center my-4">No messages found for this match.</div>';
    document.getElementById('conversation-view').style.display = 'block';
    document.getElementById('conversation-view').scrollIntoView({ behavior: 'smooth' });
    return;
  }
  
  const userId = matchItem.dataset.userId;
  const partnerId = matchItem.dataset.partnerId;
  
  // Get user names from the conversation
  const firstMessage = conversation[0] || '';
  const firstColonIndex = firstMessage.indexOf(':');
  const userName1 = firstColonIndex > 0 ? firstMessage.substring(0, firstColonIndex).trim() : 'User 1';
  
  const secondMessage = conversation.length > 1 ? conversation[1] : firstMessage;
  const secondColonIndex = secondMessage.indexOf(':');
  const userName2 = secondColonIndex > 0 ? secondMessage.substring(0, secondColonIndex).trim() : 'User 2';
  
  // Set conversation title
  document.getElementById('conversation-title').textContent = `Conversation between ${userName1} and ${userName2}`;
  
  // Clear existing messages
  const messagesContainer = document.getElementById('conversation-messages');
  messagesContainer.innerHTML = '';
  
  // Get the profile info to display
  fetchAndDisplayUserPrompts(partnerId);
  
  // Stream the messages for a more realistic chat appearance
  streamMessages(conversation, messagesContainer);
  
  // Show the conversation view
  document.getElementById('conversation-view').style.display = 'block';
  document.getElementById('conversation-view').scrollIntoView({ behavior: 'smooth' });
}

// Function to fetch and display user prompts
async function fetchAndDisplayUserPrompts(userId) {
  try {
    // Fetch the current profiles
    const response = await fetch(`${API_BASE_URL}/api/generate-profiles`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Get-Current-Only': 'true'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch profiles');
    }
    
    const data = await response.json();
    const profiles = data.profiles || [];
    
    // Find the profile with the matching ID
    const profile = profiles.find(p => p.id.toString() === userId.toString());
    
    if (profile) {
      // Create a section for profile details at the top of the conversation
      const messagesContainer = document.getElementById('conversation-messages');
      
      // Create profile header
      const profileHeader = document.createElement('div');
      profileHeader.className = 'profile-details mb-4 p-3 bg-light rounded';
      
      // Display personality and prompt answers
      let promptAnswersHtml = '';
      if (profile.prompt_answers && profile.prompt_answers.length > 0) {
        promptAnswersHtml = profile.prompt_answers.map(pa => `
          <div class="prompt-answer mb-2">
            <div class="prompt-question fw-bold">${pa.prompt}</div>
            <div class="prompt-response fst-italic">${pa.answer}</div>
          </div>
        `).join('');
      }
      
      profileHeader.innerHTML = `
        <h5 class="mb-3">${profile.name}'s Profile</h5>
        <div class="mb-2"><strong>Age:</strong> ${profile.age}</div>
        <div class="mb-2"><strong>Bio:</strong> ${profile.bio}</div>
        <div class="mb-3">
          <strong>Interests:</strong><br>
          ${(profile.interests || []).map(interest => 
            `<span class="interest-tag">${interest}</span>`
          ).join('')}
        </div>
        <div class="mb-2"><strong>Personality:</strong> <span class="fw-normal">${profile.personality || 'Not specified'}</span></div>
        
        <div class="mt-3">
          <h6 class="mb-2">Prompt Answers:</h6>
          ${promptAnswersHtml || '<div class="text-muted">No prompt answers available</div>'}
        </div>
      `;
      
      // Insert the profile details at the beginning of the conversation
      messagesContainer.insertBefore(profileHeader, messagesContainer.firstChild);
    }
  } catch (error) {
    console.error('Error fetching user profile:', error);
  }
}

// Stream messages for a more realistic chat appearance
function streamMessages(conversation, container) {
  if (!conversation || !Array.isArray(conversation) || conversation.length === 0) {
    container.innerHTML = '<div class="text-center my-4">No messages to display.</div>';
    return;
  }
  
  // Store messages with their elements for streaming
  const messageElements = [];
  
  // Create message elements
  conversation.forEach((message, index) => {
    // Skip empty messages
    if (!message || message.trim() === '') return;
    
    // Parse user and message content
    const colonIndex = message.indexOf(':');
    if (colonIndex < 0) return;
    
    const userName = message.substring(0, colonIndex).trim();
    const messageText = message.substring(colonIndex + 1).trim();
    
    // Determine if message is from first user or second user
    const isFirstUser = index % 2 === 0;
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${isFirstUser ? 'left' : 'right'}`;
    messageDiv.innerHTML = `
      <div class="message-bubble">
        <div><strong>${userName}</strong></div>
        <div class="message-content"></div>
      </div>
    `;
    
    container.appendChild(messageDiv);
    messageElements.push({
      element: messageDiv.querySelector('.message-content'),
      text: messageText
    });
  });
  
  // Stream messages with a typing effect
  function typeMessages(index, charIndex) {
    if (index >= messageElements.length) return;
    
    const { element, text } = messageElements[index];
    
    if (charIndex <= text.length) {
      element.textContent = text.substring(0, charIndex);
      
      // Typing speed varies slightly for realism
      setTimeout(() => typeMessages(index, charIndex + 1), 15 + Math.random() * 10);
    } else {
      // Add typing indicator to the next message before displaying it
      if (index + 1 < messageElements.length) {
        const nextMessageEl = messageElements[index + 1].element;
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span class="typing-circle"></span><span class="typing-circle"></span><span class="typing-circle"></span>';
        nextMessageEl.appendChild(typingIndicator);
      }
      
      // Move to next message after a delay (simulates thinking time)
      setTimeout(() => {
        // Remove typing indicator if it was added
        if (index + 1 < messageElements.length) {
          const nextMessageEl = messageElements[index + 1].element;
          const indicator = nextMessageEl.querySelector('.typing-indicator');
          if (indicator) indicator.remove();
        }
        
        // Start typing the next message
        typeMessages(index + 1, 0);
      }, 500 + Math.random() * 1000);
      
      // Scroll to the bottom
      container.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }
  
  // Start typing the first message after a short delay
  setTimeout(() => typeMessages(0, 0), 500);
}

// Test API connection and show diagnostic info
async function testApiConnection() {
  console.log('Testing API connection to:', `${API_BASE_URL}/api/status`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/status`, {
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (response.ok) {
      console.log('API connection successful');
      updateStatusBanner('Connected to server', 'success');
      return true;
    } else {
      console.log('API connection failed with status:', response.status);
      updateStatusBanner(`Error connecting to server: HTTP ${response.status}`, 'error');
      return false;
    }
  } catch (error) {
    console.error('API connection error:', error);
    updateStatusBanner(`Error connecting to server: ${error.message}`, 'error');
    return false;
  }
} 