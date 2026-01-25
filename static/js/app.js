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

// Newsletter form submission
document.getElementById('newsletter-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const dailyInput = document.getElementById('daily-input').value;
    const badassQuote = document.getElementById('badass-quote').value;
    
    showLoading(true);
    
    try {
        const response = await fetch('/generate/newsletter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                daily_input: dailyInput,
                badass_quote: badassQuote
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show output
            document.getElementById('newsletter-output').style.display = 'block';
            document.getElementById('newsletter-content').textContent = data.newsletter;
            document.getElementById('day-info').textContent = `Day ${data.day_num} - ${data.date}`;
            document.getElementById('newsletter-saved').textContent = `✓ Saved to: ${data.filepath}`;
            
            // Store for social generation
            window.currentNewsletter = data.newsletter;
            
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
    const content = document.getElementById(elementId).textContent;
    
    try {
        await navigator.clipboard.writeText(content);
        
        // Show feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        btn.style.background = '#28a745';
        btn.style.borderColor = '#28a745';
        btn.style.color = 'white';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
            btn.style.borderColor = '';
            btn.style.color = '';
        }, 2000);
    } catch (error) {
        alert('Failed to copy to clipboard');
    }
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
