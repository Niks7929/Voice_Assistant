import os
import re
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv(override=True)

from services.knowledge_service import KnowledgeService
from services.web_search_service import WebSearchService
from tools.code_tool import CodeTool
from tools.document_tool import DocumentTool

logger = logging.getLogger(__name__)


class AIService:
    """Specialized AI Assistant dedicated EXCLUSIVELY to:
    - Programming Languages (Python, JS, TS, Java, C++, C#, Go, Rust, PHP, SQL, Dart, Kotlin, Swift, HTML, CSS, Bash)
    - Web & Mobile Frameworks (React, Next.js, Vue, Angular, Node, Express, FastAPI, Django, Flask, Spring Boot, Flutter, Laravel, .NET)
    - Data Structures, Algorithms, Software Engineering, Architecture, and DevOps.
    """

    SYSTEM_PROMPT = (
        "You are CodeVocalis AI, an expert programming assistant dedicated EXCLUSIVELY to programming languages, "
        "software engineering, algorithms, databases, web & mobile frameworks, and developer tools.\n\n"
        "Core Directives:\n"
        "1. STRICT DOMAIN: Answer only software development, coding, and technical questions. If a query is entirely about "
        "politics, general history, movies, or non-technical topics, politely state that you are exclusively a programming assistant.\n"
        "2. ADAPTIVE & NATURAL CODE GENERATION (CRITICAL):\n"
        "   - When the user asks for basic, foundational, or beginner programs (e.g., 'addition in python', 'simple code for...', 'hello world', 'reverse string', 'swap numbers', 'even or odd', 'simple loop', 'fibonacci'):\n"
        "     Give the CLEANEST, SIMPLEST, MOST NATURAL code first (e.g., direct variables, interactive input()). Do NOT over-engineer simple tasks with complex type hints, heavy docstrings, or unnecessary classes unless requested.\n"
        "   - Always provide standard, readable code that students, developers, and educators actually use.\n"
        "   - Always include a short 'Sample Output' block so the user clearly sees what the program prints.\n"
        "   - For advanced/framework queries (FastAPI, React, Next.js, Spring Boot, Docker, Django), use modern idiomatic best practices with clear comments.\n"
        "3. INTENT CLASSIFICATION:\n"
        "   - If the user asks for a concept or theory ('what is an API', 'define machine learning', 'explain polymorphism'): provide a clear, well-structured explanation with headings and bullet points. DO NOT output code blocks unless code was specifically requested.\n"
        "   - If the user asks for code ('write python code', 'give code', 'how to write'): provide complete, 100% syntactically correct code blocks with language tags (```python, ```javascript, ```java, etc.) and a concise 2-3 bullet explanation.\n"
        "4. Voice-friendly: Keep text clear, concise, and easy to read or listen to."
    )

    NON_PROGRAMMING_PATTERNS = [
        r'\b(prime minister|president of|chief minister|parliament|election|political|politics|minister of|rajya sabha|lok sabha)\b',
        r'\b(bollywood|hollywood|movie|cinema|actor|actress|box office|song|singer)\b',
        r'\b(cricket|ipl|world cup|football|messi|ronaldo|tennis|badminton|olympics)\b',
        r'\b(capital of|largest continent|longest river|who founded the dynasty|who was the king)\b',
        r'^\s*[\d\s\+\-\*\/\(\)\.\^]+\s*$',
        r'^\s*(calculate|compute)\s+[\d\s\+\-\*\/\^]+\s*$'
    ]

    CODE_INTENT_KEYWORDS = [
        'code', 'program', 'script', 'implement', 'implementation', 'write a',
        'function', 'class', 'syntax', 'snippet', 'boilerplate', 'create a route',
        'debug', 'fix this error', 'solve this error', 'write python', 'write java',
        'write javascript', 'write c++', 'write go', 'write rust', 'write sql',
        'write flutter', 'write react', 'write html', 'write css', 'give code',
        'show code', 'example code'
    ]

    CONCEPT_INTENT_KEYWORDS = [
        'define', 'definition', 'what is', 'what are', 'what does', 'explain',
        'tell me about', 'tell me', 'concept of', 'overview of', 'difference between',
        'vs', 'meaning of', 'how does', 'why does', 'why is', 'how to use', 'how do i',
        'how can i', 'pros and cons', 'advantages of', 'describe', 'details of'
    ]

    def __init__(self):
        self._refresh_keys()

    def _refresh_keys(self):
        """Dynamically re-reads environment variables to pick up newly added API keys."""
        load_dotenv(override=True)
        self.gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.gemini_client = None

        if self.gemini_key and self.gemini_key.strip() and 'your_gemini' not in self.gemini_key:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                logger.debug(f"google-genai client initialization note: {e}")

    def answer(self, question: str, document_context: Optional[str] = None, conversation_history: Optional[list] = None) -> Dict[str, Any]:
        self._refresh_keys()
        q = (question or "").strip()
        if not q:
            return {
                'answer': 'Please ask any question about programming languages, frameworks, or software architecture.',
                'tool_used': 'CODE_AI'
            }

        q_lower = q.lower()

        # 1. Non-Programming Domain Guard (Focus strictly on programming & frameworks)
        if self._is_non_programming_query(q_lower):
            return {
                'answer': (
                    "### CodeVocalis AI: Programming & Framework Focus\n\n"
                    "I am **CodeVocalis AI**, a specialized assistant built **exclusively for Programming Languages, Frameworks, Software Engineering, and Algorithms**.\n\n"
                    "I do not answer questions on politics, general history, movies, or standalone arithmetic calculations.\n\n"
                    "**What you can ask me:**\n"
                    "- **All Programming Languages:** Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, PHP, SQL, Dart, Kotlin, Swift, HTML/CSS.\n"
                    "- **All Modern Frameworks:** React, Next.js, Vue, Angular, Node.js, Express, FastAPI, Django, Flask, Spring Boot, Flutter, Laravel.\n"
                    "- **Concepts & Architecture:** Algorithms, Data Structures, Machine Learning, REST APIs, Microservices, System Design, Concurrency, Git, Docker, Kubernetes.\n"
                    "- **Code & Implementation:** Ask *'write code for...'*, *'how to implement...'*, *'give syntax for...'*, or paste code to debug and fix errors!"
                ),
                'tool_used': 'DOMAIN_FOCUS_GUARD'
            }

        # 2. Document / Codebase QA Context (if file or doc URL is attached)
        if document_context:
            doc_ans = self._answer_with_document_context(q, document_context)
            if doc_ans:
                return {'answer': doc_ans, 'tool_used': 'DOCUMENT_CODE_QA'}

        # Detect User Intent
        is_code_request = any(kw in q_lower for kw in self.CODE_INTENT_KEYWORDS)
        is_concept_request = any(kw in q_lower for kw in self.CONCEPT_INTENT_KEYWORDS)

        # 3. Primary LLM: Google Gemini AI
        if self.gemini_key and self.gemini_key.strip() and 'your_gemini' not in self.gemini_key:
            gemini_response = self._call_gemini(q, conversation_history)
            if gemini_response:
                return {'answer': gemini_response, 'tool_used': 'GEMINI_CODE_AI'}

        # 4. Secondary LLM: OpenAI GPT
        if self.openai_key and self.openai_key.strip() and 'your_openai' not in self.openai_key:
            openai_response = self._call_openai(q, conversation_history)
            if openai_response:
                return {'answer': openai_response, 'tool_used': 'OPENAI_CODE_AI'}

        # 5. Routing based on User Intent (when no live LLM API key is present)

        # 5A. If user asks for CODE or implementation
        if is_code_request and not (is_concept_request and not any(w in q_lower for w in ['code', 'implement', 'write', 'give'])):
            code_tool_answer = CodeTool.answer(q)
            if code_tool_answer:
                return {'answer': code_tool_answer, 'tool_used': 'CODE_ENGINE'}

        # 5B. If user asks for DEFINITIONS, CONCEPTS, or EXPLANATIONS
        if is_concept_request:
            concept_answer = KnowledgeService.get_definition(q)
            if concept_answer:
                return {'answer': concept_answer, 'tool_used': 'KNOWLEDGE_ENGINE'}

        # 5C. CodeTool for Code Requests & Implementation Patterns
        code_tool_answer = CodeTool.answer(q)
        if code_tool_answer:
            return {'answer': code_tool_answer, 'tool_used': 'CODE_ENGINE'}

        # 5D. Try KnowledgeService for any technical concepts even if no explicit keyword
        general_concept = KnowledgeService.get_definition(q)
        if general_concept:
            return {'answer': general_concept, 'tool_used': 'KNOWLEDGE_ENGINE'}

        # 6. Live Developer Web Search for Docs / Libraries / Syntax
        search_results = WebSearchService.search(f"{q} programming documentation", limit=3)
        if search_results:
            formatted_search = self._format_web_results(search_results, q)
            return {'answer': formatted_search, 'tool_used': 'DEV_WEB_SEARCH'}

        # 7. Intelligent Developer Synthesis
        clean_topic = q.rstrip('?.')
        return {
            'answer': (
                f"### Software Engineering & Architecture Guide: `{clean_topic}`\n\n"
                f"In modern software engineering, `{clean_topic}` is an essential technical concept, library, or programming pattern.\n\n"
                f"**Technical Considerations:**\n"
                f"- **Architecture & Design:** Ensure clean separation of concerns and adhere to standard language idioms.\n"
                f"- **Production Reliability:** Implement thorough error handling, input validation, and defensive boundary checks.\n"
                f"- **Scalability & Performance:** Choose appropriate data structures with optimal time and space complexity ($O(1)$ or $O(\\log N)$ where applicable).\n\n"
                f"**Suggested Next Steps:**\n"
                f"- To see runnable, syntactically correct code, ask: *'write code for {clean_topic}'*.\n"
                f"- To explore foundational mechanics, ask: *'explain {clean_topic}'* or *'define {clean_topic}'*.\n\n"
                f"> 💡 **Tip:** To unlock 100% full, real-time Gemini AI reasoning and code generation for any query, activate your free Google Gemini API Key via the **AI Key** button in the dashboard topbar!"
            ),
            'tool_used': 'CODE_ASSISTANT'
        }


    def _is_non_programming_query(self, query: str) -> bool:
        """Detects if query is strictly outside programming, software engineering, and CS."""
        for pattern in self.NON_PROGRAMMING_PATTERNS:
            if re.search(pattern, query, re.I):
                # Exception: if query also explicitly mentions a programming language or code
                tech_whitelist = [
                    'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'rust',
                    'golang', 'php', 'sql', 'html', 'css', 'flutter', 'react', 'code',
                    'programming', 'algorithm', 'function', 'class', 'api'
                ]
                if any(w in query for w in tech_whitelist):
                    return False
                return True
        return False

    def _call_gemini(self, prompt: str, history: Optional[list] = None) -> Optional[str]:
        """Calls Google Gemini API for code generation and analysis."""
        full_prompt = f"{self.SYSTEM_PROMPT}\n\nUser Question:\n{prompt}"
        if history and isinstance(history, list):
            hist_lines = []
            for h in history[-4:]:
                role = "User" if h.get('role') == 'user' else "Assistant"
                hist_lines.append(f"{role}: {h.get('content')}")
            full_prompt = f"{self.SYSTEM_PROMPT}\n\nConversation Context:\n" + "\n".join(hist_lines) + f"\n\nUser Question:\n{prompt}"

        # Direct REST API (Fastest and resilient with strict 8s timeout)
        models_to_try = ['gemini-3-flash-preview', 'gemini-3.8-flash', 'gemini-flash-latest']
        for model in models_to_try:
            try:
                import urllib.request
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
                payload = json.dumps({"contents": [{"parts": [{"text": full_prompt}]}]}).encode('utf-8')
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=8) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    candidates = data.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        if parts and 'text' in parts[0]:
                            return parts[0]['text'].strip()
            except Exception as e:
                logger.debug(f"Direct Gemini REST ({model}) note: {e}")

        # Secondary: google-genai SDK
        if self.gemini_client:
            for model_name in ['gemini-3-flash-preview', 'gemini-3.8-flash']:
                try:
                    res = self.gemini_client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    if res and res.text:
                        return res.text.strip()
                except Exception as e:
                    logger.debug(f"Gemini SDK ({model_name}) call failed: {e}")

        return None

    def _call_openai(self, prompt: str, history: Optional[list] = None) -> Optional[str]:
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            messages = [{'role': 'system', 'content': self.SYSTEM_PROMPT}]
            if history:
                for h in history[-4:]:
                    messages.append({'role': h.get('role', 'user'), 'content': h.get('content', '')})
            messages.append({'role': 'user', 'content': prompt})

            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=messages,
                max_tokens=800
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.debug(f"OpenAI call failed: {e}")
            return None

    def _answer_with_document_context(self, question: str, doc_context: str) -> str:
        """Answers code/doc question using attached document context."""
        cleaned_doc = doc_context[:4000]

        # Check if question targets a specific function or class
        target_fn = None
        for word in re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{2,}', question):
            if word.lower() not in ['what', 'does', 'function', 'code', 'file', 'uploaded', 'explain', 'show', 'mean', 'return', 'this']:
                if word in cleaned_doc:
                    target_fn = word
                    break

        if target_fn:
            lines = cleaned_doc.split('\n')
            extracted_fn = []
            capturing = False
            for line in lines:
                if target_fn in line and any(k in line for k in ['def ', 'function ', 'class ', 'const ', 'let ']):
                    capturing = True
                    extracted_fn.append(line)
                    continue
                if capturing:
                    if line.strip() and not line.startswith(' ') and not line.startswith('\t') and any(k in line for k in ['def ', 'class ']):
                        break
                    extracted_fn.append(line)
                    if len(extracted_fn) > 15:
                        break

            if extracted_fn:
                fn_code = "\n".join(extracted_fn)
                return (
                    f"### Code Analysis: `{target_fn}`\n\n"
                    f"Here is the implementation of `{target_fn}` from your uploaded codebase:\n\n"
                    f"```python\n{fn_code}\n```\n\n"
                    f"**Functional Overview:**\n"
                    f"- The function `{target_fn}` processes the input parameters and executes the calculation shown above.\n"
                    f"- It returns the calculated output for use in business logic or API responses."
                )

        q_words = [w for w in re.split(r'\W+', question.lower()) if len(w) > 3]
        relevant_lines = []
        for line in cleaned_doc.split('\n'):
            if any(w in line.lower() for w in q_words):
                relevant_lines.append(line.strip())

        if relevant_lines:
            excerpt = "\n".join(relevant_lines[:8])
            return (
                f"### Document Context Analysis\n\n"
                f"Based on your attached file/code, here is the relevant section:\n\n"
                f"```text\n{excerpt}\n```\n\n"
                f"**Technical Assessment:**\n"
                f"The attached code addresses `{question}` within the sections highlighted above."
            )

        return (
            f"### Document Analysis for: `{question}`\n\n"
            f"Here is the relevant excerpt from your uploaded document:\n\n"
            f"```text\n{cleaned_doc[:600]}...\n```\n\n"
            f"You can ask specific questions about functions, classes, or patterns in this codebase."
        )


    def _format_web_results(self, results: list, query: str) -> str:
        lines = [f"### Developer Documentation & Resources for: `{query}`\n"]
        for idx, item in enumerate(results[:3], start=1):
            title = item.get('title', 'Technical Resource')
            url = item.get('url', '')
            snippet = item.get('snippet', '')
            lines.append(f"**{idx}. [{title}]({url})**\n{snippet}\n")
        return "\n".join(lines)
