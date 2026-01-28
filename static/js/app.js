// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
    
    // Load history if history tab is selected
    if (tabName === 'history') {
        loadHistory();
    }
}

// Show/hide Roj context input based on lens selection
document.getElementById('lens-override').addEventListener('change', function(e) {
    const rojContextGroup = document.getElementById('roj-context-group');
    if (e.target.value === 'zoroastrian_roj') {
        rojContextGroup.style.display = 'block';
    } else {
        rojContextGroup.style.display = 'none';
    }
});

// Toggle advanced parameters section
function toggleAdvancedParams() {
    const paramsDiv = document.getElementById('advanced-params');
    if (paramsDiv.style.display === 'none') {
        paramsDiv.style.display = 'block';
    } else {
        paramsDiv.style.display = 'none';
    }
}

// Regenerate newsletter with current form values
function regenerateNewsletter() {
    // Scroll to form
    document.getElementById('newsletter-tab').scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Highlight the generate button briefly
    const btn = document.querySelector('#newsletter-form button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = '🔄 Click to Regenerate';
    btn.style.background = '#f59e0b';
    
    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
    }, 2000);
}

// Scroll to form for editing
function scrollToForm() {
    document.getElementById('newsletter-tab').scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.getElementById('daily-input').focus();
}

// Update slider value display
function updateSliderValue(sliderId) {
    const slider = document.getElementById(sliderId);
    const valueSpan = document.getElementById(sliderId + '-value');
    valueSpan.textContent = slider.value;
}

// Reset all parameters to defaults
function resetParameters() {
    const defaults = {
        'temperature': 0.7,
        'top_p': 0.9,
        'frequency_penalty': 0.3,
        'presence_penalty': 0.3,
        'formality': 4,
        'energy_level': 5,
        'reflection_depth': 6,
        'personal_universal': 6
    };
    
    for (const [id, value] of Object.entries(defaults)) {
        const slider = document.getElementById(id);
        if (slider) {
            slider.value = value;
            updateSliderValue(id);
        }
    }
}

// Newsletter form submission
document.getElementById('newsletter-form').addEventListener('submit', async function generateNewsletter(e) {
    e.preventDefault();
    
    const dailyInput = document.getElementById('daily-input').value;
    const badassQuote = document.getElementById('badass-quote').value;
    const lensOverride = document.getElementById('lens-override').value;
    const rojContext = document.getElementById('roj-context').value;
    const editingInstructions = document.getElementById('editing-instructions').value;
    
    // Collect all parameter values
    const parameters = {
        temperature: parseFloat(document.getElementById('temperature').value),
        top_p: parseFloat(document.getElementById('top_p').value),
        frequency_penalty: parseFloat(document.getElementById('frequency_penalty').value),
        presence_penalty: parseFloat(document.getElementById('presence_penalty').value),
        formality: parseInt(document.getElementById('formality').value),
        energy_level: parseInt(document.getElementById('energy_level').value),
        reflection_depth: parseInt(document.getElementById('reflection_depth').value),
        personal_universal: parseInt(document.getElementById('personal_universal').value)
    };
    
    if (!dailyInput) {
        showError('Please enter your daily input');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/generate/newsletter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                daily_input: dailyInput,
                badass_quote: badassQuote,
                lens_override: lensOverride !== 'auto' ? lensOverride : null,
                roj_context: rojContext || null,
                editing_instructions: editingInstructions || null,
                parameters: parameters
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show output
            document.getElementById('newsletter-output').style.display = 'block';
            
            // Display as plain text with preserved formatting
            const contentDiv = document.getElementById('newsletter-content');
            contentDiv.textContent = data.newsletter;
            
            document.getElementById('day-info').textContent = `Day ${data.day_num} - ${data.date}`;
            document.getElementById('newsletter-saved').textContent = `✓ Saved to: ${data.filepath}`;
            
            // Store for social generation
            window.currentNewsletter = data.newsletter;
            
            // Scroll to output
            document.getElementById('newsletter-output').scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Scroll to output
            document.getElementById('newsletter-output').scrollIntoView({ behavior: 'smooth' });
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Failed to generate newsletter: ' + error.message);
    } finally {
        showLoading(false);
    }
});

// Social form submission
document.getElementById('social-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newsletterContent = document.getElementById('newsletter-content-input').value;
    const newsletterLink = document.getElementById('newsletter-link').value;
    const hasVideo = document.getElementById('has-video').checked;
    
    showLoading(true);
    
    try {
        const response = await fetch('/generate/social', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                newsletter_content: newsletterContent,
                newsletter_link: newsletterLink,
                has_video: hasVideo
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show output
            document.getElementById('social-output').style.display = 'block';
            document.getElementById('social-content').textContent = data.social_content;
            document.getElementById('social-saved').textContent = `✓ Saved to: ${data.filepath}`;
            
            // Scroll to output
            document.getElementById('social-output').scrollIntoView({ behavior: 'smooth' });
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Failed to generate social content: ' + error.message);
    } finally {
        showLoading(false);
    }
});

