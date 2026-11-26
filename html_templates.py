from html import escape

css = '''
<style>
:root {
    --page-bg: #0b1120;
    --panel-border: rgba(148, 163, 184, 0.14);
    --user-bg: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
    --bot-bg: #192233;
    --text-primary: #f8fafc;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(37, 99, 235, 0.12), transparent 28rem),
        radial-gradient(circle at 85% 80%, rgba(124, 58, 237, 0.08), transparent 24rem),
        var(--page-bg);
}

section[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.96);
    border-right: 1px solid var(--panel-border);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.25rem;
}

section[data-testid="stSidebar"] .stFileUploader {
    background: rgba(30, 41, 59, 0.72);
    border: 1px solid var(--panel-border);
    border-radius: 14px;
    padding: 0.55rem;
}

h1 {
    color: var(--text-primary) !important;
    font-weight: 750 !important;
    letter-spacing: -0.035em;
}

.block-container {
    max-width: 980px;
    padding-top: 2.25rem;
    padding-bottom: 12rem;
}

.stTextInput input {
    background: rgba(30, 41, 59, 0.92);
    border: 1px solid var(--panel-border);
    border-radius: 14px;
    color: var(--text-primary);
    min-height: 52px;
    padding: 0 1rem;
    box-shadow: 0 10px 30px rgba(2, 6, 23, 0.16);
}

.stTextInput input:focus {
    border-color: #60a5fa;
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.12);
}

.stButton > button {
    min-height: 52px;
    border-radius: 14px;
    border: 1px solid rgba(96, 165, 250, 0.32);
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    color: white;
    font-weight: 700;
    box-shadow: 0 10px 24px rgba(37, 99, 235, 0.22);
}

.stButton > button:hover {
    border-color: rgba(147, 197, 253, 0.75);
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
}

.chat-message {
    width: 100%;
    display: flex;
    gap: 0.9rem;
    margin: 0 0 1rem;
    padding: 1.15rem 1.25rem;
    border: 1px solid var(--panel-border);
    border-radius: 18px;
    box-shadow: 0 12px 36px rgba(2, 6, 23, 0.16);
    animation: message-in 180ms ease-out;
}

.chat-message.user {
    background: var(--user-bg);
    margin-left: auto;
    max-width: 88%;
}

.chat-message.bot {
    background: var(--bot-bg);
    margin-right: auto;
    max-width: 92%;
}

.chat-message .avatar {
    width: 44px;
    flex: 0 0 44px;
}

.chat-message .avatar-label {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: rgba(15, 23, 42, 0.38);
    color: #fff;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    border-radius: 14px;
}

.chat-message.bot .avatar-label {
    background: linear-gradient(135deg, #0ea5e9, #2563eb);
}

.chat-message.user .avatar-label {
    background: rgba(255, 255, 255, 0.14);
}

.chat-message .message {
    width: 100%;
    min-width: 0;
    padding: 0.18rem 0 0;
    color: var(--text-primary);
    font-size: 0.98rem;
    line-height: 1.65;
    overflow-wrap: anywhere;
}

.st-key-composer {
    position: fixed;
    z-index: 1000;
    bottom: 0.75rem;
    left: calc(50% + 9.5rem);
    transform: translateX(-50%);
    width: min(940px, calc(100vw - 24rem));
    padding: 1rem 1.15rem 0.8rem;
    border: 1px solid var(--panel-border);
    border-radius: 22px;
    background: rgba(15, 23, 42, 0.94);
    box-shadow: 0 18px 60px rgba(0, 0, 0, 0.38);
    backdrop-filter: blur(18px);
}

.st-key-composer .stTextInput input {
    background: rgba(30, 41, 59, 0.84);
    box-shadow: none;
}

.st-key-composer .stButton > button {
    min-height: 44px;
}

.welcome-screen {
    min-height: calc(100vh - 16rem);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 1rem;
    text-align: center;
}

.welcome-logo {
    width: 82px;
    height: 82px;
    display: grid;
    place-items: center;
    margin-bottom: 1.25rem;
    border: 1px solid rgba(147, 197, 253, 0.32);
    border-radius: 27px;
    background:
        radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.28), transparent 38%),
        linear-gradient(145deg, #0ea5e9 0%, #4f46e5 58%, #9333ea 100%);
    box-shadow: 0 18px 55px rgba(59, 130, 246, 0.28);
}

.welcome-logo svg {
    width: 56px;
    height: 42px;
    filter: drop-shadow(0 3px 5px rgba(15, 23, 42, 0.3));
}

.welcome-title {
    margin: 0;
    color: #f8fafc;
    font-size: clamp(2.1rem, 5vw, 3.2rem);
    font-weight: 750;
    letter-spacing: -0.055em;
    line-height: 1.08;
}

.welcome-subtitle {
    max-width: 34rem;
    margin: 0.9rem 0 0;
    color: #a9b3c4;
    font-size: 1rem;
    line-height: 1.65;
}

@keyframes message-in {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 700px) {
    .block-container {
        padding: 1.25rem 0.75rem 1.5rem;
    }
    .chat-message,
    .chat-message.user,
    .chat-message.bot {
        max-width: 100%;
        padding: 0.85rem;
        border-radius: 14px;
    }
    .chat-message .avatar {
        width: 36px;
        flex-basis: 36px;
    }
    .chat-message .avatar-label {
        width: 36px;
        height: 36px;
        border-radius: 11px;
        font-size: 0.68rem;
    }
    .st-key-composer {
        left: 0.65rem;
        right: 0.65rem;
        bottom: 0.55rem;
        transform: none;
        width: auto;
        padding: 0.75rem;
        border-radius: 18px;
    }
    .welcome-screen {
        min-height: calc(100vh - 14rem);
    }
}
</style>
'''

