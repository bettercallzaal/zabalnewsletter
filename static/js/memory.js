// Memory & Voice Management

let currentMemory = null;

// Load memory when tab is opened
async function loadMemory() {
    try {
        const response = await fetch('/memory/get');
        const data = await response.json();
        
        if (data.success) {
            currentMemory = data.memory;
            displayMemory();
        }
    } catch (error) {
        console.error('Failed to load memory:', error);
    }
}

// Display all memory sections
function displayMemory() {
    if (!currentMemory) return;
    
    displayVoiceExamples();
    displayVoiceDonts();
    displayStyleNotes();
    displayContextMemories();
}

// Voice Examples
function displayVoiceExamples() {
    const container = document.getElementById('voice-examples-list');
    if (!currentMemory.voice_examples || currentMemory.voice_examples.length === 0) {
        container.innerHTML = '<p style="color: #999; font-style: italic;">No voice examples yet. Add your actual writing to help the AI match your style.</p>';
        return;
    }
    
    container.innerHTML = currentMemory.voice_examples.map((example, index) => `
        <div class="memory-item">
            <strong>${example.title}</strong>
            <p style="margin: 8px 0; color: #666; font-size: 0.9rem;">${example.content.substring(0, 150)}...</p>
            <button onclick="removeVoiceExample(${index})" class="btn-remove">Remove</button>
        </div>
    `).join('');
}

function showAddVoiceExample() {
    document.getElementById('add-voice-example-form').style.display = 'block';
}

function cancelAddVoiceExample() {
    document.getElementById('add-voice-example-form').style.display = 'none';
    document.getElementById('voice-example-title').value = '';
    document.getElementById('voice-example-content').value = '';
}

async function addVoiceExample() {
    const title = document.getElementById('voice-example-title').value;
    const content = document.getElementById('voice-example-content').value;
    
    if (!title || !content) {
        alert('Please fill in both title and content');
        return;
    }
    
    try {
        const response = await fetch('/memory/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'voice_example',
                title: title,
                content: content
            })
        });
        
        if (response.ok) {
            cancelAddVoiceExample();
            await loadMemory();
        }
    } catch (error) {
        alert('Failed to add voice example');
    }
}

async function removeVoiceExample(index) {
    currentMemory.voice_examples.splice(index, 1);
    await saveMemory();
}

// Voice Don'ts
function displayVoiceDonts() {
    const container = document.getElementById('voice-donts-list');
    if (!currentMemory.voice_donts || currentMemory.voice_donts.length === 0) {
        container.innerHTML = '<p style="color: #999; font-style: italic;">No phrases to avoid yet.</p>';
        return;
    }
    
    container.innerHTML = '<div class="tags-container">' + 
        currentMemory.voice_donts.map((phrase, index) => `
            <span class="tag">
                ${phrase}
                <button onclick="removeVoiceDont(${index})" class="tag-remove">×</button>
            </span>
        `).join('') + 
        '</div>';
}

async function addVoiceDont() {
    const input = document.getElementById('voice-dont-input');
    const phrase = input.value.trim();
    
    if (!phrase) return;
    
    try {
        const response = await fetch('/memory/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'voice_dont',
                content: phrase
            })
        });
        
        if (response.ok) {
            input.value = '';
            await loadMemory();
        }
    } catch (error) {
        alert('Failed to add phrase');
    }
}

async function removeVoiceDont(index) {
    currentMemory.voice_donts.splice(index, 1);
    await saveMemory();
}

// Style Notes
function displayStyleNotes() {
    const container = document.getElementById('style-notes-list');
    if (!currentMemory.style_notes || currentMemory.style_notes.length === 0) {
        container.innerHTML = '<p style="color: #999; font-style: italic;">No style notes yet.</p>';
        return;
    }
    
    container.innerHTML = '<ul style="list-style: disc; padding-left: 20px;">' +
        currentMemory.style_notes.map((note, index) => `
            <li style="margin: 8px 0;">
                ${note}
                <button onclick="removeStyleNote(${index})" class="btn-remove" style="margin-left: 8px;">Remove</button>
            </li>
        `).join('') +
        '</ul>';
}

async function addStyleNote() {
    const input = document.getElementById('style-note-input');
    const note = input.value.trim();
    
    if (!note) return;
    
    try {
        const response = await fetch('/memory/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'style_note',
                content: note
            })
        });
        
        if (response.ok) {
            input.value = '';
            await loadMemory();
        }
    } catch (error) {
        alert('Failed to add style note');
    }
}

async function removeStyleNote(index) {
    currentMemory.style_notes.splice(index, 1);
    await saveMemory();
}

// Context Memories
function displayContextMemories() {
    const container = document.getElementById('context-memories-list');
    if (!currentMemory.context_memories || currentMemory.context_memories.length === 0) {
        container.innerHTML = '<p style="color: #999; font-style: italic;">No context memories yet.</p>';
        return;
    }
    
    container.innerHTML = '<ul style="list-style: disc; padding-left: 20px;">' +
        currentMemory.context_memories.map((memory, index) => `
            <li style="margin: 8px 0;">
                ${memory}
                <button onclick="removeContextMemory(${index})" class="btn-remove" style="margin-left: 8px;">Remove</button>
            </li>
        `).join('') +
        '</ul>';
}

async function addContextMemory() {
    const input = document.getElementById('context-memory-input');
    const memory = input.value.trim();
    
    if (!memory) return;
    
    try {
        const response = await fetch('/memory/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'context',
                content: memory
            })
        });
        
        if (response.ok) {
            input.value = '';
            await loadMemory();
        }
    } catch (error) {
        alert('Failed to add context memory');
    }
}

async function removeContextMemory(index) {
    currentMemory.context_memories.splice(index, 1);
    await saveMemory();
}

// Save entire memory
async function saveMemory() {
    try {
        const response = await fetch('/memory/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ memory: currentMemory })
        });
        
        if (response.ok) {
            await loadMemory();
        }
    } catch (error) {
        alert('Failed to save memory');
    }
}

// Load memory when memory tab is opened
const originalShowTab = window.showTab;
window.showTab = function(tabName) {
    originalShowTab.call(this, tabName);
    if (tabName === 'memory') {
        loadMemory();
    }
};