// Generate social from newsletter
function generateSocialFromNewsletter() {
    if (window.currentNewsletter) {
        // Switch to social tab
        showTab('social');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
        
        // Fill in the newsletter content
        document.getElementById('newsletter-content-input').value = window.currentNewsletter;
        
        // Scroll to form
        document.getElementById('social-tab').scrollIntoView({ behavior: 'smooth' });
    }
}

// Copy to clipboard
async function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const content = element.textContent;
    
    try {
        // Try modern clipboard API first
        await navigator.clipboard.writeText(content);
        showCopySuccess();
    } catch (error) {
        // Fallback: select text for manual copy
        const range = document.createRange();
        range.selectNodeContents(element);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        try {
            // Try execCommand as second fallback
            const success = document.execCommand('copy');
            selection.removeAllRanges();
            
            if (success) {
                showCopySuccess();
            } else {
                // Text is selected, show instruction
                showCopyInstruction();
            }
        } catch (err) {
            // Text is already selected, just show instruction
            showCopyInstruction();
        }
    }
}

function showCopySuccess() {
    const btn = event.target;
    const originalText = btn.textContent;
    const originalStyle = {
        background: btn.style.background,
        borderColor: btn.style.borderColor,
        color: btn.style.color
    };
    
    btn.textContent = '✓ Copied!';
    btn.style.background = '#10b981';
    btn.style.borderColor = '#10b981';
    btn.style.color = 'white';
    
    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = originalStyle.background;
        btn.style.borderColor = originalStyle.borderColor;
        btn.style.color = originalStyle.color;
    }, 2000);
}

function showCopyInstruction() {
    const btn = event.target;
    const originalText = btn.textContent;
    
    btn.textContent = 'Press Cmd+C / Ctrl+C';
    btn.style.background = '#f59e0b';
    btn.style.borderColor = '#f59e0b';
    btn.style.color = 'white';
    
    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
        btn.style.borderColor = '';
        btn.style.color = '';
    }, 3000);
}

// Load history
async function loadHistory() {
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = '<p class="loading">Loading...</p>';
    
    try {
        const response = await fetch('/history/newsletters');
        const data = await response.json();
        
        if (data.newsletters && data.newsletters.length > 0) {
            historyList.innerHTML = '';
            data.newsletters.forEach(newsletter => {
                const item = document.createElement('div');
                item.className = 'history-item';
                item.innerHTML = `
                    <h4>${newsletter.title}</h4>
                    <p>${newsletter.filename}</p>
                `;
                item.onclick = () => loadNewsletterContent(newsletter.filename);
                historyList.appendChild(item);
            });
        } else {
            historyList.innerHTML = '<p class="loading">No newsletters found</p>';
        }
    } catch (error) {
        historyList.innerHTML = '<p class="error">Failed to load history</p>';
    }
}

// Load newsletter content
async function loadNewsletterContent(filename) {
    try {
        const response = await fetch(`/history/newsletter/${filename}`);
        const data = await response.json();
        
        if (data.success) {
            // Switch to social tab and fill in content
            showTab('social');
            document.querySelectorAll('.tab-btn')[1].classList.add('active');
            document.getElementById('newsletter-content-input').value = data.content;
        }
    } catch (error) {
        showError('Failed to load newsletter');
    }
}

// Show/hide loading overlay
function showLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    
    const container = document.querySelector('.tab-content.active .form-section');
    container.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Load prompt content
async function loadPrompt() {
    const promptType = document.getElementById('prompt-type-select').value;
    
    try {
        const response = await fetch(`/prompts/get/${promptType}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('current-prompt-display').value = data.content;
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Failed to load prompt: ' + error.message);
    }
}

// Improve prompt with AI
async function improvePrompt() {
    const promptType = document.getElementById('prompt-type-select').value;
    const currentPrompt = document.getElementById('current-prompt-display').value;
    const feedback = document.getElementById('prompt-feedback').value;
    
    if (!feedback.trim()) {
        showError('Please provide feedback on how to improve the prompt');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/prompts/improve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt_type: promptType,
                current_prompt: currentPrompt,
                feedback: feedback
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('improved-prompt-section').style.display = 'block';
            document.getElementById('improved-prompt-content').value = data.improved_prompt;
            
            // Store for saving
            window.improvedPromptType = promptType;
            
            // Scroll to output
            document.getElementById('improved-prompt-section').scrollIntoView({ behavior: 'smooth' });
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Failed to improve prompt: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Save improved prompt
async function saveImprovedPrompt() {
    const promptType = window.improvedPromptType;
    const content = document.getElementById('improved-prompt-content').value;
    
    if (!confirm('This will replace your current prompt. The old version will be backed up. Continue?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/prompts/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt_type: promptType,
                content: content
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✓ Prompt saved successfully! Backup created in prompts/backups/');
            
            // Reload the current prompt display
            loadPrompt();
            
            // Clear feedback
            document.getElementById('prompt-feedback').value = '';
            
            // Hide improved section
            document.getElementById('improved-prompt-section').style.display = 'none';
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Failed to save prompt: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Load prompt when prompts tab is opened
const originalShowTab = showTab;
showTab = function(tabName) {
    originalShowTab.call(this, tabName);
    if (tabName === 'prompts') {
        loadPrompt();
    }
};