def get_welcome_template():
    return '''
    <div class="welcome-screen">
        <div class="welcome-logo" aria-hidden="true">
            <svg viewBox="0 0 64 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <clipPath id="bharat-flag-clip">
                        <rect x="1" y="1" width="62" height="46" rx="3"/>
                    </clipPath>
                </defs>
                <g clip-path="url(#bharat-flag-clip)">
                    <path fill="#FF9933" d="M1 1h62v15H1z"/>
                    <path fill="#FFFFFF" d="M1 16h62v16H1z"/>
                    <path fill="#138808" d="M1 32h62v15H1z"/>
                    <g stroke="#000080" stroke-width=".8">
                        <circle cx="32" cy="24" r="7.1"/>
                        <circle cx="32" cy="24" r="1.15" fill="#000080"/>
                        <path d="M32 16.9v5.95M32 25.15v5.95M24.9 24h5.95M33.15 24h5.95
                            M26.98 18.98l4.21 4.21M32.81 24.81l4.21 4.21
                            M37.02 18.98l-4.21 4.21M31.19 24.81l-4.21 4.21"/>
                        <path d="M34.85 17.45l-1.6 5.73M30.75 24.82l-1.6 5.73
                            M25.13 22.85l5.73 1.6M33.14 27.55l5.73 1.6
                            M27.45 17.96l2.93 5.18M33.62 24.86l2.93 5.18
                            M38.04 19.45l-5.18 2.93M31.14 25.62l-5.18 2.93"/>
                    </g>
                </g>
            </svg>
        </div>
        <h1 class="welcome-title">BharatGPT</h1>
        <p class="welcome-subtitle">
            Your private AI space. Ask a question, share an image, or explore a PDF.
        </p>
    </div>
    '''


def _format_message(message):
    return escape(str(message)).replace("\n", "<br>")


def get_bot_template(MSG):
    bot_template = f'''
    <div class="chat-message bot">
        <div class="avatar">
            <div class="avatar-label">AI</div>
        </div>
        <div class="message">{_format_message(MSG)}</div>
    </div>
    '''
    return bot_template

def get_user_template(MSG):
    user_template = f'''
    <div class="chat-message user">
        <div class="avatar">
            <div class="avatar-label">You</div>
        </div>    
        <div class="message">{_format_message(MSG)}</div>
    </div>
    '''
    return user_template
