"""Universal Knowledge Service for Conceptual, Technical, and General Inquiries.
Provides structured definitions, explanations, and overviews without forcing code blocks.
Integrates curated Computer Science & AI domains with DuckDuckGo Instant Answers and Wikipedia REST API.
"""

import json
import logging
import re
import urllib.parse
import urllib.request
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Answers conceptual, definitions, architectural, and factual questions."""

    @classmethod
    def get_definition(cls, query: str) -> Optional[str]:
        q = (query or "").strip()
        if not q:
            return None

        lower_q = q.lower()
        search_term = cls._extract_search_term(lower_q)

        # 1. Curated High-Quality Domain Knowledge (Priority)
        curated = cls._get_curated_knowledge(search_term, lower_q)
        if curated:
            return curated

        # 2. DuckDuckGo Instant Answer API
        ddg_result = cls._fetch_duckduckgo_instant_answer(search_term)
        if ddg_result:
            return ddg_result

        # 3. Wikipedia REST API & OpenSearch
        wiki_result = cls._fetch_wikipedia_summary(search_term)
        if wiki_result:
            return wiki_result

        # 4. Fallback search on original query
        if search_term != lower_q:
            wiki_alt = cls._fetch_wikipedia_summary(lower_q)
            if wiki_alt:
                return wiki_alt

        return None

    @classmethod
    def _extract_search_term(cls, query: str) -> str:
        term = query.strip()
        prefixes = [
            'define ', 'definition of ', 'what is an ', 'what is a ', 'what is ',
            'what are ', 'who is the ', 'who is ', 'explain ', 'tell me about ',
            'meaning of ', 'concept of ', 'describe '
        ]
        for p in prefixes:
            if term.startswith(p):
                term = term[len(p):].strip()
                break
        return term.rstrip('?.! ')

    @classmethod
    def _fetch_duckduckgo_instant_answer(cls, term: str) -> Optional[str]:
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(term)}&format=json&no_html=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'CodeVocalis/1.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                abstract = data.get('AbstractText', '').strip()
                if abstract and len(abstract) > 30:
                    heading = data.get('Heading') or term.title()
                    source = data.get('AbstractSource', 'Encyclopedia')
                    page_url = data.get('AbstractURL', '')
                    return cls._format_response(heading, abstract, source, page_url)
        except Exception as e:
            logger.debug(f"DuckDuckGo instant answer failed: {e}")
        return None

    @classmethod
    def _fetch_wikipedia_summary(cls, term: str) -> Optional[str]:
        try:
            # Disambiguate common computer science terms so they don't resolve to biology, law, or furniture
            tech_term = term
            cs_keywords = ['inheritance', 'class', 'stack', 'queue', 'tree', 'table', 'port', 'thread', 'process', 'module', 'package', 'pointer', 'reference', 'garbage collection', 'closure', 'hoisting']
            if any(term == w or term.startswith(f"{w} ") for w in cs_keywords):
                tech_term = f"{term} (computer science)"

            # Step A: Search for the best matching article title
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(tech_term)}&limit=1&namespace=0&format=json"
            req = urllib.request.Request(search_url, headers={'User-Agent': 'CodeVocalis/1.0 (contact: student@developer.local)'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                search_data = json.loads(resp.read().decode('utf-8'))
                if len(search_data) >= 4 and search_data[1]:
                    page_title = search_data[1][0]
                    # Step B: Fetch summary from Wikipedia REST API
                    sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_title)}"
                    sum_req = urllib.request.Request(sum_url, headers={'User-Agent': 'CodeVocalis/1.0 (contact: student@developer.local)'})
                    with urllib.request.urlopen(sum_req, timeout=4) as sum_resp:
                        sum_data = json.loads(sum_resp.read().decode('utf-8'))
                        extract = sum_data.get('extract', '').strip()
                        if extract and len(extract) > 20:
                            page_url = sum_data.get('content_urls', {}).get('desktop', {}).get('page', '')
                            return cls._format_response(page_title, extract, 'Wikipedia', page_url)
        except Exception as e:
            logger.debug(f"Wikipedia summary fetch failed: {e}")
        return None

    @classmethod
    def _format_response(cls, title: str, text: str, source: str, url: str) -> str:
        # Split into readable paragraphs
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if len(sentences) > 1:
            overview = sentences[0]
            details = " ".join(sentences[1:])
            res = f"### {title}\n\n**Overview:**\n{overview}\n\n**Key Details:**\n{details}\n\n"
        else:
            res = f"### {title}\n\n**Overview:**\n{text}\n\n"

        if url:
            res += f"**Source Reference:** [{source}]({url})"
        return res.strip()

    @classmethod
    def _get_curated_knowledge(cls, term: str, full_query: str) -> Optional[str]:
        # ==========================================
        # 0. OOP INDIVIDUAL PILLARS & CONCEPTS
        # ==========================================
        if 'inheritance' in term or 'inheritance' in full_query:
            return (
                "### Inheritance in Object-Oriented Programming (OOP)\n\n"
                "**Definition:**\n"
                "Inheritance is a fundamental mechanism of Object-Oriented Programming (OOP) wherein a new class "
                "(child or subclass) derives attributes, fields, and methods from an existing class (parent or superclass). "
                "It establishes an **'is-a'** relationship between classes and maximizes code reusability.\n\n"
                "**Types of Inheritance:**\n"
                "1. **Single Inheritance:** A subclass inherits from a single parent class.\n"
                "2. **Multilevel Inheritance:** A class is derived from a class which is also derived from another class (Grandparent -> Parent -> Child).\n"
                "3. **Hierarchical Inheritance:** Multiple subclasses inherit from one common parent class.\n"
                "4. **Multiple Inheritance:** A subclass inherits directly from more than one parent class (Supported in Python and C++; Java uses Interfaces).\n\n"
                "**Key Concepts & Keywords:**\n"
                "- `super()`: Used in subclasses to invoke constructors and methods of the parent class.\n"
                "- **Method Overriding:** A subclass provides a specific implementation of a method that is already defined in its superclass.\n"
                "- **Code Reusability:** Prevents duplicate boilerplate logic across domain entities.\n\n"
                "*(To see working code, ask 'write inheritance code in python' or 'inheritance in java'.)*"
            )

        if 'polymorphism' in term or 'polymorphism' in full_query:
            return (
                "### Polymorphism in Object-Oriented Programming\n\n"
                "**Definition:**\n"
                "Polymorphism (meaning 'many forms') allows entities such as functions, methods, or objects to behave "
                "differently based on the context or the runtime type of the object receiving the call.\n\n"
                "**Two Types of Polymorphism:**\n"
                "1. **Compile-Time Polymorphism (Static / Early Binding):**\n"
                "   - **Method Overloading:** Multiple methods in the same class share the same name with different parameter lists.\n"
                "   - **Operator Overloading:** Custom behavior defined for operators like `+` or `*` on custom objects.\n"
                "2. **Runtime Polymorphism (Dynamic / Late Binding):**\n"
                "   - **Method Overriding:** A child class overrides a virtual/abstract method of its parent class, and the runtime environment decides which method to call based on the instantiated object.\n\n"
                "**Benefits:** Loose coupling, dynamic extensibility, and interface-driven design."
            )

        if 'encapsulation' in term or 'encapsulation' in full_query:
            return (
                "### Encapsulation in Software Engineering\n\n"
                "**Definition:**\n"
                "Encapsulation is the OOP principle of bundling data (fields/variables) and the methods that operate on that data "
                "within a single cohesive unit (a class), while restricting direct outside access to internal state.\n\n"
                "**Core Mechanisms:**\n"
                "- **Access Modifiers:** `private` (accessible only within class), `protected` (within class and subclasses), and `public` (accessible anywhere).\n"
                "- **Getters & Setters:** Controlled accessor methods that validate data before reading or modifying internal state.\n"
                "- **Data Hiding:** Shielding object internals from unauthorized modification and unexpected external side effects."
            )

        if 'abstraction' in term or 'abstraction' in full_query:
            return (
                "### Abstraction in Software Design\n\n"
                "**Definition:**\n"
                "Abstraction is the process of hiding complex internal implementation details and showing only the essential "
                "features and contracts to the external consumer.\n\n"
                "**How Abstraction is Implemented:**\n"
                "- **Abstract Classes:** Classes that cannot be instantiated directly and define abstract method signatures for subclasses to implement.\n"
                "- **Interfaces:** Pure contracts defining what methods a class must implement without specifying how (e.g. `interface` in TypeScript/Java, `Protocol` in Python).\n"
                "- **Real-World Analogy:** Driving a car requires pressing the accelerator pedal; the driver does not need to know the internal fuel injection and combustion physics."
            )

        # ==========================================
        # 0B. JAVASCRIPT & MODERN WEB CONCEPTS
        # ==========================================
        if any(w in term for w in ['let var const', 'var vs let', 'difference between let', 'difference between var', 'var, let']):
            return (
                "### JavaScript: `var` vs. `let` vs. `const`\n\n"
                "In modern JavaScript (ES6+), variable declaration keywords have crucial differences in scope, hoisting, and reassignability:\n\n"
                "| Feature | `var` (Legacy ES5) | `let` (Modern ES6) | `const` (Modern ES6) |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Scope** | Function Scope | Block Scope (`{}`) | Block Scope (`{}`) |\n"
                "| **Hoisting** | Hoisted with `undefined` | Hoisted in Temporal Dead Zone (TDZ) | Hoisted in Temporal Dead Zone (TDZ) |\n"
                "| **Re-declaration** | Allowed in same scope | SyntaxError | SyntaxError |\n"
                "| **Re-assignment** | Allowed | Allowed | Not Allowed (Immutable binding) |\n"
                "| **Window property** | Adds to `window` object | Does not attach to `window` | Does not attach to `window` |\n\n"
                "**Best Practice Rule of Thumb:**\n"
                "1. Default to **`const`** for all variables.\n"
                "2. Use **`let`** only when you know the variable value needs to change (e.g., loop counters, toggles).\n"
                "3. **Never use `var`** in modern codebases to prevent accidental scope leakage and hoisting bugs."
            )

        if 'closure' in term or 'closures' in term:
            return (
                "### Closures in JavaScript & Computer Science\n\n"
                "**Definition:**\n"
                "A closure is the combination of a function bundled together with references to its surrounding state "
                "(the lexical environment). In JavaScript, a closure gives an inner function access to an outer function's scope "
                "even after the outer function has finished executing and returned.\n\n"
                "**Primary Use Cases:**\n"
                "1. **Data Privacy / Encapsulation:** Creating private variables and functions that cannot be accessed or mutated from the global scope.\n"
                "2. **Function Factories:** Functions that configure and return specialized functions (e.g., multipliers or custom loggers).\n"
                "3. **Partial Application & Currying:** Pre-filling arguments in functional programming patterns."
            )

        if 'hoisting' in term:
            return (
                "### Hoisting in JavaScript\n\n"
                "**Definition:**\n"
                "Hoisting is JavaScript's default behavior of moving variable and function declarations to the top of their "
                "containing scope during the compilation phase before code execution.\n\n"
                "**How Different Declarations Behave:**\n"
                "- **Function Declarations (`function foo() {}`):** Fully hoisted with their body. You can call the function before its line of declaration.\n"
                "- **`var`:** Hoisted and initialized with `undefined`. Accessing it before declaration yields `undefined` rather than an error.\n"
                "- **`let` and `const`:** Hoisted to the top of their block, but **not initialized**. Accessing them before their declaration line throws a `ReferenceError` because they reside in the **Temporal Dead Zone (TDZ)**."
            )

        # ==========================================
        # 0C. POINTERS, MEMORY & SYSTEMS
        # ==========================================
        if 'pointer' in term or 'pointers' in term:
            return (
                "### Pointers in Computer Programming (C / C++)\n\n"
                "**Definition:**\n"
                "A pointer is a variable that stores the **memory address** of another variable in RAM rather than storing the actual direct value.\n\n"
                "**Core Operators:**\n"
                "- **Address-of Operator (`&`):** Retrieves the memory address of a variable (e.g., `int* ptr = &val;`).\n"
                "- **Dereference Operator (`*`):** Accesses or modifies the value stored at the memory address pointed to (e.g., `*ptr = 42;`).\n\n"
                "**Why Pointers are Essential:**\n"
                "1. **Pass-by-Reference:** Allows functions to modify the caller's variables directly without creating expensive copies in memory.\n"
                "2. **Dynamic Memory Allocation:** Used with `malloc()`, `calloc()`, and `free()` (or `new`/`delete` in C++) to allocate memory on the Heap at runtime.\n"
                "3. **Complex Data Structures:** Pointers form the structural links connecting nodes in Linked Lists, Trees, and Graphs.\n"
                "4. **Smart Pointers (C++11):** `std::unique_ptr` and `std::shared_ptr` provide RAII automatic memory reclamation, preventing memory leaks."
            )

        if 'garbage collection' in term or term == 'gc':
            return (
                "### Garbage Collection (GC) in Software Runtimes\n\n"
                "**Definition:**\n"
                "Garbage Collection is an automated memory management feature built into programming language runtimes "
                "(such as Java Virtual Machine, Python, Node.js V8, Go, and .NET CLR). It automatically detects and frees memory "
                "allocated to objects that are no longer referenced or reachable by the running program.\n\n"
                "**Major Garbage Collection Algorithms:**\n"
                "1. **Reference Counting:** Tracks the number of active references to each object. When the count drops to 0, memory is immediately reclaimed (used in Python along with a cyclic GC).\n"
                "2. **Mark-and-Sweep:** Pauses or runs concurrently, traversing the object graph from root references ('marking' live objects) and then sweeping away unreached objects.\n"
                "3. **Generational Garbage Collection:** Objects are divided into generations (Eden/Young and Old/Tenured). Young objects are collected frequently because most objects die young (Weak Generational Hypothesis)."
            )

        if 'stack vs heap' in term or ('stack' in term and 'heap' in term and 'memory' in full_query):
            return (
                "### Stack vs. Heap Memory\n\n"
                "| Dimension | Stack Memory | Heap Memory |\n"
                "| :--- | :--- | :--- |\n"
                "| **Allocation** | Contiguous, managed automatically by CPU | Dynamic, managed via code or Garbage Collector |\n"
                "| **Access Speed** | Extremely fast (single pointer push/pop) | Slower (pointer dereferencing, fragmentation) |\n"
                "| **Structure** | LIFO (Last-In, First-Out) call frames | Hierarchical / unstructured memory pool |\n"
                "| **Stored Content** | Primitive types, local variables, function calls | Large objects, dynamic arrays, reference types |\n"
                "| **Size Limit** | Fixed and small (triggers `StackOverflowError`) | Large, limited only by physical/virtual RAM |\n"
                "| **Thread Safety** | Each thread has its own private stack | Shared across all threads in the process |"
            )

        # ==========================================
        # 1. ARTIFICIAL INTELLIGENCE & MACHINE LEARNING
        # ==========================================
        if 'machine learning' in term or 'machine learning' in full_query:
            return (
                "### Machine Learning (ML)\n\n"
                "**Definition:**\n"
                "Machine Learning (ML) is a branch of Artificial Intelligence (AI) and computer science focused on "
                "building applications that learn from data and improve their accuracy over time without being "
                "explicitly programmed with hardcoded rules for every scenario.\n\n"
                "**Three Primary Types of Machine Learning:**\n"
                "1. **Supervised Learning:** The model trains on labeled input-output pairs. "
                "Common algorithms include Linear Regression, Logistic Regression, Decision Trees, Random Forests, and Support Vector Machines (SVM).\n"
                "2. **Unsupervised Learning:** The model analyzes unlabeled data to uncover hidden patterns or groupings. "
                "Common algorithms include K-Means Clustering, Hierarchical Clustering, and Principal Component Analysis (PCA).\n"
                "3. **Reinforcement Learning:** An autonomous agent learns by taking actions within an environment to maximize cumulative rewards. "
                "Widely used in robotics, autonomous navigation, and gaming AI (e.g., Q-Learning, Deep Q-Networks).\n\n"
                "**Standard Machine Learning Lifecycle:**\n"
                "- **Data Ingestion & Cleaning:** Removing duplicates, handling null values, feature scaling.\n"
                "- **Feature Engineering:** Extracting relevant signals and encoding categorical variables.\n"
                "- **Model Training & Hyperparameter Tuning:** Optimizing parameters via cross-validation.\n"
                "- **Evaluation:** Assessing performance using metrics such as Precision, Recall, F1-Score, and ROC-AUC.\n"
                "- **Deployment & Monitoring:** Serving models via REST APIs and tracking data drift.\n\n"
                "**Key Industry Libraries:**\n"
                "- **Python:** Scikit-Learn, PyTorch, TensorFlow, Pandas, NumPy, XGBoost, LightGBM\n\n"
                "*(Note: If you need a specific code implementation, such as training an ML regression or classification model, just ask 'write machine learning code in python'.)*"
            )

        if 'deep learning' in term or 'neural network' in term:
            return (
                "### Deep Learning & Neural Networks\n\n"
                "**Definition:**\n"
                "Deep Learning is a specialized subfield of Machine Learning based on Artificial Neural Networks (ANNs) "
                "with multiple hidden layers (hence 'deep'). It enables computers to solve complex perceptual problems like "
                "image recognition, natural language processing (NLP), and speech synthesis.\n\n"
                "**Key Architectures:**\n"
                "- **Convolutional Neural Networks (CNNs):** Designed for grid-structured data like images and computer vision.\n"
                "- **Recurrent Neural Networks (RNNs & LSTMs):** Designed for sequential data such as time series and text.\n"
                "- **Transformers:** Self-attention based models that power Large Language Models (LLMs) like GPT, Gemini, and Claude.\n\n"
                "**Leading Frameworks:** PyTorch, TensorFlow, Keras, Hugging Face Transformers."
            )

        if 'artificial intelligence' in term or term == 'ai':
            return (
                "### Artificial Intelligence (AI)\n\n"
                "**Definition:**\n"
                "Artificial Intelligence refers to the simulation of human intelligence by machines, particularly computer systems. "
                "It encompasses perception, reasoning, decision-making, natural language communication, and autonomous problem solving.\n\n"
                "**Main Disciplines of AI:**\n"
                "- **Machine Learning & Deep Learning:** Data-driven statistical models.\n"
                "- **Natural Language Processing (NLP):** Understanding and generating human text and speech.\n"
                "- **Computer Vision:** Image classification, object detection, and visual scene understanding.\n"
                "- **Robotics:** Autonomous motion, sensor fusion, and real-time environment interaction."
            )

        # ==========================================
        # 1B. PROGRAMMING FRAMEWORKS MASTERY
        # ==========================================
        if 'python framework' in term or 'python frameworks' in full_query or ('framework' in term and 'python' in full_query):
            return (
                "### Modern Python Frameworks & Libraries\n\n"
                "Python has a rich ecosystem of frameworks spanning web development, data science, and asynchronous microservices:\n\n"
                "**1. Web & API Frameworks:**\n"
                "- **FastAPI:** Modern, high-performance async API framework built on Starlette and Pydantic. It provides automatic OpenAPI/Swagger interactive documentation (`/docs`), strict type validation, and concurrency support.\n"
                "- **Django:** Full-featured 'batteries-included' web framework with a powerful ORM, built-in Admin dashboard, user authentication, and database migration engine.\n"
                "- **Flask:** Lightweight, minimalist WSGI microframework designed for rapid prototyping, customizable extensions, and modular microservices.\n\n"
                "**2. Data Science & Machine Learning:**\n"
                "- **PyTorch & TensorFlow:** Industry standard deep learning frameworks for building and deploying neural networks.\n"
                "- **Scikit-Learn:** Comprehensive library for classical machine learning algorithms (Random Forest, SVM, K-Means, PCA).\n"
                "- **Pandas & NumPy:** Core data manipulation, matrix operations, and high-performance array analytics.\n\n"
                "**3. Asynchronous & Distributed Tasks:**\n"
                "- **Celery:** Distributed task queue for asynchronous background jobs using Redis or RabbitMQ.\n\n"
                "*(To see working code for any framework, ask 'create a fastapi route' or 'flask example'.)*"
            )

        if 'javascript framework' in term or 'frontend framework' in term or ('framework' in term and ('javascript' in full_query or 'frontend' in full_query)):
            return (
                "### Leading JavaScript & Frontend Frameworks\n\n"
                "The JavaScript/TypeScript ecosystem powers modern interactive web applications:\n\n"
                "**1. Component-Based UI Frameworks:**\n"
                "- **React.js:** Declarative, component-driven UI library using a Virtual DOM and functional Hooks (`useState`, `useEffect`).\n"
                "- **Next.js:** Full-stack React framework with Server-Side Rendering (SSR), Static Site Generation (SSG), and the modern App Router.\n"
                "- **Vue.js:** Approachable and versatile progressive framework featuring reactive two-way data binding and the Composition API.\n"
                "- **Angular:** Google's robust enterprise framework with built-in TypeScript, Dependency Injection, and RxJS reactive streams.\n\n"
                "**2. Backend JavaScript (Node.js):**\n"
                "- **Express.js:** Minimalist, unopinionated web server and REST API framework.\n"
                "- **NestJS:** Enterprise TypeScript framework inspired by Angular architecture (Modules, Controllers, Services)."
            )

        if 'java framework' in term or ('framework' in term and 'java' in full_query):
            return (
                "### Leading Java Enterprise Frameworks\n\n"
                "**1. Spring Boot:**\n"
                "The de facto enterprise standard for building stand-alone, production-grade Spring-based applications. "
                "Features include Inversion of Control (IoC), Dependency Injection (DI), Spring Data JPA, and embedded Tomcat/Jetty servers.\n\n"
                "**2. Hibernate:**\n"
                "An Object-Relational Mapping (ORM) framework that maps Java domain models to relational database tables, eliminating boilerplate SQL queries.\n\n"
                "**3. Quarkus & Micronaut:**\n"
                "Next-generation, Kubernetes-native Java frameworks designed for instant startup and low memory footprints via GraalVM ahead-of-time (AOT) compilation."
            )

        # ==========================================
        # 2. WEB & ARCHITECTURE CONCEPTS
        # ==========================================
        if 'rest api' in term or 'restful' in term:
            return (
                "### REST API (Representational State Transfer)\n\n"
                "**Definition:**\n"
                "A REST API is an architectural style for networked web applications that enables stateless communication between "
                "a client and a server over HTTP standard protocols.\n\n"
                "**Key Architectural Constraints:**\n"
                "1. **Statelessness:** Every HTTP request contains all necessary credentials and context. The server stores no client session state.\n"
                "2. **Client-Server Separation:** User interface concerns are decoupled from data storage and business logic.\n"
                "3. **Uniform Interface:** Standard HTTP verbs (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) with predictable URI endpoints.\n"
                "4. **Cacheability:** Responses indicate whether they can be cached to improve performance.\n"
                "5. **Layered System:** Clients cannot distinguish whether they are connected directly to the end server or intermediate proxies/gateways."
            )

        if 'microservices' in term or 'microservice' in term:
            return (
                "### Microservices Architecture\n\n"
                "**Definition:**\n"
                "Microservices is an architectural design where an application is composed of small, independent services that "
                "communicate over lightweight protocols (such as HTTP REST, gRPC, or event streams like Kafka/RabbitMQ).\n\n"
                "**Benefits vs. Monolith:**\n"
                "- **Independent Deployments:** Deploy new features or bug fixes without redeploying the entire codebase.\n"
                "- **Technology Diversity:** Different services can use different programming languages or databases.\n"
                "- **Fault Isolation:** A failure in one microservice does not automatically bring down the entire application.\n"
                "- **Horizontal Scalability:** Scale only resource-intensive services rather than the whole monolith."
            )

        if 'sql vs nosql' in term or ('sql' in term and 'nosql' in term):
            return (
                "### SQL vs. NoSQL Databases\n\n"
                "| Feature | SQL (Relational) | NoSQL (Non-Relational) |\n"
                "| :--- | :--- | :--- |\n"
                "| **Data Structure** | Tables with rows and columns | Documents (JSON), Key-Value, Columnar, Graph |\n"
                "| **Schema** | Predefined, rigid, strictly typed schema | Dynamic, flexible, schema-less |\n"
                "| **Scaling** | Vertical scaling (Scale-Up: CPU/RAM) | Horizontal scaling (Scale-Out: sharding nodes) |\n"
                "| **Transaction Model** | ACID compliance (Atomicity, Consistency, Isolation, Durability) | BASE model (Basically Available, Soft-state, Eventual consistency) |\n"
                "| **Leading Systems** | PostgreSQL, MySQL, SQLite, Oracle | MongoDB, Redis, Apache Cassandra, DynamoDB |\n"
                "| **Ideal Use Cases** | Financial ledgers, complex relational joins, ERP | Big data streaming, real-time caching, mobile JSON feeds |"
            )

        # ==========================================
        # 3. CLOUD & DEVOPS CONCEPTS
        # ==========================================
        if 'docker' in term and 'kubernetes' not in term:
            return (
                "### Docker & Containerization\n\n"
                "**Definition:**\n"
                "Docker is an open-source containerization platform that allows developers to package an application and all its "
                "runtime dependencies into a standardized unit called a container.\n\n"
                "**Core Components:**\n"
                "- **Dockerfile:** Declarative recipe defining the OS environment, dependencies, and launch command.\n"
                "- **Docker Image:** An immutable, layered template created from building a Dockerfile.\n"
                "- **Docker Container:** A running, isolated instance of an image sharing the host OS kernel.\n"
                "- **Docker Compose:** A tool for defining and running multi-container Docker applications via YAML."
            )

        if 'kubernetes' in term or term == 'k8s':
            return (
                "### Kubernetes (K8s)\n\n"
                "**Definition:**\n"
                "Kubernetes is an open-source container orchestration platform originally designed by Google. It automates "
                "the deployment, scaling, health-monitoring, and management of containerized applications across clusters of servers.\n\n"
                "**Key Concepts:**\n"
                "- **Pod:** The smallest deployable computing unit in Kubernetes, hosting one or more containers.\n"
                "- **Service:** An abstraction defining a logical set of Pods and access policies (ClusterIP, NodePort, LoadBalancer).\n"
                "- **Deployment:** Declarative state manager for Pods, managing zero-downtime rolling updates.\n"
                "- **Ingress:** Manages external HTTP/HTTPS routing into services within the cluster."
            )

        # ==========================================
        # 4. PROGRAMMING CONCEPTS & COMPUTER SCIENCE
        # ==========================================
        if 'oop' in term or 'object oriented' in term or 'object-oriented' in term:
            return (
                "### Object-Oriented Programming (OOP)\n\n"
                "**Definition:**\n"
                "Object-Oriented Programming (OOP) is a programming paradigm based on the concept of 'objects', "
                "which can contain data (attributes/properties) and code (methods/functions).\n\n"
                "**The Four Core Pillars of OOP:**\n"
                "1. **Encapsulation:** Bundling the data and the methods that operate on that data within a single unit (class), "
                "and restricting direct access to internal state using private/protected access modifiers.\n"
                "2. **Abstraction:** Hiding complex implementation details and exposing only the necessary high-level interface to users.\n"
                "3. **Inheritance:** Enabling a new class (child/subclass) to inherit fields and methods from an existing class (parent/superclass), promoting code reuse.\n"
                "4. **Polymorphism:** Allowing entities (methods or objects) to take on multiple forms—such as method overriding (runtime) and method overloading (compile-time).\n\n"
                "**Supported Languages:** Java, C++, Python, C#, TypeScript, PHP, Ruby, Dart."
            )

        if 'recursion' in term:
            return (
                "### Recursion in Computer Science\n\n"
                "**Definition:**\n"
                "Recursion is a problem-solving technique where a function calls itself directly or indirectly to solve smaller instances "
                "of the same problem until a terminating condition is met.\n\n"
                "**Two Essential Components:**\n"
                "1. **Base Case:** The condition that stops recursion and prevents an infinite loop (`StackOverflowError`).\n"
                "2. **Recursive Step:** The logic where the function calls itself with modified parameters moving closer to the base case.\n\n"
                "**Classic Examples:**\n"
                "- Factorial calculation: $n! = n \\times (n-1)!$\n"
                "- Fibonacci sequence: $F(n) = F(n-1) + F(n-2)$\n"
                "- Tree and Graph traversals (DFS, Binary Search Tree searches)\n\n"
                "*(To see working code for recursion, ask 'write recursive fibonacci in python'.)*"
            )

        if 'big o' in term or 'complexity' in term or 'time complexity' in term:
            return (
                "### Big-O Notation & Algorithm Complexity\n\n"
                "**Definition:**\n"
                "Big-O notation is a mathematical notation that describes the limiting behavior of a function when the argument "
                "tends towards a particular value or infinity. In computer science, it classifies algorithms according to how their "
                "run time or space requirements grow as the input size ($N$) grows.\n\n"
                "**Common Time Complexities (From Fastest to Slowest):**\n"
                "1. **$O(1)$ - Constant Time:** Hash table lookup, array index access.\n"
                "2. **$O(\\log N)$ - Logarithmic Time:** Binary Search on sorted array.\n"
                "3. **$O(N)$ - Linear Time:** Linear search, single loop through array.\n"
                "4. **$O(N \\log N)$ - Linearithmic Time:** Efficient sorting algorithms (Merge Sort, Quick Sort average, Heap Sort).\n"
                "5. **$O(N^2)$ - Quadratic Time:** Nested loops (Bubble Sort, Selection Sort, Insertion Sort).\n"
                "6. **$O(2^N)$ - Exponential Time:** Recursive calculation of Fibonacci, power set generation.\n"
                "7. **$O(N!)$ - Factorial Time:** Traveling Salesperson brute force."
            )

        if 'async' in term or 'await' in term or 'promise' in term or 'event loop' in term:
            return (
                "### Asynchronous Programming & Event Loop\n\n"
                "**Definition:**\n"
                "Asynchronous programming is a non-blocking execution model where long-running operations (such as network I/O, "
                "file reading, or database queries) run in the background without freezing the main application execution thread.\n\n"
                "**Core Mechanisms:**\n"
                "- **Event Loop:** A single-threaded runtime loop (used in Node.js, JavaScript browsers, Python `asyncio`) that constantly monitors the call stack and dequeues callback tasks from the task/microtask queue.\n"
                "- **Promises:** Objects representing the eventual completion (or failure) of an asynchronous operation.\n"
                "- **Async/Await:** Syntactic sugar built on top of Promises/Futures that allows writing asynchronous code with clean, synchronous-looking readability.\n\n"
                "**Key Advantages:** High concurrency throughput, low memory footprint, responsive user interfaces."
            )

        if 'solid' in term:
            return (
                "### SOLID Principles in Software Engineering\n\n"
                "SOLID is an acronym for five design principles for writing maintainable, understandable, and flexible object-oriented software:\n\n"
                "1. **S - Single Responsibility Principle (SRP):** A class should have one, and only one, reason to change.\n"
                "2. **O - Open/Closed Principle (OCP):** Software entities should be open for extension, but closed for modification.\n"
                "3. **L - Liskov Substitution Principle (LSP):** Subtypes must be substitutable for their base types without altering program correctness.\n"
                "4. **I - Interface Segregation Principle (ISP):** Clients should not be forced to depend upon interfaces they do not use.\n"
                "5. **D - Dependency Inversion Principle (DIP):** High-level modules should not depend on low-level modules; both should depend upon abstractions."
            )

        if 'graphql' in term:
            return (
                "### GraphQL vs. REST APIs\n\n"
                "**Definition:**\n"
                "GraphQL is an open-source data query and manipulation language for APIs, created by Meta, providing a complete "
                "and understandable description of the data in your API.\n\n"
                "**Key Differences from REST:**\n"
                "- **Precise Fetching:** Clients request exactly the fields they need, eliminating over-fetching and under-fetching.\n"
                "- **Single Endpoint:** Uses a single HTTP POST endpoint (`/graphql`) rather than numerous REST URI routes (`/users`, `/posts`).\n"
                "- **Schema & Type System:** Strongly typed schema defining queries, mutations, and subscriptions.\n"
                "- **Subscriptions:** Built-in real-time updates over WebSockets."
            )

        if term == 'api' or 'what is an api' in full_query or 'what is api' in full_query:
            return (
                "### API (Application Programming Interface)\n\n"
                "**Definition:**\n"
                "An Application Programming Interface (API) is a formal software intermediary and contract that defines how two separate "
                "software applications communicate with each other using requests, endpoints, and data payloads.\n\n"
                "**Major Types of APIs:**\n"
                "1. **REST APIs (HTTP/JSON):** Stateless, resource-oriented architectures using HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`).\n"
                "2. **GraphQL:** Query language allowing clients to request exact fields across complex relational graphs in a single request.\n"
                "3. **gRPC:** High-performance, low-latency RPC framework by Google using Protocol Buffers over HTTP/2 for microservices.\n"
                "4. **WebSockets:** Full-duplex, persistent two-way communication channel for real-time chat, notifications, and live streaming."
            )

        if 'git' in term:
            return (
                "### Git (Distributed Version Control System)\n\n"
                "**Definition:**\n"
                "Git is a free and open-source distributed version control system designed to handle everything from small to very "
                "large projects with speed, integrity, and non-linear branching workflows.\n\n"
                "**Core Git Concepts:**\n"
                "- **Repository (Repo):** Project directory tracked by Git containing `.git` database and commit history.\n"
                "- **Commit:** Cryptographically secured (SHA) snapshot of your project state with author and message.\n"
                "- **Branching (`git checkout -b`):** Lightweight movable pointer to commits, allowing isolated feature development.\n"
                "- **Merge & Rebase:** Combining branches (`merge` preserves commit history topology; `rebase` creates a linear history).\n"
                "- **Staging Area (`git add`):** Intermediate indexing step preparing files for the next commit."
            )

        if 'jwt' in term or 'json web token' in term:
            return (
                "### JWT (JSON Web Token)\n\n"
                "**Definition:**\n"
                "A JSON Web Token (JWT) is an open, industry-standard (RFC 7519) compact and self-contained method for securely "
                "transmitting information between parties as a verifiable JSON object.\n\n"
                "**Structure of a JWT (Separated by dots `.`):**\n"
                "1. **Header:** Contains the token type (`JWT`) and signing algorithm (`HS256` or `RS256`).\n"
                "2. **Payload:** Contains claims (user ID, username, roles, expiration timestamp `exp`).\n"
                "3. **Signature:** Created by hashing the base64-encoded header and payload with a server-side secret key.\n\n"
                "**Key Advantage:** Stateless authentication—the backend server validates the cryptographic signature without querying a database or session store."
            )

        if 'stack' in term and ('data structure' in full_query or 'what is' in full_query or term == 'stack'):
            return (
                "### Stack Data Structure (LIFO)\n\n"
                "**Definition:**\n"
                "A Stack is a linear data structure that follows the **Last-In, First-Out (LIFO)** principle: the last element added "
                "is the first element to be removed.\n\n"
                "**Primary Operations (All $O(1)$ Time Complexity):**\n"
                "- `push(x)`: Inserts element $x$ onto the top of the stack.\n"
                "- `pop()`: Removes and returns the top element.\n"
                "- `peek()` / `top()`: Inspects the top element without removing it.\n"
                "- `isEmpty()`: Checks if the stack contains elements.\n\n"
                "**Real-World Applications:** Browser forward/back navigation, Undo/Redo in editors, Function call stacks, Expression parsing & syntax checking."
            )

        if 'queue' in term and ('data structure' in full_query or 'what is' in full_query or term == 'queue'):
            return (
                "### Queue Data Structure (FIFO)\n\n"
                "**Definition:**\n"
                "A Queue is a linear data structure that follows the **First-In, First-Out (FIFO)** principle: the first element added "
                "is the first element to be removed.\n\n"
                "**Primary Operations (All $O(1)$ Time Complexity):**\n"
                "- `enqueue(x)`: Inserts element $x$ at the rear (tail) of the queue.\n"
                "- `dequeue()`: Removes and returns the element at the front (head) of the queue.\n"
                "- `front()`: Inspects the front element without removing it.\n\n"
                "**Real-World Applications:** CPU scheduling, Printer spooling, Breadth-First Search (BFS) in graphs, Message queues (RabbitMQ, Kafka)."
            )

        if 'linked list' in term:
            return (
                "### Linked List Data Structure\n\n"
                "**Definition:**\n"
                "A Linked List is a linear data structure where elements (called nodes) are stored non-contiguously in memory. "
                "Each node consists of two parts: data and a reference (pointer) to the next node in sequence.\n\n"
                "**Types of Linked Lists:**\n"
                "1. **Singly Linked List:** Each node points only to the next node (`head -> node -> next -> NULL`).\n"
                "2. **Doubly Linked List:** Each node maintains two pointers (`prev` and `next`), allowing bidirectional traversal.\n"
                "3. **Circular Linked List:** The last node's `next` pointer loops back to the `head`.\n\n"
                "**Comparison with Arrays:**\n"
                "- Insertion/Deletion at beginning: $O(1)$ in Linked List vs. $O(N)$ in Array.\n"
                "- Random element access: $O(N)$ in Linked List vs. $O(1)$ in Array."
            )

        return None

