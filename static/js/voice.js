// Voice Interaction Module (Web Speech API Integration)

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isSpeaking = false;
        this.ttsEnabled = true;
        this.speechRate = 1.0;
        
        // DOM Elements
        this.micBtn = document.getElementById('mic-btn');
        this.micIcon = document.getElementById('mic-icon');
        this.pulseRing = document.getElementById('mic-pulse-ring');
        this.pulseGlow = document.getElementById('mic-pulse-glow');
        this.statusBadge = document.getElementById('voice-status-badge');
        this.statusText = document.getElementById('status-text');
        this.statusDot = document.getElementById('status-indicator-dot');
        this.speechLiveText = document.getElementById('speech-live-text');
        this.chatInput = document.getElementById('chat-input');
        this.ttsToggleBtn = document.getElementById('toggle-tts-btn');

        this.initSpeechRecognition();
        this.bindEvents();
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("Speech Recognition API is not supported in this browser.");
            this.updateState('unsupported');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateState('listening');
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            const currentText = finalTranscript || interimTranscript;
            if (this.speechLiveText) {
                this.speechLiveText.innerText = currentText ? `"${currentText}"` : '';
            }
            if (this.chatInput && finalTranscript) {
                this.chatInput.value = finalTranscript;
            }
        };

        this.recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            this.isListening = false;

            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                alert("Microphone permission was denied. Please allow microphone access in your browser settings to use voice input.");
                this.updateState('permission_denied');
            } else if (event.error === 'no-speech') {
                this.updateState('no_speech');
                setTimeout(() => this.updateState('ready'), 2500);
            } else {
                this.updateState('ready');
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;
            if (this.chatInput && this.chatInput.value.trim().length > 0) {
                // Auto-submit recognized speech
                this.updateState('processing');
                if (window.submitChatQuestion) {
                    window.submitChatQuestion(this.chatInput.value.trim());
                }
            } else {
                this.updateState('ready');
            }
        };
    }

    bindEvents() {
        if (this.micBtn) {
            this.micBtn.addEventListener('click', () => {
                if (this.isListening) {
                    this.stopListening();
                } else {
                    this.startListening();
                }
            });
        }

        if (this.ttsToggleBtn) {
            this.ttsToggleBtn.addEventListener('click', () => {
                this.ttsEnabled = !this.ttsEnabled;
                this.updateTTSToggleUI();
            });
        }
    }

    startListening() {
        if (!this.recognition) {
            alert("Speech recognition is not supported on this browser. You can type your question manually in the input box.");
            return;
        }

        // Stop any active speech synthesis
        if (this.synthesis) {
            this.synthesis.cancel();
        }

        try {
            this.recognition.start();
        } catch (e) {
            console.warn("Recognition start failed or already active:", e);
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }

    speak(text) {
        if (!this.ttsEnabled || !this.synthesis || !text) return;

        this.synthesis.cancel(); // Stop current speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = this.speechRate;
        utterance.pitch = 1.0;

        utterance.onstart = () => {
            this.isSpeaking = true;
            this.updateState('responding');
        };

        utterance.onend = () => {
            this.isSpeaking = false;
            this.updateState('ready');
        };

        utterance.onerror = (e) => {
            console.error("Speech synthesis error:", e);
            this.isSpeaking = false;
            this.updateState('ready');
        };

        this.synthesis.speak(utterance);
    }

    updateState(state) {
        if (!this.statusText || !this.statusDot) return;

        // Reset indicators
        if (this.pulseRing) this.pulseRing.classList.add('hidden');
        if (this.pulseGlow) this.pulseGlow.classList.add('hidden');
        if (this.micBtn) this.micBtn.className = "relative w-16 h-16 sm:w-20 sm:h-20 rounded-full flex items-center justify-center text-2xl sm:text-3xl shadow-lg transition-all duration-200 ";

        switch (state) {
            case 'listening':
                this.statusText.innerText = "Listening...";
                this.statusDot.className = "fa-solid fa-circle text-[8px] text-rose-500 animate-pulse";
                if (this.pulseRing) this.pulseRing.classList.remove('hidden');
                if (this.pulseGlow) this.pulseGlow.classList.remove('hidden');
                if (this.micBtn) this.micBtn.className += "bg-rose-600 text-white shadow-rose-500/40 scale-105";
                break;

            case 'processing':
                this.statusText.innerText = "Processing...";
                this.statusDot.className = "fa-solid fa-spinner text-[10px] text-amber-500 animate-spin";
                if (this.micBtn) this.micBtn.className += "bg-amber-500 text-white shadow-amber-500/30";
                break;

            case 'responding':
                this.statusText.innerText = "Assistant is responding...";
                this.statusDot.className = "fa-solid fa-volume-high text-[10px] text-indigo-500 animate-bounce";
                if (this.micBtn) this.micBtn.className += "bg-indigo-600 text-white shadow-indigo-500/30";
                break;

            case 'no_speech':
                this.statusText.innerText = "No speech detected";
                this.statusDot.className = "fa-solid fa-circle text-[8px] text-slate-400";
                if (this.micBtn) this.micBtn.className += "bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-blue-500/30";
                break;

            case 'permission_denied':
                this.statusText.innerText = "Microphone blocked";
                this.statusDot.className = "fa-solid fa-circle text-[8px] text-rose-500";
                if (this.micBtn) this.micBtn.className += "bg-slate-400 text-white shadow-none cursor-not-allowed";
                break;

            case 'unsupported':
                this.statusText.innerText = "Speech API unsupported (Type questions)";
                this.statusDot.className = "fa-solid fa-circle text-[8px] text-amber-500";
                if (this.micBtn) this.micBtn.className += "bg-slate-400 text-white cursor-not-allowed";
                break;

            case 'ready':
            default:
                this.statusText.innerText = "Click to speak";
                this.statusDot.className = "fa-solid fa-circle text-[8px] text-emerald-500";
                if (this.speechLiveText) this.speechLiveText.innerText = "";
                if (this.micBtn) this.micBtn.className += "bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-blue-500/30 hover:scale-105 active:scale-95";
                break;
        }
    }

    updateTTSToggleUI() {
        if (!this.ttsToggleBtn) return;
        const icon = document.getElementById('tts-icon');
        const label = document.getElementById('tts-label');

        if (this.ttsEnabled) {
            this.ttsToggleBtn.className = "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 transition-colors";
            if (icon) icon.className = "fa-solid fa-volume-high";
            if (label) label.innerText = "Voice ON";
        } else {
            this.ttsToggleBtn.className = "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700 transition-colors";
            if (icon) icon.className = "fa-solid fa-volume-xmark";
            if (label) label.innerText = "Voice OFF";
            if (this.synthesis) this.synthesis.cancel();
        }
    }
}

// Global instance
window.voiceAssistant = new VoiceAssistant();
