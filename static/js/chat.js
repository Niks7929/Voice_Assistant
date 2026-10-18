// CodeVocalis AI - Chat & Code Engine Module

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-messages-container');
    const currentConvInput = document.getElementById('current-conv-id');
    const currentDocInput = document.getElementById('current-doc-id');
    const btnNewChat = document.getElementById('btn-new-chat');
    const activeChatTitle = document.getElementById('active-chat-title');
    const activeToolBadge = document.getElementById('active-tool-badge');
    const docFileInput = document.getElementById('doc-file-input');
    const sidebarConvList = document.getElementById('sidebar-conv-list');
    const btnClearHistory = document.getElementById('btn-clear-history');

    // URL Modal elements
    const urlModal = document.getElementById('url-modal');
    const btnOpenUrlModal = document.getElementById('btn-open-url-modal');
    const btnCloseUrlModal = document.getElementById('btn-close-url-modal');
    const btnCancelUrl = document.getElementById('btn-cancel-url');
    const btnSubmitUrl = document.getElementById('btn-submit-url');
    const urlInput = document.getElementById('url-input');

    // Attachment banner
    const attachmentBanner = document.getElementById('active-attachment-banner');
    const attachmentName = document.getElementById('active-attachment-name');
    const btnRemoveAttachment = document.getElementById('btn-remove-attachment');

    function getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    function scrollToBottom() {
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    // Markdown Parser for Code Blocks and Text Formatting
    function formatMarkdownResponse(rawText) {
        if (!rawText) return '';

        // 1. Parse fenced code blocks: ```lang ... ```
        const codeBlockRegex = /```([a-zA-Z0-9_\-+]*)\n([\s\S]*?)```/g;
        let formatted = rawText.replace(codeBlockRegex, (match, lang, code) => {
            const displayLang = (lang || 'code').toUpperCase();
            const prismLang = (lang || 'javascript').toLowerCase();
            const escapedCode = escapeHTML(code.trim());

            return `
                <div class="my-3 rounded-2xl border border-slate-800 bg-slate-950 overflow-hidden shadow-xl">
                    <div class="flex items-center justify-between border-b border-slate-800/80 bg-slate-900/90 px-4 py-2 text-xs font-mono">
                        <span class="text-indigo-400 font-bold flex items-center gap-1.5">
                            <i class="fa-solid fa-code text-[10px]"></i> ${displayLang}
                        </span>
                        <button type="button" class="btn-copy-code text-slate-400 hover:text-white flex items-center gap-1 transition-colors px-2 py-1 rounded-lg hover:bg-slate-800">
                            <i class="fa-regular fa-copy"></i> <span>Copy</span>
                        </button>
                    </div>
                    <pre class="p-4 overflow-x-auto text-xs leading-relaxed text-slate-200 font-mono"><code class="language-${prismLang}">${escapedCode}</code></pre>
                </div>
            `;
        });

        // 2. Parse inline code: `code`
        formatted = formatted.replace(/`([^`]+)`/g, '<code class="bg-slate-800/80 text-indigo-300 px-1.5 py-0.5 rounded text-[11px] font-mono border border-slate-700/50">$1</code>');

        // 3. Parse headers: ### Header
        formatted = formatted.replace(/^### (.*$)/gim, '<h4 class="text-sm font-bold text-white mt-3 mb-1.5">$1</h4>');
        formatted = formatted.replace(/^## (.*$)/gim, '<h3 class="text-base font-bold text-white mt-4 mb-2">$1</h3>');

        // 4. Parse bold: **text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-white">$1</strong>');

        // 5. Parse bullet lists: - list item
        formatted = formatted.replace(/^\s*-\s+(.*$)/gim, '<li class="ml-4 list-disc text-slate-300 text-xs leading-relaxed">$1</li>');

        // 6. Convert newlines to paragraphs/breaks
        formatted = formatted.replace(/\n\n+/g, '<p class="my-2"></p>');

        return formatted;
    }

    // Extract Text for Speech (Omit Code Blocks for natural audio)
    function extractSpokenText(rawText) {
        if (!rawText) return '';
        // Remove fenced code blocks
        let clean = rawText.replace(/```[\s\S]*?```/g, ' [Code example displayed on screen] ');
        // Remove markdown symbols
        clean = clean.replace(/#{1,6}\s*/g, '');
        clean = clean.replace(/\*{1,2}/g, '');
        clean = clean.replace(/`([^`]+)`/g, '$1');
        clean = clean.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');
        clean = clean.replace(/\s+/g, ' ').trim();
        if (clean.length > 500) {
            clean = clean.substring(0, 500) + "... and more details provided in code.";
        }
        return clean;
    }

    // Append User Message to UI
    function appendUserMessage(text) {
        const welcomeCanvas = document.getElementById('welcome-canvas');
        if (welcomeCanvas) welcomeCanvas.remove();

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const userHtml = `
            <div class="flex justify-end animate-fade-in">
                <div class="max-w-2xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-3xl rounded-tr-none shadow-lg shadow-indigo-500/10 space-y-1">
                    <div class="flex items-center gap-2 text-xs font-semibold text-blue-200 mb-1">
                        <i class="fa-solid fa-user"></i> You
                    </div>
                    <p class="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">${escapeHTML(text)}</p>
                    <span class="text-[10px] text-blue-200/80 block text-right pt-1">${timeStr}</span>
                </div>
            </div>
        `;
        chatContainer.insertAdjacentHTML('beforeend', userHtml);
        scrollToBottom();
    }

    // Append Typing / Reasoning Indicator
    function showTypingIndicator() {
        const typingId = 'typing-indicator-' + Date.now();
        const typingHtml = `
            <div class="flex justify-start animate-fade-in" id="${typingId}">
                <div class="max-w-2xl bg-slate-900 border border-slate-800 p-4 rounded-3xl rounded-tl-none shadow-md">
                    <div class="flex items-center gap-2 text-xs font-bold text-indigo-400 mb-2">
                        <i class="fa-solid fa-robot"></i> CodeVocalis AI
                    </div>
                    <div class="flex items-center gap-2 py-1">
                        <div class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0s"></div>
                        <div class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0.15s"></div>
                        <div class="w-2 h-2 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0.3s"></div>
                        <span class="text-xs text-slate-400 font-mono ml-2">Synthesizing code solution...</span>
                    </div>
                </div>
            </div>
        `;
        chatContainer.insertAdjacentHTML('beforeend', typingHtml);
        scrollToBottom();
        return typingId;
    }

    // Append AI Response to UI
    function appendAIMessage(rawText, data) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const toolName = data && data.tool_used ? data.tool_used : 'CODE_AI';
        const msgId = data && data.message_id ? data.message_id : '';
        const parsedContent = formatMarkdownResponse(rawText);

        const aiHtml = `
            <div class="flex justify-start animate-fade-in" data-msg-id="${msgId}">
                <div class="max-w-3xl w-full bg-slate-900/90 border border-slate-800/90 p-5 rounded-3xl rounded-tl-none shadow-xl space-y-3">
                    <div class="flex items-center justify-between gap-4 text-xs font-semibold text-indigo-400 border-b border-slate-800/80 pb-2">
                        <span class="flex items-center gap-2">
                            <i class="fa-solid fa-code"></i> CodeVocalis AI
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                                ${toolName}
                            </span>
                        </span>

                        <!-- Action Toolbar -->
                        <div class="flex items-center gap-3 text-slate-400">
                            <button type="button" class="btn-read-aloud hover:text-indigo-400 transition-colors" data-raw="${escapeHTML(rawText)}" title="Read Aloud">
                                <i class="fa-solid fa-volume-high"></i>
                            </button>
                            <button type="button" class="btn-copy-full hover:text-indigo-400 transition-colors" data-raw="${escapeHTML(rawText)}" title="Copy Full Text">
                                <i class="fa-regular fa-copy"></i>
                            </button>
                            <button type="button" class="btn-feedback-like hover:text-emerald-400 transition-colors" title="Helpful response">
                                <i class="fa-regular fa-thumbs-up"></i>
                            </button>
                            <button type="button" class="btn-feedback-dislike hover:text-rose-400 transition-colors" title="Not helpful">
                                <i class="fa-regular fa-thumbs-down"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Content -->
                    <div class="text-xs sm:text-sm text-slate-300 leading-relaxed space-y-2 ai-content">
                        ${parsedContent}
                    </div>

                    <span class="text-[10px] text-slate-500 block pt-1">${timeStr}</span>
                </div>
            </div>
        `;
        chatContainer.insertAdjacentHTML('beforeend', aiHtml);
        
        // Highlight with Prism if available
        if (window.Prism) {
            Prism.highlightAllUnder(chatContainer);
        }
        scrollToBottom();
    }

    function escapeHTML(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    // Submit question to Flask Backend
    window.submitChatQuestion = function(questionText) {
        if (!questionText || questionText.trim() === '') return;

        const convId = currentConvInput ? currentConvInput.value : null;
        const docId = currentDocInput ? currentDocInput.value : null;

        // Display user message in UI
        appendUserMessage(questionText);
        if (chatInput) chatInput.value = '';

        if (window.voiceAssistant) {
            window.voiceAssistant.updateState('processing');
        }

        const typingIndicatorId = showTypingIndicator();

        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                question: questionText,
                conversation_id: convId ? parseInt(convId) : null,
                document_id: docId ? parseInt(docId) : null
            })
        })
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            return response.json();
        })
        .then(data => {
            const typingElem = document.getElementById(typingIndicatorId);
            if (typingElem) typingElem.remove();

            if (!data) return;

            if (data.status === 'success') {
                if (currentConvInput) currentConvInput.value = data.conversation_id;
                if (activeChatTitle && data.conversation_title) {
                    activeChatTitle.innerText = data.conversation_title;
                }
                if (activeToolBadge && data.tool_used) {
                    activeToolBadge.innerText = data.tool_used;
                }

                const aiRawText = data.answer;
                appendAIMessage(aiRawText, data);

                // Add to sidebar if new
                updateSidebarAfterNewChat(data.conversation_id, data.conversation_title);

                // Voice synthesis: speak concise explanation
                if (window.voiceAssistant) {
                    const spokenExplanation = extractSpokenText(aiRawText);
                    window.voiceAssistant.speak(spokenExplanation);
                }
            } else {
                appendAIMessage("Sorry, an error occurred while processing your code query: " + (data.message || "Unknown error"));
                if (window.voiceAssistant) window.voiceAssistant.updateState('ready');
            }
        })
        .catch(err => {
            console.error("Chat API error:", err);
            const typingElem = document.getElementById(typingIndicatorId);
            if (typingElem) typingElem.remove();

            appendAIMessage("Sorry, a network connection error occurred. Please verify your internet connection.");
            if (window.voiceAssistant) window.voiceAssistant.updateState('ready');
        });
    };

    function updateSidebarAfterNewChat(convId, convTitle) {
        if (!sidebarConvList || !convId) return;
        const existing = sidebarConvList.querySelector(`[data-conv-id="${convId}"]`);
        if (!existing) {
            const emptyTxt = document.getElementById('empty-history-text');
            if (emptyTxt) emptyTxt.remove();

            const itemHtml = `
                <div class="group flex items-center justify-between rounded-xl px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800/80 cursor-pointer transition-colors conv-item" data-conv-id="${convId}">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <i class="fa-regular fa-message text-indigo-400 flex-shrink-0"></i>
                        <span class="truncate conv-title">${escapeHTML(convTitle || 'New Code Session')}</span>
                    </div>
                    <button type="button" class="btn-delete-conv opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 p-1 transition-opacity" data-conv-id="${convId}" title="Delete chat">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                </div>
            `;
            sidebarConvList.insertAdjacentHTML('afterbegin', itemHtml);
        }
    }

    // Form submission
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const q = chatInput.value.trim();
            if (q) {
                window.submitChatQuestion(q);
            }
        });
    }

    // New Conversation
    if (btnNewChat) {
        btnNewChat.addEventListener('click', () => {
            if (currentConvInput) currentConvInput.value = '';
            if (currentDocInput) currentDocInput.value = '';
            if (attachmentBanner) attachmentBanner.classList.add('hidden');
            if (activeChatTitle) activeChatTitle.innerText = 'New Code Session';
            if (activeToolBadge) activeToolBadge.innerText = 'PROGRAMMING_AI';
            
            chatContainer.innerHTML = `
                <div class="h-full flex flex-col items-center justify-center text-center p-8 max-w-xl mx-auto" id="welcome-canvas">
                    <div class="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center text-2xl mb-4 shadow-inner">
                        <i class="fa-solid fa-code"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-2">CodeVocalis Programming Assistant</h3>
                    <p class="text-xs text-slate-400 mb-6 leading-relaxed">
                        Click the microphone below to speak your coding question, or type in the console box. You can ask about any programming language, framework, algorithm, or bug.
                    </p>
                    <div class="flex flex-wrap gap-2 justify-center">
                        <button type="button" class="sample-prompt-btn text-xs bg-slate-900 border border-slate-800 text-slate-300 py-2 px-3 rounded-xl hover:border-indigo-500/50 hover:text-white transition-all">
                            "How to create a React component with useState and useEffect?"
                        </button>
                        <button type="button" class="sample-prompt-btn text-xs bg-slate-900 border border-slate-800 text-slate-300 py-2 px-3 rounded-xl hover:border-indigo-500/50 hover:text-white transition-all">
                            "Create a FastAPI route with Pydantic in Python"
                        </button>
                        <button type="button" class="sample-prompt-btn text-xs bg-slate-900 border border-slate-800 text-slate-300 py-2 px-3 rounded-xl hover:border-indigo-500/50 hover:text-white transition-all">
                            "Binary search algorithm in Python with complexity"
                        </button>
                    </div>
                </div>
            `;
            if (window.voiceAssistant) window.voiceAssistant.updateState('ready');
        });
    }

    // Document / Code File Upload
    if (docFileInput) {
        docFileInput.addEventListener('change', () => {
            if (!docFileInput.files || docFileInput.files.length === 0) return;

            const file = docFileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);
            formData.append('csrf_token', getCSRFToken());

            appendUserMessage(`[Attached Code File: ${file.name}]`);
            const typingId = showTypingIndicator();

            fetch('/api/document/upload', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();

                if (data.status === 'success') {
                    if (currentDocInput) currentDocInput.value = data.document.id;
                    if (attachmentName) attachmentName.innerText = `Active File: ${data.document.filename}`;
                    if (attachmentBanner) attachmentBanner.classList.remove('hidden');

                    appendAIMessage(`Successfully indexed '${data.document.filename}'. You can now ask questions about this code or document!`, { tool_used: 'DOCUMENT_QA' });
                } else {
                    appendAIMessage(`Failed to upload file: ${data.message}`);
                }
            })
            .catch(err => {
                console.error("Upload error:", err);
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();
                appendAIMessage("Network error while uploading code file.");
            });
        });
    }

    // Remove Attachment Context
    if (btnRemoveAttachment) {
        btnRemoveAttachment.addEventListener('click', () => {
            if (currentDocInput) currentDocInput.value = '';
            if (attachmentBanner) attachmentBanner.classList.add('hidden');
        });
    }

    // URL Modal Open / Close
    if (btnOpenUrlModal && urlModal) {
        btnOpenUrlModal.addEventListener('click', () => urlModal.classList.remove('hidden'));
    }
    if (btnCloseUrlModal && urlModal) {
        btnCloseUrlModal.addEventListener('click', () => urlModal.classList.add('hidden'));
    }
    if (btnCancelUrl && urlModal) {
        btnCancelUrl.addEventListener('click', () => urlModal.classList.add('hidden'));
    }

    // URL Submit
    if (btnSubmitUrl && urlInput) {
        btnSubmitUrl.addEventListener('click', () => {
            const urlVal = urlInput.value.trim();
            if (!urlVal) return;
            urlModal.classList.add('hidden');

            appendUserMessage(`[Analyzing Web Docs: ${urlVal}]`);
            const typingId = showTypingIndicator();

            fetch('/api/document/analyze-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ url: urlVal })
            })
            .then(res => res.json())
            .then(data => {
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();

                if (data.status === 'success') {
                    if (currentDocInput) currentDocInput.value = data.document.id;
                    if (attachmentName) attachmentName.innerText = `Active URL: ${data.document.filename}`;
                    if (attachmentBanner) attachmentBanner.classList.remove('hidden');

                    appendAIMessage(`Scraped and indexed documentation from '${data.document.filename}'. What would you like to know about it?`, { tool_used: 'DOCS_QA' });
                } else {
                    appendAIMessage(`Error fetching URL: ${data.message}`);
                }
            })
            .catch(err => {
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();
                appendAIMessage("Error connecting to web URL.");
            });
        });
    }

    // ==============================================
    // API KEY MODAL LOGIC
    // ==============================================
    const apikeyModal = document.getElementById('apikey-modal');
    const btnOpenApiKeyModal = document.getElementById('btn-open-apikey-modal');
    const btnCloseApiKeyModal = document.getElementById('btn-close-apikey-modal');
    const btnCancelApiKey = document.getElementById('btn-cancel-apikey');
    const btnSubmitApiKey = document.getElementById('btn-submit-apikey');
    const apikeyInput = document.getElementById('apikey-input');
    const apikeyStatusText = document.getElementById('apikey-status-text');

    function checkApiKeyStatus() {
        if (!apikeyStatusText) return;
        fetch('/api/settings/apikey')
            .then(res => res.json())
            .then(data => {
                if (data.has_key) {
                    apikeyStatusText.innerHTML = `<span class="text-emerald-400 font-bold"><i class="fa-solid fa-circle-check"></i> Active (${data.key_preview})</span>`;
                    if (apikeyInput) apikeyInput.placeholder = "Key configured. Enter new key to change...";
                } else {
                    apikeyStatusText.innerHTML = `<span class="text-amber-400 font-bold"><i class="fa-solid fa-circle-exclamation"></i> Free Built-in Mode (Add Key for Gemini AI)</span>`;
                }
            })
            .catch(() => {
                if (apikeyStatusText) apikeyStatusText.innerText = "Ready";
            });
    }

    if (btnOpenApiKeyModal && apikeyModal) {
        btnOpenApiKeyModal.addEventListener('click', () => {
            apikeyModal.classList.remove('hidden');
            checkApiKeyStatus();
        });
    }
    if (btnCloseApiKeyModal && apikeyModal) {
        btnCloseApiKeyModal.addEventListener('click', () => apikeyModal.classList.add('hidden'));
    }
    if (btnCancelApiKey && apikeyModal) {
        btnCancelApiKey.addEventListener('click', () => apikeyModal.classList.add('hidden'));
    }

    if (btnSubmitApiKey && apikeyInput) {
        btnSubmitApiKey.addEventListener('click', () => {
            const keyVal = apikeyInput.value.trim();
            if (!keyVal) {
                alert("Please enter a valid Google Gemini API key (starts with AIzaSy...).");
                return;
            }
            btnSubmitApiKey.disabled = true;
            btnSubmitApiKey.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Activating...';

            fetch('/api/settings/apikey', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ api_key: keyVal })
            })
            .then(res => res.json())
            .then(data => {
                btnSubmitApiKey.disabled = false;
                btnSubmitApiKey.innerHTML = '<i class="fa-solid fa-check"></i> Save & Activate';

                if (data.status === 'success') {
                    if (apikeyModal) apikeyModal.classList.add('hidden');
                    apikeyInput.value = '';
                    appendAIMessage("🎉 **Google Gemini AI Activated!** You now have real-time ChatGPT/Gemini generative AI connected for all programming languages and frameworks.", { tool_used: 'GEMINI_CODE_AI' });
                } else {
                    alert(data.message || "Failed to save API key.");
                }
            })
            .catch(err => {
                btnSubmitApiKey.disabled = false;
                btnSubmitApiKey.innerHTML = '<i class="fa-solid fa-check"></i> Save & Activate';
                alert("Network error connecting to API key service.");
            });
        });
    }

    // Clear History Button
    if (btnClearHistory) {
        btnClearHistory.addEventListener('click', () => {
            if (confirm("Are you sure you want to clear all conversation history?")) {
                fetch('/api/chat/conversations/clear', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCSRFToken() }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        sidebarConvList.innerHTML = '<p class="px-3 py-3 text-xs text-slate-500 italic" id="empty-history-text">No previous conversations yet.</p>';
                        if (btnNewChat) btnNewChat.click();
                    }
                });
            }
        });
    }

    // Global Delegated Click Handler
    document.addEventListener('click', (e) => {
        // 1. Sample Prompt Chips
        const promptBtn = e.target.closest('.sample-prompt-btn');
        if (promptBtn) {
            const promptText = promptBtn.innerText.replace(/^"|"$/g, '');
            window.submitChatQuestion(promptText);
            return;
        }

        // 2. Copy Code Block Button
        const copyCodeBtn = e.target.closest('.btn-copy-code');
        if (copyCodeBtn) {
            const container = copyCodeBtn.closest('.rounded-2xl');
            const codeElem = container ? container.querySelector('code') : null;
            if (codeElem) {
                navigator.clipboard.writeText(codeElem.innerText);
                const originalHtml = copyCodeBtn.innerHTML;
                copyCodeBtn.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i> <span class="text-emerald-400">Copied!</span>';
                setTimeout(() => copyCodeBtn.innerHTML = originalHtml, 2000);
            }
            return;
        }

        // 3. Copy Full Message
        const copyFullBtn = e.target.closest('.btn-copy-full');
        if (copyFullBtn) {
            const raw = copyFullBtn.getAttribute('data-raw') || '';
            navigator.clipboard.writeText(raw);
            const orig = copyFullBtn.innerHTML;
            copyFullBtn.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i>';
            setTimeout(() => copyFullBtn.innerHTML = orig, 1800);
            return;
        }

        // 4. Read Aloud Button
        const readBtn = e.target.closest('.btn-read-aloud');
        if (readBtn) {
            const raw = readBtn.getAttribute('data-raw') || '';
            const spokenText = extractSpokenText(raw);
            if (window.voiceAssistant && spokenText) {
                window.voiceAssistant.speak(spokenText);
            }
            return;
        }

        // 5. Thumbs Up / Down Feedback
        const likeBtn = e.target.closest('.btn-feedback-like');
        const dislikeBtn = e.target.closest('.btn-feedback-dislike');
        if (likeBtn || dislikeBtn) {
            const msgCard = (likeBtn || dislikeBtn).closest('[data-msg-id]');
            const msgId = msgCard ? msgCard.getAttribute('data-msg-id') : null;
            const rating = likeBtn ? 'like' : 'dislike';

            if (msgId) {
                fetch('/api/chat/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({ message_id: parseInt(msgId), rating: rating })
                }).then(() => {
                    const btn = likeBtn || dislikeBtn;
                    btn.classList.add('text-indigo-400');
                });
            }
            return;
        }

        // 6. Sidebar Conversation Item Click
        const convItem = e.target.closest('.conv-item');
        const delBtn = e.target.closest('.btn-delete-conv');

        if (delBtn) {
            const convId = delBtn.getAttribute('data-conv-id');
            if (convId) {
                fetch(`/api/chat/conversations/${convId}`, {
                    method: 'DELETE',
                    headers: { 'X-CSRFToken': getCSRFToken() }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        const row = delBtn.closest('.conv-item');
                        if (row) row.remove();
                        if (currentConvInput && currentConvInput.value === convId) {
                            if (btnNewChat) btnNewChat.click();
                        }
                    }
                });
            }
            return;
        }

        if (convItem && !delBtn) {
            const convId = convItem.getAttribute('data-conv-id');
            if (convId) {
                loadConversationDetail(convId);
            }
        }
    });

    function loadConversationDetail(convId) {
        const typingId = showTypingIndicator();
        fetch(`/api/chat/conversations/${convId}`)
            .then(res => res.json())
            .then(data => {
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();

                if (data.status === 'success' && data.conversation) {
                    const conv = data.conversation;
                    if (currentConvInput) currentConvInput.value = conv.id;
                    if (activeChatTitle) activeChatTitle.innerText = conv.title;

                    chatContainer.innerHTML = '';
                    if (conv.messages && conv.messages.length > 0) {
                        conv.messages.forEach(m => {
                            if (m.role === 'user') {
                                appendUserMessage(m.content);
                            } else {
                                appendAIMessage(m.content, { tool_used: m.tool_used, message_id: m.id });
                            }
                        });
                    }
                    scrollToBottom();
                }
            })
            .catch(err => {
                const typingElem = document.getElementById(typingId);
                if (typingElem) typingElem.remove();
            });
    }

    scrollToBottom();
});
