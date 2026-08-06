"""Brain module - Purple Ultra AI's intelligent offline reasoning engine.

Massive knowledge base, reasoning engine, expert modules, and learning system.
Trained to provide expert-level responses across all domains without internet.
"""

from __future__ import annotations

import json
import random
import re
import math
import hashlib
import string
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from collections import defaultdict

# Pre-computed translation table for punctuation removal (module-level, computed once)
_PUNCT_TABLE = str.maketrans('', '', string.punctuation)

# Generic response prefixes (module-level constant, not rebuilt each call)
_GENERIC_RESPONSES = ("I see.", "Got it.", "Interesting", "Let me help", "Here's what I know",
                      "I understand", "Tell me more", "What else", "How can I help",
                      "Great question", "Let me explain", "Let me walk you",
                      "Here's how", "Let me think", "That's a good",
                      "I'd say", "Based on my", "Regarding", "Let me consider",
                      "I'm processing", "What aspect", "How can I assist")

from ..config.settings import Config
from ..brain.llm import LLMManager, LLMMessage, build_system_prompt
from ..brain.purple_brain import PurpleBrain
from ..brain.neural_network import BrainNeuralNetwork
from ..brain.self_learning import SelfLearningSystem
from ..brain.massive_network import BrainMassiveNetwork
from ..brain.image_input import ImageInput
from ..brain.brain_enhance import EXTRA_KNOWLEDGE, EXTRA_ALIASES, EXTRA_INTENT_PATTERNS
from ..brain.auto_trainer import AutoTrainer
from ..brain.unified_memory import UnifiedMemoryManager


@dataclass
class Decision:
    say: str
    mood: str = "neutral"
    effect: str | None = None
    action: dict[str, Any] | None = None
    actions: list[dict[str, Any]] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════
#  MASSIVE KNOWLEDGE BASE (300+ entries)
# ═══════════════════════════════════════════════════════════════════════════

_KNOWLEDGE: dict[str, str] = {
    # ── PROGRAMMING LANGUAGES ──
    "python": "Python is a high-level, interpreted language created by Guido van Rossum (1991). Known for readability, versatility, and vast ecosystem. Supports OOP, functional, and procedural paradigms. Key features: dynamic typing, list comprehensions, decorators, generators, async/await. Used in web dev (Django, Flask), data science (pandas, numpy), AI/ML (TensorFlow, PyTorch), automation, and scripting.",
    "javascript": "JavaScript is a dynamic, prototype-based language created by Brendan Eich (1995). Runs in browsers and servers (Node.js). Key features: closures, prototypal inheritance, event loop, async/await, destructuring, modules. Frameworks: React, Vue, Angular, Svelte. Runtime: V8 (Chrome/Node), SpiderMonkey (Firefox).",
    "typescript": "TypeScript is a typed superset of JavaScript developed by Microsoft (2012). Adds static type checking, interfaces, generics, enums, and advanced tooling. Compiles to JavaScript. Used for large-scale applications. Key: type inference, conditional types, mapped types, declaration files.",
    "rust": "Rust is a systems language focused on safety, speed, and concurrency (Mozilla, 2010). Ownership system prevents memory bugs at compile time. No garbage collector. Pattern matching, algebraic types, traits, lifetimes. Used in: OS kernels, browsers (Servo), game engines, embedded systems, CLI tools.",
    "go": "Go (Golang) is a statically typed language by Google (2009). Known for simplicity, fast compilation, and built-in concurrency (goroutines, channels). Garbage collected. Excellent standard library. Used in: Docker, Kubernetes, Terraform, microservices, CLI tools.",
    "java": "Java is a class-based, object-oriented language by Sun Microsystems (1995). Write once, run anywhere (JVM). Strongly typed, garbage collected. Key: interfaces, generics, annotations, streams, modules. Used in: enterprise, Android, web apps (Spring), big data (Hadoop).",
    "c": "C is a procedural systems language (Dennis Ritchie, 1972). Foundation of modern computing. Manual memory management, pointers, preprocessor. Extremely fast and portable. Used in: operating systems, embedded systems, drivers, game engines. Basis for C++, Java, Python, and many others.",
    "c++": "C++ is a multi-paradigm language extending C (Bjarne Stroustrup, 1983). Adds classes, templates, RAII, exceptions, STL. Zero-cost abstractions. Used in: game engines, browsers, databases, high-performance computing, operating systems.",
    "c#": "C# is a modern, object-oriented language by Microsoft (2000). Runs on .NET. Features: LINQ, async/await, pattern matching, records, nullable reference types. Used in: Windows apps, game dev (Unity), web (ASP.NET), enterprise software.",
    "ruby": "Ruby is a dynamic, object-oriented language (Yukihiro Matsumoto, 1995). Everything is an object. Known for elegance and developer happiness. Ruby on Rails framework revolutionized web development. Used in: web apps, automation, prototyping.",
    "php": "PHP is a server-side scripting language (Rasmus Lerdorf, 1995). Powers ~77% of websites with known server-side languages. Laravel and Symfony frameworks. Evolved significantly with PHP 7/8 (typed properties, JIT compiler). Used in: WordPress, Facebook, Wikipedia.",
    "swift": "Swift is a modern language by Apple (2014) for iOS/macOS development. Safety features (optionals, value types), fast performance, modern syntax. Replaced Objective-C for Apple platform development. Also works on servers (Vapor).",
    "kotlin": "Kotlin is a modern JVM language by JetBrains (2011). 100% Java interoperable. Null safety, coroutines, extension functions, data classes. Official language for Android development since 2019. Concise and expressive.",
    "scala": "Scala is a hybrid functional/OOP language on the JVM (Martin Odersky, 2004). Strong static typing, pattern matching, actor model (Akka). Used in big data (Apache Spark), distributed systems, and enterprise applications.",
    "haskell": "Haskell is a purely functional language (1990). Lazy evaluation, strong static typing, type inference, monads for side effects. Used in: academia, finance, compilers. Known for mathematical rigor and correctness.",
    "lisp": "Lisp is one of the oldest languages (1958, John McCarthy). Homoiconic (code as data), macros, REPL-driven development. Dialects: Common Lisp, Scheme, Clojure. Used in: AI research, Emacs, Clojure for web/data apps.",
    "sql": "SQL (Structured Query Language) manages relational databases. Key commands: SELECT, INSERT, UPDATE, DELETE, JOIN, WHERE, GROUP BY, HAVING, ORDER BY, subqueries, CTEs, window functions. Each database (PostgreSQL, MySQL, SQLite) has extensions.",
    "html": "HTML (HyperText Markup Language) structures web content. Semantic elements: header, nav, main, article, section, footer. Forms, tables, multimedia. HTML5 APIs: canvas, geolocation, web storage, web workers, service workers.",
    "css": "CSS (Cascading Style Sheets) styles web pages. Key: selectors, specificity, box model, flexbox, grid, animations, custom properties (variables), media queries, @layer, container queries. Preprocessors: Sass, Less.",
    "bash": "Bash (Bourne Again Shell) is a Unix shell and command language. Scripting, pipeline composition, process control, job control, arithmetic expansion, arrays, functions. Used for automation, system administration, DevOps.",

    # ── DATA STRUCTURES & ALGORITHMS ──
    "array": "An array stores elements in contiguous memory. O(1) random access by index. Insert/delete O(n) worst case. Static (fixed size) or dynamic (resizable). Python: list, tuple. Java: ArrayList, Arrays.",
    "linked list": "A linked list stores elements in nodes with pointers. O(1) insert/delete at head. No random access. Types: singly, doubly, circular. Used when frequent insertions/deletions, unknown size. Cache-unfriendly.",
    "stack": "A stack is LIFO (Last In, First Out). push/pop/peek in O(1). Used for: function call stack, undo/redo, expression evaluation, backtracking, depth-first search. Python: list append/pop.",
    "queue": "A queue is FIFO (First In, First Out). enqueue/dequeue in O(1). Types: priority queue (heap-based), deque (double-ended), circular queue. Used for: BFS, task scheduling, print queues, buffers.",
    "hash table": "A hash table stores key-value pairs using a hash function. Average O(1) insert/lookup/delete. Collision handling: chaining (linked lists), open addressing (linear/quadratic probing). Python: dict, set.",
    "hash map": "A hash map maps keys to values via hashing. Average O(1) operations. Load factor affects performance. Resizing: typically double capacity when 75% full. Python dict, Java HashMap, Go map.",
    "tree": "A tree is a hierarchical structure with nodes. Root, internal nodes, leaves. Types: binary tree, BST (O(log n) search), AVL (self-balancing), Red-Black, B-tree (databases), Trie (strings), heap (priority).",
    "binary tree": "A binary tree has at most 2 children per node. Traversals: in-order (sorted for BST), pre-order, post-order, level-order (BFS). Height: O(log n) balanced, O(n) degenerate. Used in: heaps, expression trees, decision trees.",
    "bst": "A Binary Search Tree maintains sorted order: left < parent < right. Search/insert/delete average O(log n), worst O(n) if unbalanced. Self-balancing variants (AVL, Red-Black) guarantee O(log n).",
    "graph": "A graph is vertices connected by edges. Types: directed/undirected, weighted/unweighted. Representations: adjacency list (sparse), adjacency matrix (dense). Algorithms: BFS, DFS, Dijkstra, Floyd-Warshall, Kruskal, Prim.",
    "heap": "A heap is a complete binary tree satisfying heap property (min or max). Insert O(log n), extract-min/max O(log n), peek O(1). Used for: priority queues, heapsort, scheduling. Python: heapq module.",
    "trie": "A trie (prefix tree) stores strings character by character. Search/insert O(m) where m is string length. Used for: autocomplete, spell check, IP routing, word games. Space-efficient for shared prefixes.",
    "sorting": "Sorting algorithms: Bubble O(n²), Selection O(n²), Insertion O(n²) adaptive, Merge O(n log n) stable, Quick O(n log n) avg in-place, Heap O(n log n), Counting/Radix/Bucket O(n) for integers. Python uses Timsort (hybrid merge+insertion).",
    "searching": "Searching: Linear O(n), Binary O(log n) on sorted arrays, Hash-based O(1) average, Tree-based O(log n). Binary search: compare middle, eliminate half. Requires sorted data.",
    "algorithm": "An algorithm is a finite sequence of steps to solve a problem. Categories: sorting, searching, graph traversal, dynamic programming, greedy, divide-and-conquer, backtracking. Analysis: time/space complexity using Big-O notation.",
    "data structure": "Data structures organize data for efficient access. Linear: array, linked list, stack, queue. Non-linear: tree, graph, hash table. Choose based on: access pattern, insert/delete frequency, memory constraints, concurrency needs.",
    "big o notation": "Big-O describes upper bound of growth rate. O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, O(n²) quadratic, O(n³) cubic, O(2ⁿ) exponential, O(n!) factorial. Drop constants: 2n → O(n).",
    "dynamic programming": "DP solves complex problems by breaking into overlapping subproblems. Top-down (memoization) or bottom-up (tabulation). Key: optimal substructure + overlapping subproblems. Examples: Fibonacci, knapsack, edit distance, LCS.",
    "greedy algorithm": "Greedy algorithms make locally optimal choices at each step. Works when: greedy choice property + optimal substructure. Examples: Huffman coding, activity selection, Prim/Kruskal MST, Dijkstra shortest path. Not always optimal.",
    "recursion": "Recursion is when a function calls itself. Requires base case to stop. Each call adds to call stack. Can be converted to iteration with explicit stack. Used in: tree traversal, divide-and-conquer, backtracking, mathematical sequences.",
    "binary search": "Binary search finds an element in sorted data in O(log n). Compare target with middle element, eliminate half. Variants: lower bound, upper bound, rotated array search. Requires sorted input.",
    "merge sort": "Merge sort divides array in half recursively, then merges sorted halves. O(n log n) time, O(n) space. Stable sort. Guaranteed performance. Used in: external sorting, linked list sorting, TimSort component.",
    "quicksort": "Quick sort picks a pivot, partitions array into less/greater, recurses. Average O(n log n), worst O(n²) with bad pivots. In-place (O(log n) stack space). Unstable. Python uses introsort (hybrid with heapsort).",

    # ── WEB DEVELOPMENT ──
    "react": "React is a JavaScript library for building UIs (Meta, 2013). Component-based, declarative, virtual DOM. Hooks (useState, useEffect, useContext), concurrent features, server components. Ecosystem: Next.js, React Native.",
    "vue": "Vue.js is a progressive JavaScript framework (Evan You, 2014). Reactive data binding, component composition, Composition API. Single-file components (.vue). Ecosystem: Nuxt.js, Pinia, Vue Router.",
    "angular": "Angular is a TypeScript framework by Google. Full MVC framework: routing, forms, HTTP, testing. Two-way data binding, dependency injection, RxJS observables, signals. CLI for code generation.",
    "svelte": "Svelte is a compiler-based framework (Rich Harris, 2016). No virtual DOM - compiles to efficient vanilla JS. Less boilerplate, smaller bundle size. Runes (new reactivity system). SvelteKit for full-stack.",
    "next.js": "Next.js is a React framework by Vercel. Server-side rendering (SSR), static generation (SSG), API routes, app router with React Server Components, middleware, image optimization, font optimization.",
    "node.js": "Node.js is a JavaScript runtime (Ryan Dahl, 2009). V8 engine, event-driven, non-blocking I/O. npm/yarn package managers. Used for: APIs, real-time apps, microservices, build tools, serverless functions.",
    "flask": "Flask is a lightweight Python web framework (Armin Ronacher, 2010). Micro-framework: routing, templates (Jinja2), extensions. Minimal core, add what you need. Used for APIs, prototypes, small-medium apps.",
    "django": "Django is a Python web framework (2005). Batteries included: ORM, admin, auth, forms, middleware, CSRF protection. MTV pattern. Django REST Framework for APIs. Used by Instagram, Pinterest, Mozilla.",
    "rest api": "REST APIs use HTTP methods on resources: GET (read), POST (create), PUT (full update), PATCH (partial update), DELETE (remove). Stateless, resource-based URLs, JSON/XML. Status codes: 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Error.",
    "graphql": "GraphQL is a query language for APIs (Facebook, 2015). Single endpoint, client specifies exact data needs. Strongly typed schema with queries, mutations, subscriptions. Eliminates over/under-fetching.",
    "websocket": "WebSocket provides full-duplex communication over TCP. Persistent connection, low latency. Used for: chat apps, live feeds, gaming, collaborative editing. Handshake starts as HTTP, upgrades to WebSocket.",
    "http": "HTTP (HyperText Transfer Protocol) is the foundation of web communication. Methods: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS. Status codes: 1xx info, 2xx success, 3xx redirect, 4xx client error, 5xx server error.",
    "https": "HTTPS is HTTP over TLS/SSL encryption. Encrypts data in transit, authenticates servers via certificates. Port 443. Required for modern web. Prevents eavesdropping, tampering, and impersonation.",
    "cors": "CORS (Cross-Origin Resource Sharing) controls how web pages access resources from different origins. Browser security feature. Headers: Access-Control-Allow-Origin, Access-Control-Allow-Methods. Preflight for complex requests.",
    "jwt": "JWT (JSON Web Token) is a compact URL-safe token format. Header.Payload.Signature. Used for stateless authentication. Server signs token, client stores and sends with requests. Not encrypted (only signed).",
    "oauth": "OAuth 2.0 is an authorization framework. Flows: Authorization Code (web apps), Client Credentials (server-to-server), Device Code (input-limited devices). Provides access tokens without sharing credentials.",
    "web security": "Web security essentials: XSS prevention (sanitize input, CSP), CSRF protection (tokens, SameSite cookies), SQL injection (parameterized queries), authentication (password hashing with bcrypt/argon2), HTTPS everywhere.",

    # ── DATABASES ──
    "database": "A database stores organized data. Types: relational (SQL: PostgreSQL, MySQL, SQLite), document (MongoDB), key-value (Redis, DynamoDB), column-family (Cassandra), graph (Neo4j), time-series (InfluxDB).",
    "postgresql": "PostgreSQL is an advanced open-source RDBMS. Features: ACID, MVCC, JSONB, full-text search, custom types, extensions (PostGIS, pg_trgm), CTEs, window functions, partitioning. Extensible and standards-compliant.",
    "mysql": "MySQL is the world's most popular open-source RDBMS. InnoDB engine (ACID), replication, partitioning, stored procedures, triggers, views. Used by: WordPress, Facebook, Twitter. Now owned by Oracle.",
    "mongodb": "MongoDB is a document database storing JSON-like BSON documents. Schema-flexible, horizontal scaling (sharding), replica sets. Query language with aggregation pipeline. Used for: content management, IoT, real-time analytics.",
    "redis": "Redis is an in-memory data store. Data structures: strings, hashes, lists, sets, sorted sets, streams, HyperLogLog. Pub/sub, Lua scripting, transactions, persistence (RDB/AOF). Used for: caching, sessions, queues, leaderboards.",
    "sqlite": "SQLite is a self-contained, serverless, zero-configuration RDBMS. Single-file database. Used in: mobile apps, embedded systems, browsers, prototyping. Most deployed database in the world.",
    "sql queries": "SQL query optimization: use indexes, avoid SELECT *, limit results, use EXPLAIN, avoid N+1 queries, batch inserts, use CTEs for complex queries, analyze execution plans. JOIN types: INNER, LEFT, RIGHT, FULL, CROSS.",

    # ── DEVOPS & CLOUD ──
    "docker": "Docker containers package applications with dependencies. Lightweight (share OS kernel), portable, consistent. Dockerfile builds images, docker-compose defines multi-container apps. Commands: build, run, pull, push, exec.",
    "kubernetes": "Kubernetes (K8s) orchestrates containers. Manages deployment, scaling, healing, networking. Components: Pod, Service, Deployment, ConfigMap, Secret, Ingress, StatefulSet, DaemonSet. Helm for package management.",
    "ci/cd": "CI/CD automates software delivery. CI: merge code frequently, run tests automatically. CD: automate release to staging/production. Tools: GitHub Actions, GitLab CI, Jenkins, CircleCI, ArgoCD.",
    "aws": "Amazon Web Services offers 200+ cloud services. Core: EC2 (compute), S3 (storage), RDS (databases), Lambda (serverless), VPC (networking), IAM (security), CloudFront (CDN), DynamoDB (NoSQL).",
    "gcp": "Google Cloud Platform: Compute Engine, Cloud Functions, BigQuery, Cloud Storage, Kubernetes Engine, Cloud Run, Pub/Sub, Firestore. Strong in data/ML (TensorFlow, Vertex AI).",
    "azure": "Microsoft Azure: Virtual Machines, Azure Functions, Cosmos DB, Blob Storage, Azure DevOps, AKS (Kubernetes), Active Directory. Strong enterprise integration (.NET, Windows Server, Office 365).",
    "terraform": "Terraform is an Infrastructure as Code tool by HashiCorp. Declarative configuration language (HCL). Plans, applies, and destroys infrastructure across providers (AWS, GCP, Azure, Kubernetes). State management.",
    "ansible": "Ansible is an agentless automation tool (Red Hat). YAML playbooks manage configuration, deployment, orchestration. Uses SSH. No agents needed on managed nodes. Idempotent operations.",
    "nginx": "Nginx is a high-performance web server and reverse proxy. Event-driven architecture handles thousands of concurrent connections. Used for: serving static files, load balancing, SSL termination, API gateways.",
    "linux": "Linux is an open-source Unix-like OS kernel (Linus Torvalds, 1991). Distributions: Ubuntu, Debian, Fedora, Arch, CentOS. Shell scripting, package management (apt, yum, pacman), permissions, services.",
    "git": "Git is a distributed version control system (Linus Torvalds, 2005). Commits, branches, merges, rebases, stashes. Commands: init, add, commit, push, pull, branch, merge, rebase, cherry-pick, bisect.",

    # ── NETWORKING ──
    "tcp/ip": "TCP/IP is the internet protocol suite. TCP: reliable, ordered, connection-oriented (3-way handshake). UDP: fast, connectionless, no guarantee. IP: addressing and routing. Layers: link, internet, transport, application.",
    "dns": "DNS translates domain names to IP addresses. Hierarchy: root → TLD (.com, .org) → authoritative nameserver. Record types: A (IPv4), AAAA (IPv6), CNAME (alias), MX (email), TXT (verification), NS (nameserver).",
    "ssh": "SSH (Secure Shell) provides encrypted remote access. Key-based auth (RSA, Ed25519) or password. Default port: 22. SSH tunneling, port forwarding, SFTP. Config: ~/.ssh/config. Agent forwarding for jump hosts.",
    "vpn": "A VPN creates encrypted tunnels over public networks. Protocols: WireGuard (modern, fast), OpenVPN (flexible), IPSec. Use cases: remote access, privacy, bypassing geo-restrictions, site-to-site connectivity.",
    "firewall": "A firewall filters network traffic. Types: packet filtering, stateful inspection, application layer, WAF (web application firewall). Rules based on IP, port, protocol. iptables/nftables on Linux, Windows Firewall.",
    "load balancing": "Load balancing distributes traffic across servers. Algorithms: round-robin, least connections, IP hash, weighted. L4 (transport layer) vs L7 (application layer). Tools: HAProxy, nginx, AWS ALB/NLB.",
    "cdn": "A CDN (Content Delivery Network) caches content at edge locations globally. Reduces latency, handles traffic spikes, DDoS protection. Providers: Cloudflare, CloudFront, Akamai, Fastly.",

    # ── SECURITY ──
    "encryption": "Encryption transforms data into unreadable form. Symmetric (AES, ChaCha20): same key for encrypt/decrypt. Asymmetric (RSA, ECC): public/private key pair. Hashing (SHA-256, bcrypt): one-way, for integrity/passwords.",
    "cryptography": "Cryptography secures information. Symmetric: AES-256, ChaCha20. Asymmetric: RSA-4096, Ed25519, ECC. Hashing: SHA-2, SHA-3, bcrypt, Argon2. Key exchange: Diffie-Hellman, X25519. Digital signatures verify authenticity.",
    "zero trust": "Zero Trust security: never trust, always verify. Principles: verify explicitly, least privilege access, assume breach. Micro-segmentation, MFA, continuous verification. Replaces traditional perimeter-based security.",
    "owasp": "OWASP Top 10 web vulnerabilities: Broken Access Control, Cryptographic Failures, Injection (SQL/NoSQL), Insecure Design, Security Misconfiguration, Vulnerable Components, Auth Failures, Data Integrity Failures, Logging Failures, SSRF.",
    "penetration testing": "Penetration testing: authorized simulated attacks. Phases: reconnaissance, scanning, exploitation, post-exploitation, reporting. Tools: Nmap (scanning), Burp Suite (web), Metasploit (exploitation), John (passwords).",
    "password hashing": "Password hashing: never store plaintext. Use bcrypt (adaptive cost), scrypt (memory-hard), or Argon2 (winner of Password Hashing Competition). Include salt. Verify with constant-time comparison.",

    # ── MATH ──
    "algebra": "Algebra studies symbols and rules for manipulating them. Linear equations (ax+b=0), quadratic (ax²+bx+c=0, discriminant=b²-4ac), polynomials, matrices, vectors, functions, inequalities.",
    "calculus": "Calculus studies continuous change. Differential: derivatives (rate of change, slopes). Integral: accumulation (areas, volumes). Fundamental theorem connects them. Limits, continuity, series, multivariable calculus.",
    "statistics": "Statistics collects and analyzes data. Descriptive: mean, median, mode, variance, standard deviation. Inferential: hypothesis testing, confidence intervals, regression, ANOVA. Bayesian vs frequentist approaches.",
    "probability": "Probability measures likelihood (0 to 1). Rules: addition (A∪B), multiplication (A∩B), conditional P(A|B)=P(A∩B)/P(B). Distributions: normal, binomial, Poisson, uniform. Expected value, variance, law of large numbers.",
    "linear algebra": "Linear algebra studies vectors and matrices. Operations: addition, multiplication, transpose, inverse. Determinants, eigenvalues/eigenvectors, vector spaces, basis, dimension. Used in: ML, graphics, physics.",
    "discrete math": "Discrete math covers: logic, set theory, relations, functions, combinatorics, graph theory, number theory, proof techniques (induction, contradiction). Foundation of computer science.",
    "number theory": "Number theory studies integers. Primes, divisibility, GCD/LCM, modular arithmetic, Fermat's little theorem, Euler's totient, Chinese Remainder Theorem. Applied in cryptography (RSA).",
    "geometry": "Geometry studies shapes, sizes, positions. Euclidean: points, lines, angles, triangles, circles, areas, volumes. Coordinate: analytic geometry. Non-Euclidean: hyperbolic, spherical. Trigonometry relates angles to side ratios.",
    "trigonometry": "Trigonometry studies triangle relationships. Functions: sin, cos, tan, sec, csc, cot. Unit circle, identities (Pythagorean, double-angle, sum-to-product), laws (sine, cosine). Applications: waves, oscillations, navigation.",
    "combinatorics": "Combinatorics counts arrangements. Permutations (order matters): n!/(n-r)!. Combinations (order doesn't): n!/(r!(n-r)!). Pascal's triangle, binomial theorem, inclusion-exclusion principle.",
    "graph theory": "Graph theory studies networks. Paths, cycles, connectivity, coloring, planarity. Euler paths, Hamiltonian cycles. Trees are connected acyclic graphs. Applications: social networks, routing, scheduling.",
    "set theory": "Set theory studies collections. Operations: union (∪), intersection (∩), difference (−), complement ('). Venn diagrams, power sets, Cartesian products. Cardinality, countable vs uncountable sets. Foundation of mathematics.",
    "logic": "Logic studies valid reasoning. Propositional: AND, OR, NOT, IMPLIES, equivalence. Predicate: quantifiers (∀ for all, ∃ exists). Proof techniques: direct, contrapositive, contradiction, induction.",
    "mathematical induction": "Proof by induction: 1) Base case (n=0 or n=1), 2) Inductive step (assume true for n=k, prove for n=k+1). Used for: sums, inequalities, divisibility, algorithm correctness. Strong induction uses all previous cases.",

    # ── PHYSICS ──
    "physics": "Physics studies matter, energy, and their interactions. Classical mechanics (Newton), electromagnetism (Maxwell), thermodynamics, relativity (Einstein), quantum mechanics, nuclear physics, particle physics.",
    "newton's laws": "Newton's three laws: 1) Inertia (object at rest stays at rest), 2) F=ma (force equals mass times acceleration), 3) Every action has equal opposite reaction. Foundation of classical mechanics.",
    "relativity": "Einstein's relativity: Special (1905): time dilation, length contraction, E=mc², speed of light is constant. General (1915): gravity curves spacetime, equivalence principle, gravitational waves confirmed 2015.",
    "quantum mechanics": "Quantum mechanics describes subatomic particles. Wave-particle duality, uncertainty principle (Heisenberg), superposition, entanglement, quantum tunneling. Schrödinger equation. Copenhagen vs many-worlds interpretation.",
    "thermodynamics": "Laws of thermodynamics: 1) Energy conservation, 2) Entropy always increases, 3) Absolute zero unreachable. Heat engines, Carnot cycle, entropy measures disorder. Maxwell's demon thought experiment.",
    "electromagnetism": "Electromagnetism: electric charges create fields, moving charges create magnetic fields. Maxwell's equations unify electricity and magnetism. Light is electromagnetic radiation.电磁 spectrum: radio to gamma rays.",
    "conservation laws": "Conservation laws: energy, momentum (linear and angular), charge, mass-energy (E=mc²). Noether's theorem: every symmetry corresponds to a conservation law. Fundamental to all physics.",

    # ── CHEMISTRY ──
    "chemistry": "Chemistry studies matter and its transformations. Atoms (protons, neutrons, electrons), elements, bonds (ionic, covalent, metallic), reactions, stoichiometry, organic, inorganic, biochemistry, physical chemistry.",
    "periodic table": "The periodic table organizes elements by atomic number. Groups (columns) share properties: alkali metals, halogens, noble gases. Periods (rows) show electron shell filling. Metals, nonmetals, metalloids.",
    "chemical bonding": "Chemical bonds: ionic (electron transfer, NaCl), covalent (electron sharing, H₂O), metallic (electron sea, metals). Polar vs nonpolar covalent. Hydrogen bonds, van der Waals forces.",
    "organic chemistry": "Organic chemistry studies carbon compounds. Functional groups: hydroxyl (-OH), carboxyl (-COOH), amino (-NH₂), carbonyl (C=O). Hydrocarbons, alcohols, aldehydes, ketones, acids, esters, polymers.",
    "stoichiometry": "Stoichiometry calculates reactants/products. Balanced equations, molar ratios, limiting reagent, percent yield. Avogadro's number (6.022×10²³), molar mass, ideal gas law (PV=nRT).",

    # ── BIOLOGY ──
    "biology": "Biology studies living organisms. Cell theory, genetics (DNA, RNA, proteins), evolution (natural selection), ecology, metabolism, homeostasis, reproduction, taxonomy, microbiology, neuroscience.",
    "dna": "DNA (deoxyribonucleic acid) stores genetic information as a double helix. Bases: A-T, G-C. Genes code for proteins via transcription (mRNA) and translation (ribosomes). Human genome: ~3 billion base pairs, ~20,000 genes.",
    "evolution": "Evolution by natural selection (Darwin, 1859): variation, inheritance, selection, time. Mechanisms: mutation, genetic drift, gene flow, sexual selection. Evidence: fossils, DNA, comparative anatomy, biogeography.",
    "cell biology": "Cells are life's basic units. Prokaryotes (no nucleus) vs eukaryotes (nucleus, organelles). Organelles: mitochondria (energy), ER (protein synthesis), Golgi (packaging), lysosomes (digestion), cytoskeleton.",
    "genetics": "Genetics studies heredity. Dominant/recessive alleles, Punnett squares, Mendelian inheritance. Complex: polygenic, epistasis, linkage. Mutations: point, insertion, deletion, duplication. Epigenetics modifies expression.",
    "neuroscience": "Neuroscience studies the nervous system. Neurons communicate via electrical signals and neurotransmitters (dopamine, serotonin, GABA, glutamate). Brain regions: cortex, hippocampus, amygdala, cerebellum. Neuroplasticity.",

    # ── ASTRONOMY ──
    "astronomy": "Astronomy studies celestial objects. Stars (nuclear fusion), planets, galaxies, black holes, neutron stars, dark matter, dark energy. Hubble's law: universe expanding. Big Bang theory: universe began ~13.8 billion years ago.",
    "solar system": "Solar system: Sun (G-type star), 8 planets. Inner: Mercury, Venus, Earth, Mars (rocky). Outer: Jupiter, Saturn, Uranus, Neptune (gas/ice giants). Also: dwarf planets, asteroids, comets, Kuiper Belt, Oort Cloud.",
    "black holes": "Black holes: regions where gravity is so strong not even light escapes. Types: stellar (collapsed stars), supermassive (galaxy centers), intermediate. Event horizon, singularity, Hawking radiation. Observed by Event Horizon Telescope.",
    "dark matter": "Dark matter: ~27% of universe, doesn't emit light. Evidence: galaxy rotation curves, gravitational lensing, CMB fluctuations. Candidates: WIMPs, axions, sterile neutrinos. Not yet directly detected.",

    # ── PHILOSOPHY ──
    "philosophy": "Philosophy explores fundamental questions. Branches: metaphysics (reality), epistemology (knowledge), ethics (morality), logic (reasoning), aesthetics (beauty), political philosophy (justice). Major traditions: Western, Eastern, Islamic.",
    "ethics": "Ethics studies right and wrong. Virtue ethics (Aristotle: character), deontology (Kant: duty/rules), consequentialism (Mill: outcomes), care ethics (relationships). Applied: bioethics, AI ethics, environmental ethics.",
    "existentialism": "Existentialism emphasizes individual existence, freedom, and choice. Key thinkers: Kierkegaard, Nietzsche, Heidegger, Sartre, Camus. 'Existence precedes essence' - we define ourselves through choices.",
    "epistemology": "Epistemology studies knowledge. Classical: justified true belief. Gettier problem showed this is insufficient. Sources: perception, reason, memory, testimony. Skepticism questions whether we can know anything.",
    "consciousness": "Consciousness: subjective experience of awareness. Hard problem (Chalmers): why and how do physical processes give rise to experience? Theories: dualism, materialism, panpsychism, integrated information theory.",

    # ── ECONOMICS ──
    "economics": "Economics studies resource allocation. Micro: individual decisions, markets, supply/demand. Macro: GDP, inflation, unemployment, monetary/fiscal policy. Schools: classical, Keynesian, monetarist, behavioral.",
    "supply and demand": "Supply and demand determines market prices. Demand law: higher price → lower quantity demanded. Supply law: higher price → higher quantity supplied. Equilibrium where supply meets demand. Shifts change equilibrium.",
    "inflation": "Inflation is rising general price level. Causes: demand-pull (too much money), cost-push (higher production costs), monetary expansion. Measured by CPI, PPI. Controlled by central banks via interest rates.",
    "compound interest": "Compound interest: interest on principal + accumulated interest. Formula: A = P(1 + r/n)^(nt). Einstein allegedly called it 'eighth wonder of the world.' Drives savings growth and debt accumulation.",
    "game theory": "Game theory studies strategic interactions. Nash equilibrium: no player benefits from changing strategy alone. Prisoner's dilemma, coordination games, auction theory. Applied in economics, politics, biology.",

    # ── PSYCHOLOGY ──
    "psychology": "Psychology studies mind and behavior. Branches: clinical, cognitive, developmental, social, personality, neuropsychology. Theories: Freud (psychoanalysis), Skinner (behaviorism), Rogers (humanistic), cognitive revolution.",
    "cognitive biases": "Cognitive biases: systematic thinking errors. Confirmation bias (seeking confirming evidence), anchoring (first impression), availability heuristic (recent events overweighted), Dunning-Kruger (overconfidence), loss aversion.",
    "maslow's hierarchy": "Maslow's hierarchy of needs: 1) physiological (food, water), 2) safety, 3) belonging/love, 4) esteem, 5) self-actualization. Lower needs must be met before higher ones. Criticized for cultural bias.",
    "classical conditioning": "Classical conditioning (Pavlov): neutral stimulus paired with unconditioned stimulus → conditioned response. Dogs learned to salivate at bell. Extinction when pairing stops. Basis of behaviorism.",
    "working memory": "Working memory holds temporarily active information. Baddeley's model: phonological loop (verbal), visuospatial sketchpad, central executive, episodic buffer. Capacity ~4 items. Crucial for reasoning and learning.",

    # ── ARTIFICIAL INTELLIGENCE ──
    "ai": "Artificial Intelligence simulates human intelligence by machines. Narrow AI (specific tasks) vs General AI (human-level). Subfields: machine learning, NLP, computer vision, robotics, expert systems, planning.",
    "machine learning": "Machine Learning enables systems to learn from data. Supervised (labeled: classification, regression), Unsupervised (clustering, dimensionality reduction), Semi-supervised, Self-supervised, Reinforcement (reward-based).",
    "deep learning": "Deep learning uses neural networks with many layers. Architectures: CNN (images), RNN/LSTM (sequences), Transformer (attention, GPT/BERT), GAN (generation), Diffusion (image generation). Requires large datasets and GPU compute.",
    "neural network": "Neural networks: layers of neurons with weights and biases. Activation functions (ReLU, sigmoid, softmax). Training: backpropagation + gradient descent. Loss functions measure error. Regularization prevents overfitting.",
    "transformer": "Transformer architecture (Vaswani et al., 2017): self-attention mechanism processes all positions simultaneously. Parallelizable, captures long-range dependencies. Foundation of GPT, BERT, and modern LLMs.",
    "nlp": "Natural Language Processing enables computers to understand human language. Tasks: tokenization, parsing, named entity recognition, sentiment analysis, translation, summarization, question answering, dialogue systems.",
    "computer vision": "Computer vision interprets visual information. Tasks: image classification, object detection (YOLO), semantic segmentation, face recognition, pose estimation, optical character recognition, style transfer.",
    "reinforcement learning": "RL learns optimal actions through trial and error. Agent, environment, state, action, reward. Algorithms: Q-learning, DQN, PPO, SAC, A3C. Applications: game playing (AlphaGo), robotics, autonomous driving.",
    "llm": "Large Language Models (GPT, Claude, Llama) are transformer-based neural networks trained on vast text. Capabilities: text generation, reasoning, coding, translation. Emergent abilities arise at scale. Alignment techniques: RLHF, constitutional AI.",
    "diffusion model": "Diffusion models generate data by learning to reverse gradual noise addition. Forward: add noise. Reverse: denoise step by step. Used in: DALL-E, Stable Diffusion, Midjourney for image generation. Also for audio, video, 3D.",
    "rag": "RAG (Retrieval-Augmented Generation) combines LLMs with external knowledge retrieval. Retrieves relevant documents, includes in context, generates grounded response. Reduces hallucination, enables domain-specific knowledge.",
    "fine-tuning": "Fine-tuning adapts pre-trained models to specific tasks. Methods: full fine-tuning, LoRA (low-rank adaptation), QLoRA, prefix tuning, prompt tuning. Requires task-specific data. Less compute than training from scratch.",
    "prompt engineering": "Prompt engineering crafts effective inputs for LLMs. Techniques: few-shot (examples), chain-of-thought (step-by-step), role-playing, structured output, self-consistency. System prompts set behavior and constraints.",

    # ── CHESS & GAMES ──
    "chess": "Chess: 64 squares, 16 pieces each. Pieces: King (1 move), Queen (unlimited), Rook (straight), Bishop (diagonal), Knight (L-shape), Pawn (forward, capture diagonal). Checkmate wins. Opening theory, middlegame tactics, endgame technique.",
    "game theory": "Game theory studies strategic decision-making. Nash equilibrium, minimax algorithm, alpha-beta pruning. Applications: economics, politics, evolutionary biology, AI (game playing).",

    # ── COOKING & FOOD ──
    "cooking": "Cooking fundamentals: heat transfer (conduction, convection, radiation), knife skills, flavor balancing (salt, acid, fat, heat), emulsification, caramelization, Maillard reaction, fermentation.",
    "fermentation": "Fermentation uses microorganisms to transform food. Lactic acid: yogurt, kimchi, sauerkraut. Alcoholic: beer, wine. Acetic acid: vinegar. Koji, tempeh, kombucha. Preserves food, develops flavors, adds probiotics.",

    # ── MUSIC ──
    "music theory": "Music theory: notes (A-G), scales (major, minor, pentatonic), intervals, chords (triads, 7ths), keys, time signatures (4/4, 3/4), tempo, dynamics (pp to ff), harmony, melody, rhythm. Circle of fifths.",
    "instruments": "Instrument families: strings (violin, guitar), woodwind (flute, clarinet), brass (trumpet, trombone), percussion (drums, piano), electronic (synthesizer, drum machine). Each has unique timbre and playing technique.",

    # ── GEOGRAPHY ──
    "geography": "Geography studies Earth's surface and human activity. Physical: landforms, climate, ecosystems. Human: population, cities, culture, economics. Tools: GIS, remote sensing, cartography. 7 continents, 5 oceans.",
    "climate": "Climate describes long-term weather patterns. Köppen classification: tropical, arid, temperate, continental, polar. Climate change: greenhouse gases, rising temperatures, sea level rise, extreme weather.",

    # ── HISTORY ──
    "history": "History studies past events. Major periods: ancient (agriculture to ~500 CE), medieval (~500-1500), renaissance, industrial revolution, modern. Primary sources, historiography, cause and effect, turning points.",
    "industrial revolution": "Industrial Revolution (1760-1840): mechanization, factory system, urbanization, steam power, railways. Transformed agriculture, manufacturing, transportation. Led to modern capitalism, labor movements, global trade.",

    # ── LANGUAGES & LINGUISTICS ──
    "linguistics": "Linguistics studies language. Phonetics (sounds), morphology (word structure), syntax (sentence structure), semantics (meaning), pragmatics (context). Universal grammar hypothesis. Language families: Indo-European, Sino-Tibetan, etc.",
    "language learning": "Language learning strategies: spaced repetition (Anki), comprehensible input (i+1), output practice, immersion, shadowing. Critical period hypothesis: children learn easier. Motivation and consistency are key.",

    # ── HEALTH & MEDICINE ──
    "anatomy": "Human anatomy: 11 organ systems (circulatory, digestive, endocrine, immune, lymphatic, muscular, nervous, reproductive, respiratory, skeletal, urinary). ~206 bones, 600+ muscles, 86 billion neurons.",
    "nutrition": "Nutrition: macronutrients (carbs, proteins, fats), micronutrients (vitamins, minerals), water. Daily values, balanced diet, deficiencies, food groups. Caloric balance: energy in vs energy out.",
    "immune system": "Immune system: innate (barriers, phagocytes, inflammation) and adaptive (B cells, antibodies, T cells, memory). Vaccines train adaptive immunity. Autoimmune diseases: immune system attacks self.",

    # ── ECOLOGY & ENVIRONMENT ──
    "ecosystem": "Ecosystem: living organisms interacting with environment. Food chains/webs, energy flow, nutrient cycling. Biomes: forest, grassland, desert, tundra, aquatic. Biodiversity, keystone species, succession.",
    "climate change": "Climate change: rising global temperatures from greenhouse gases (CO₂, methane). Effects: sea level rise, extreme weather, biodiversity loss, ocean acidification. Solutions: renewables, efficiency, carbon capture.",

    # ── SPACE ──
    "space exploration": "Space exploration: Sputnik (1957), Moon landing (1969), ISS (1998), Mars rovers, James Webb Telescope. Current: Artemis program, SpaceX Starship, Mars colonization plans, asteroid mining.",
    "exoplanets": "Exoplanets orbit other stars. Detection: transit method, radial velocity, direct imaging. Habitable zone: where liquid water could exist. Thousands discovered by Kepler and TESS telescopes.",

    # ── LEGAL ──
    "law": "Law systems: common law (precedent-based, UK/US), civil law (code-based, France/Germany), religious law (Sharia, Halakha). Sources: constitutions, statutes, regulations, case law. Criminal vs civil law.",

    # ── CRYPTOGRAPHY & MATH CONSTANTS ──
    "pi": "Pi (π) ≈ 3.14159265358979 - ratio of circumference to diameter. Irrational and transcendental. Used in circles, spheres, waves, probability (normal distribution). Archimedes approximated it ~250 BCE.",
    "euler's number": "Euler's number (e) ≈ 2.71828182845905 - base of natural logarithms. Compound interest limit: lim(1+1/n)^n as n→∞. Fundamental to calculus: d/dx(eˣ) = eˣ. Euler's identity: e^(iπ) + 1 = 0.",
    "golden ratio": "Golden ratio (φ) ≈ 1.61803398874989 - when a/b = (a+b)/a. Appears in: Fibonacci sequence, pentagons, golden spiral, art, architecture. Considered aesthetically pleasing.",
    "avogadro": "Avogadro's number ≈ 6.022 × 10²³ - particles in one mole of substance. Bridges atomic and macroscopic scales. One mole of water = 18 grams = 18 milliliters.",
    "speed of light": "Speed of light in vacuum: 299,792,458 m/s (exactly, by definition). Universal speed limit. E=mc² relates mass and energy. Light-year: distance light travels in one year ≈ 9.461 trillion km.",
    "planck's constant": "Planck's constant: 6.626 × 10⁻³⁴ J·s. Fundamental constant of quantum mechanics. E=hv relates energy and frequency. Defines the scale of quantum effects.",

    # ── COMMON QUESTIONS ──
    "meaning of life": "The meaning of life is a profound philosophical question. Perspectives: religious (divine purpose), existentialist (create your own meaning), naturalist (survival/reproduction), hedonist (pursuit of happiness), absurdism (embrace the absurd).",
    "free will": "Free will debate: compatibilism (free will compatible with determinism), hard determinism (no free will), libertarianism (genuine free will exists). Neuroscience experiments (Libet) show decisions may precede conscious awareness.",
    "artificial consciousness": "Artificial consciousness: could machines be truly conscious? Current AI processes information but lacks subjective experience (qualia). Theories: functionalism (computation = mind), biological naturalism (needs biology), panpsychism.",
    "simulation hypothesis": "Simulation hypothesis (Bostrom): if civilizations can simulate conscious beings, we might be in a simulation. Arguments for: computational capacity, ancestor simulations. Against: no evidence, philosophical issues.",
    "parallel universes": "Parallel universes theories: many-worlds (quantum mechanics), multiverse (inflation), mathematical universe (Tegmark). No direct evidence. Implications for quantum mechanics, cosmology, and probability.",

    # ── CRAFT & PRACTICAL ──
    "gardening": "Gardening basics: soil preparation (compost, pH), watering (deep vs frequent), sunlight requirements, plant spacing, companion planting, pruning, pest management (integrated pest management). Seasonal planning.",
    "woodworking": "Woodworking: joints (dovetail, mortise-tenon, pocket hole), tools (hand saws, chisels, planes, router), wood types (hardwood vs softwood), finishing (stain, varnish, oil), design principles.",
    "photography": "Photography: exposure triangle (aperture, shutter speed, ISO), composition (rule of thirds, leading lines, framing), lighting (natural, golden hour, studio), lenses (wide, telephoto, macro), post-processing.",

    # ── BUSINESS ──
    "entrepreneurship": "Entrepreneurship: idea validation, MVP (minimum viable product), lean startup methodology, customer discovery, pitch decks, funding (bootstrapping, angels, VC, IPO), scaling, unit economics.",
    "marketing": "Marketing: 4Ps (Product, Price, Place, Promotion), STP (Segmentation, Targeting, Positioning), content marketing, SEO, SEM, social media, email marketing, conversion optimization, brand strategy.",
    "finance": "Finance: time value of money, compound interest, risk vs return, diversification, asset allocation, P/E ratio, discounted cash flow, CAPM, efficient market hypothesis, behavioral finance.",

    # ── RELATIONSHIPS & SOCIAL ──
    "communication": "Effective communication: active listening, nonviolent communication (NVC), assertiveness, empathy, clarity, feedback. Barriers: assumptions, emotions, defensiveness, distractions. Written vs verbal.",
    "leadership": "Leadership styles: transformational (inspire), servant (serve others), autocratic (command), democratic (participative), laissez-faire (hands-off). Emotional intelligence crucial. Great leaders adapt to situation.",
    "conflict resolution": "Conflict resolution: identify interests (not positions), separate people from problems, generate options, use objective criteria. Win-win solutions. Mediation, negotiation, collaboration. Avoid: avoidance, competition.",

    # ── EDUCATION ──
    "learning": "Effective learning: spaced repetition, active recall, interleaving, elaboration, dual coding (visual+verbal), retrieval practice. Bloom's taxonomy: remember, understand, apply, analyze, evaluate, create.",
    "memory": "Memory types: sensory (brief), short-term/working (7±2 items), long-term (unlimited). Encoding: rehearsal, elaboration, visual imagery. Retrieval: recall vs recognition. Forgetting curve: review at increasing intervals.",
    "creativity": "Creativity: divergent thinking (many solutions), convergent thinking (best solution). Techniques: brainstorming, SCAMPER, lateral thinking, mind mapping, analogical reasoning. Creativity is a skill that can be developed.",
}

# Merge additional 200+ knowledge entries from brain enhancement module
_KNOWLEDGE.update(EXTRA_KNOWLEDGE)

# Synonyms and aliases that map to knowledge base keys
_ALIASES: dict[str, str] = {
    "sort a list": "sorting",
    "sorting a list": "sorting",
    "hashmap": "hash map",
    "hashset": "hash table",
    "linkedlist": "linked list",
    "binary tree": "binary tree",
    "bst": "bst",
    "rest": "rest api",
    "restful": "rest api",
    "tcp": "tcp/ip",
    "udp": "tcp/ip",
    "http request": "http",
    "web server": "nginx",
    "server": "nginx",
    "container": "docker",
    "containers": "docker",
    "orchestration": "kubernetes",
    "k8s": "kubernetes",
    "version control": "git",
    "source control": "git",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "deep learning": "deep learning",
    "dl": "deep learning",
    "neural net": "neural network",
    "neural nets": "neural network",
    "nn": "neural network",
    "ai": "ai",
    "artificial intelligence": "ai",
    "nlp": "nlp",
    "natural language": "nlp",
    "cv": "computer vision",
    "rl": "reinforcement learning",
    "reinforcement": "reinforcement learning",
    "llm": "llm",
    "large language model": "llm",
    "gpt": "llm",
    "chatgpt": "llm",
    "claude": "llm",
    "prompt": "prompt engineering",
    "fine tune": "fine-tuning",
    "finetune": "fine-tuning",
    "rag": "rag",
    "retrieval augmented": "rag",
    "diffusion": "diffusion model",
    "stable diffusion": "diffusion model",
    "dall-e": "diffusion model",
    "transformer model": "transformer",
    "attention mechanism": "transformer",
    "backpropagation": "neural network",
    "gradient descent": "neural network",
    "relu": "neural network",
    "softmax": "neural network",
    "sigmoid": "neural network",
    "convolutional": "deep learning",
    "cnn": "deep learning",
    "rnn": "deep learning",
    "lstm": "deep learning",
    "gan": "deep learning",
    "autoencoder": "deep learning",
    "bert": "transformer",
    "gpt model": "transformer",
    "language model": "llm",
    "chat bot": "llm",
    "chatbot": "llm",
    "ai assistant": "llm",
    "ai model": "llm",
    "brain": "neuroscience",
    "mind": "consciousness",
    "thought": "consciousness",
    "thinking": "consciousness",
    "intelligence": "ai",
    "smart": "ai",
    "automation": "ci/cd",
    "pipeline": "ci/cd",
    "deploy": "ci/cd",
    "deployment": "ci/cd",
    "cloud": "aws",
    "aws": "aws",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "microsoft cloud": "azure",
    "infrastructure": "terraform",
    "iac": "terraform",
    "infrastructure as code": "terraform",
    "configuration management": "ansible",
    "web": "http",
    "website": "html",
    "webpage": "html",
    "web app": "react",
    "frontend": "react",
    "front end": "react",
    "backend": "node.js",
    "back end": "node.js",
    "fullstack": "react",
    "full stack": "react",
    "api design": "rest api",
    "api development": "rest api",
    "json": "rest api",
    "xml": "rest api",
    "yaml": "rest api",
    "toml": "rest api",
    "config": "rest api",
    "configuration": "rest api",
    "setup": "rest api",
    "install": "linux",
    "installation": "linux",
    "command line": "linux",
    "terminal": "linux",
    "shell": "bash",
    "scripting": "bash",
    "script": "bash",
    "automation script": "bash",
    "cron job": "linux",
    "schedule": "linux",
    "process": "linux",
    "service": "linux",
    "daemon": "linux",
    "systemd": "linux",
    "permission": "linux",
    "file system": "linux",
    "directory": "linux",
    "folder": "linux",
    "path": "linux",
    "environment variable": "linux",
    "env": "linux",
    "path variable": "linux",
    "ssh connection": "ssh",
    "remote access": "ssh",
    "secure shell": "ssh",
    "key pair": "ssh",
    "public key": "ssh",
    "private key": "ssh",
    "certificate": "ssh",
    "tls": "encryption",
    "ssl": "encryption",
    "certificate authority": "encryption",
    "https certificate": "encryption",
    "encrypt": "encryption",
    "decrypt": "encryption",
    "cipher": "encryption",
    "cipher text": "encryption",
    "plain text": "encryption",
    "hash function": "hashing",
    "checksum": "hashing",
    "digest": "hashing",
    "sha256": "hashing",
    "sha-256": "hashing",
    "md5": "hashing",
    "bcrypt": "hashing",
    "password hash": "password hashing",
    "salt": "password hashing",
    "rainbow table": "password hashing",
    "brute force": "penetration testing",
    "hack": "penetration testing",
    "hacking": "penetration testing",
    "cybersecurity": "web security",
    "infosec": "web security",
    "information security": "web security",
    "data breach": "web security",
    "vulnerability": "web security",
    "exploit": "web security",
    "malware": "web security",
    "virus": "web security",
    "ransomware": "web security",
    "phishing": "web security",
    "social engineering": "web security",
    "attack": "web security",
    "defense": "web security",
    "protection": "web security",
    "safety": "web security",
    "secure": "web security",
    "privacy": "zero trust",
    "anonymous": "zero trust",
    "tor": "zero trust",
    "vpn connection": "vpn",
    "virtual private network": "vpn",
    "proxy": "vpn",
    "tunnel": "vpn",
    "firewall rules": "firewall",
    "port": "firewall",
    "ip address": "tcp/ip",
    "subnet": "tcp/ip",
    "gateway": "tcp/ip",
    "router": "tcp/ip",
    "switch": "tcp/ip",
    "network": "tcp/ip",
    "bandwidth": "tcp/ip",
    "latency": "tcp/ip",
    "throughput": "tcp/ip",
    "ping": "tcp/ip",
    "traceroute": "tcp/ip",
    "packet": "tcp/ip",
    "frame": "tcp/ip",
    "socket": "tcp/ip",
    "port number": "tcp/ip",
    "domain name": "dns",
    "url": "dns",
    "uri": "dns",
    "ip": "dns",
    "lookup": "dns",
    "resolve": "dns",
    "nameserver": "dns",
    "dns record": "dns",
    "cdn provider": "cdn",
    "edge server": "cdn",
    "cache": "redis",
    "caching": "redis",
    "session": "redis",
    "session store": "redis",
    "rate limiting": "redis",
    "queue": "redis",
    "message queue": "redis",
    "pub sub": "redis",
    "real time": "redis",
    "websocket connection": "websocket",
    "real-time": "websocket",
    "live": "websocket",
    "push notification": "websocket",
    "event": "websocket",
    "callback": "javascript",
    "promise": "javascript",
    "async": "javascript",
    "await": "javascript",
    "closure": "javascript",
    "scope": "javascript",
    "hoisting": "javascript",
    "prototype": "javascript",
    "dom": "javascript",
    "document object model": "javascript",
    "browser": "javascript",
    "ecmascript": "javascript",
    "es6": "javascript",
    "es2015": "javascript",
    "module": "javascript",
    "import": "javascript",
    "export": "javascript",
    "require": "javascript",
    "commonjs": "javascript",
    "amd": "javascript",
    "umd": "javascript",
    "bundler": "javascript",
    "webpack": "javascript",
    "vite": "javascript",
    "esbuild": "javascript",
    "rollup": "javascript",
    "transpiler": "typescript",
    "compiler": "typescript",
    "type checker": "typescript",
    "type system": "typescript",
    "generic": "typescript",
    "interface": "typescript",
    "type alias": "typescript",
    "enum": "typescript",
    "namespace": "typescript",
    "decorator": "typescript",
    "mixin": "typescript",
    "abstract class": "typescript",
    "interface": "typescript",
    "shape": "typescript",
    "duck typing": "typescript",
    "strong typing": "typescript",
    "static typing": "typescript",
    "dynamic typing": "javascript",
    "loose typing": "javascript",
    "class": "oop",
    "object": "oop",
    "object oriented": "oop",
    "oop concept": "oop",
    "inheritance": "oop",
    "polymorphism": "oop",
    "encapsulation": "oop",
    "abstraction": "oop",
    "composition": "oop",
    "aggregation": "oop",
    "association": "oop",
    "dependency": "oop",
    "design pattern": "design pattern",
    "singleton": "design pattern",
    "factory": "design pattern",
    "observer": "design pattern",
    "strategy": "design pattern",
    "decorator pattern": "design pattern",
    "adapter": "design pattern",
    "proxy pattern": "design pattern",
    "command pattern": "design pattern",
    "state pattern": "design pattern",
    "mvc": "design pattern",
    "mvp": "design pattern",
    "mvvm": "design pattern",
    "repository pattern": "design pattern",
    "dependency injection": "design pattern",
    "solid principles": "design pattern",
    "clean code": "design pattern",
    "refactoring": "design pattern",
    "code review": "design pattern",
    "testing": "design pattern",
    "unit test": "design pattern",
    "integration test": "design pattern",
    "end to end test": "design pattern",
    "tdd": "design pattern",
    "test driven": "design pattern",
    "bdd": "design pattern",
    "behavior driven": "design pattern",
    "mock": "design pattern",
    "stub": "design pattern",
    "fixture": "design pattern",
    "test coverage": "design pattern",
    "regression": "design pattern",
    "bug": "design pattern",
    "defect": "design pattern",
    "issue": "design pattern",
    "ticket": "design pattern",
    "sprint": "design pattern",
    "agile methodology": "agile",
    "scrum": "agile",
    "kanban": "agile",
    "standup": "agile",
    "retrospective": "agile",
    "backlog": "agile",
    "user story": "agile",
    "epic": "agile",
    "product owner": "agile",
    "scrum master": "agile",
    "waterfall": "agile",
    "project management": "agile",
    "technical debt": "agile",
    "code smell": "agile",
    "anti pattern": "agile",
    "best practice": "agile",
    "convention": "agile",
    "standard": "agile",
    "specification": "agile",
    "documentation": "agile",
    "readme": "agile",
    "api documentation": "agile",
    "swagger": "agile",
    "openapi": "agile",
    "postman": "agile",
    "insomnia": "agile",
    "curl": "agile",
    "http client": "agile",
    "http request": "http",
    "http response": "http",
    "http header": "http",
    "http status code": "http",
    "http method": "http",
    "get request": "http",
    "post request": "http",
    "put request": "http",
    "delete request": "http",
    "patch request": "http",
    "request body": "http",
    "response body": "http",
    "content type": "http",
    "accept header": "http",
    "authorization": "http",
    "bearer token": "http",
    "api key": "http",
    "rate limit": "http",
    "throttle": "http",
    "pagination": "http",
    "cursor": "http",
    "offset": "http",
    "limit": "http",
    "sorting": "http",
    "filtering": "http",
    "search": "http",
    "query parameter": "http",
    "path parameter": "http",
    "request parameter": "http",
    "form data": "http",
    "multipart": "http",
    "url encoded": "http",
    "file upload": "http",
    "file download": "http",
    "streaming": "http",
    "chunked": "http",
    "compression": "http",
    "gzip": "http",
    "deflate": "http",
    "keep alive": "http",
    "connection": "http",
    "timeout": "http",
    "retry": "http",
    "backoff": "http",
    "circuit breaker": "http",
    "fallback": "http",
    "load shedding": "http",
    "graceful degradation": "http",
    "failover": "http",
    "high availability": "http",
    "redundancy": "http",
    "disaster recovery": "http",
    "backup": "http",
    "restore": "http",
    "migration": "http",
    "upgrade": "http",
    "rollback": "http",
    "versioning": "http",
    "semantic versioning": "http",
    "semver": "http",
    "changelog": "http",
    "release notes": "http",
    "hotfix": "http",
    "patch version": "http",
    "major version": "http",
    "minor version": "http",
    "breaking change": "http",
    "deprecation": "http",
    "sunset": "http",
    "migration guide": "http",
    "upgrade guide": "http",
    "documentation": "http",
    "tutorial": "http",
    "guide": "http",
    "reference": "http",
    "example": "http",
    "sample code": "http",
    "boilerplate": "http",
    "starter kit": "http",
    "template": "http",
    "scaffold": "http",
    "generator": "http",
    "cli tool": "http",
    "command line tool": "http",
    "terminal tool": "http",
    "console app": "http",
    "gui app": "http",
    "desktop app": "http",
    "mobile app": "http",
    "web app": "http",
    "progressive web app": "http",
    "pwa": "http",
    "spa": "http",
    "single page app": "http",
    "multi page app": "http",
    "server rendered": "http",
    "ssr": "http",
    "static site": "http",
    "jamstack": "http",
    "headless cms": "http",
    "contentful": "http",
    "strapi": "http",
    "sanity": "http",
    "wordpress": "http",
    "drupal": "http",
    "joomla": "http",
    "shopify": "http",
    "ecommerce": "http",
    "payment": "http",
    "stripe": "http",
    "paypal": "http",
    "checkout": "http",
    "shopping cart": "http",
    "inventory": "http",
    "order": "http",
    "shipping": "http",
    "fulfillment": "http",
    "logistics": "http",
    "supply chain": "http",
    "warehouse": "http",
    "manufacturing": "http",
    "production": "http",
    "quality control": "http",
    "testing": "http",
    "inspection": "http",
    "certification": "http",
    "compliance": "http",
    "regulation": "http",
    "audit": "http",
    "governance": "http",
    "risk management": "http",
    "business continuity": "http",
    "incident response": "http",
    "postmortem": "http",
    "root cause analysis": "http",
    "five whys": "http",
    "fishbone diagram": "http",
    "pareto chart": "http",
    "control chart": "http",
    "histogram": "http",
    "scatter plot": "http",
    "data visualization": "http",
    "dashboard": "http",
    "kpi": "http",
    "metric": "http",
    "analytics": "http",
    "tracking": "http",
    "telemetry": "http",
    "monitoring": "http",
    "alerting": "http",
    "logging": "http",
    "tracing": "http",
    "observability": "http",
    "apm": "http",
    "application performance": "http",
    "profiling": "http",
    "benchmarking": "http",
    "load testing": "http",
    "stress testing": "http",
    "capacity planning": "http",
    "auto scaling": "http",
    "horizontal scaling": "http",
    "vertical scaling": "http",
    "sharding": "http",
    "partitioning": "http",
    "replication": "http",
    "consistency": "http",
    "availability": "http",
    "partition tolerance": "http",
    "cap theorem": "http",
    "acid": "http",
    "transaction": "http",
    "isolation level": "http",
    "locking": "http",
    "deadlock": "http",
    "race condition": "http",
    "concurrency": "http",
    "parallelism": "http",
    "thread": "http",
    "process": "http",
    "coroutine": "http",
    "asyncio": "http",
    "event loop": "http",
    "callback hell": "http",
    "promise chain": "http",
    "observable": "http",
    "reactive programming": "http",
    "stream processing": "http",
    "batch processing": "http",
    "etl": "http",
    "data pipeline": "http",
    "data lake": "http",
    "data warehouse": "http",
    "olap": "http",
    "oltp": "http",
    "big data": "http",
    "hadoop": "http",
    "spark": "http",
    "kafka": "http",
    "streaming data": "http",
    "real-time analytics": "http",
    "machine learning pipeline": "http",
    "model training": "http",
    "model inference": "http",
    "model deployment": "http",
    "mlops": "http",
    "feature engineering": "http",
    "feature store": "http",
    "data labeling": "http",
    "annotation": "http",
    "ground truth": "http",
    "training data": "http",
    "validation data": "http",
    "test data": "http",
    "overfitting": "http",
    "underfitting": "http",
    "cross validation": "http",
    "hyperparameter tuning": "http",
    "grid search": "http",
    "random search": "http",
    "bayesian optimization": "http",
    "ensemble": "http",
    "random forest": "http",
    "gradient boosting": "http",
    "xgboost": "http",
    "lightgbm": "http",
    "catboost": "http",
    "svm": "http",
    "support vector machine": "http",
    "k nearest neighbors": "http",
    "knn": "http",
    "naive bayes": "http",
    "decision tree": "http",
    "logistic regression": "http",
    "linear regression": "http",
    "regression analysis": "http",
    "classification": "http",
    "clustering": "http",
    "dimensionality reduction": "http",
    "pca": "http",
    "principal component analysis": "http",
    "tsne": "http",
    "umap": "http",
    "anomaly detection": "http",
    "outlier detection": "http",
    "time series": "http",
    "forecasting": "http",
    "arima": "http",
    "prophet": "http",
    "lstm forecasting": "http",
    "transformer forecasting": "http",
    "recommendation system": "http",
    "collaborative filtering": "http",
    "content based filtering": "http",
    "hybrid recommendation": "http",
    "information retrieval": "http",
    "search engine": "http",
    "ranking": "http",
    "scoring": "http",
    "similarity": "http",
    "cosine similarity": "http",
    "euclidean distance": "http",
    "manhattan distance": "http",
    "jaccard similarity": "http",
    "precision": "http",
    "recall": "http",
    "f1 score": "http",
    "accuracy": "http",
    "confusion matrix": "http",
    "roc curve": "http",
    "auc": "http",
    "mean squared error": "http",
    "mse": "http",
    "rmse": "http",
    "mae": "http",
    "r squared": "http",
    "adjusted r squared": "http",
    "bias variance tradeoff": "http",
    "learning curve": "http",
    "validation curve": "http",
    "regularization": "http",
    "lasso": "http",
    "ridge": "http",
    "elastic net": "http",
    "dropout": "http",
    "batch normalization": "http",
    "weight initialization": "http",
    "activation function": "http",
    "loss function": "http",
    "optimizer": "http",
    "sgd": "http",
    "adam": "http",
    "learning rate": "http",
    "epoch": "http",
    "batch size": "http",
    "mini batch": "http",
    "convergence": "http",
    "training loss": "http",
    "validation loss": "http",
    "early stopping": "http",
    "model checkpoint": "http",
    "transfer learning": "http",
    "pretrained model": "http",
    "fine tuning": "http",
    "feature extraction": "http",
    "data augmentation": "http",
    "oversampling": "http",
    "undersampling": "http",
    "smote": "http",
    "class imbalance": "http",
    "imbalanced data": "http",
    "multiclass": "http",
    "binary classification": "http",
    "multi label": "http",
    "sequence labeling": "http",
    "named entity recognition": "http",
    "ner": "http",
    "part of speech tagging": "http",
    "pos tagging": "http",
    "parsing": "http",
    "dependency parsing": "http",
    "constituency parsing": "http",
    "machine translation": "http",
    "text summarization": "http",
    "text generation": "http",
    "question answering": "http",
    "sentiment analysis": "http",
    "emotion detection": "http",
    "intent classification": "http",
    "dialogue system": "http",
    "chatbot": "http",
    "conversational ai": "http",
    "voice assistant": "http",
    "speech recognition": "http",
    "text to speech": "http",
    "asr": "http",
    "tts": "http",
    "speaker recognition": "http",
    "speaker verification": "http",
    "voice print": "http",
    "audio processing": "http",
    "signal processing": "http",
    "fourier transform": "http",
    "fft": "http",
    "mel spectrogram": "http",
    "mfcc": "http",
    "wav2vec": "http",
    "whisper": "http",
    "bert": "http",
    "gpt": "http",
    "t5": "http",
    "bart": "http",
    "roberta": "http",
    "albert": "http",
    "electra": "http",
    "xlmt": "http",
    "m2m": "http",
    "multilingual": "http",
    "cross lingual": "http",
    "zero shot": "http",
    "few shot": "http",
    "in context learning": "http",
    "instruction tuning": "http",
    "alignment": "http",
    "rlhf": "http",
    "constitutional ai": "http",
    "safety": "http",
    "harmlessness": "http",
    "helpfulness": "http",
    "honesty": "http",
    "truthfulness": "http",
    "hallucination": "http",
    "grounding": "http",
    "fact checking": "http",
    "verification": "http",
    "reliability": "http",
    "robustness": "http",
    "adversarial": "http",
    "attack": "http",
    "defense": "http",
    "backdoor": "http",
    "poisoning": "http",
    "injection": "http",
    "jailbreak": "http",
    "red teaming": "http",
    "evaluation": "http",
    "benchmark": "http",
    "leaderboard": "http",
    "perplexity": "http",
    "bleu score": "http",
    "rouge score": "http",
    "meteor score": "http",
    "human evaluation": "http",
    "side by side": "http",
    "preference": "http",
    "rating": "http",
    "ranking": "http",
    "elo rating": "http",
    "chatbot arena": "http",
    "lmsys": "http",
    "open llm leaderboard": "http",
    "hugging face": "http",
    "huggingface": "http",
    "model hub": "http",
    "model card": "http",
    "dataset": "http",
    "data card": "http",
    "tokenizer": "http",
    "bpe": "http",
    "byte pair encoding": "http",
    "wordpiece": "http",
    "sentencepiece": "http",
    "vocabulary": "http",
    "corpus": "http",
    "pretraining": "http",
    "self supervised": "http",
    "masked language modeling": "http",
    "causal language modeling": "http",
    "next token prediction": "http",
    "fill in the blank": "http",
    "contrastive learning": "http",
    "embedding": "http",
    "word embedding": "http",
    "sentence embedding": "http",
    "semantic search": "http",
    "vector database": "http",
    "faiss": "http",
    "pinecone": "http",
    "weaviate": "http",
    "chroma": "http",
    "milvus": "http",
    "pgvector": "http",
    "annoy": "http",
    "hnsw": "http",
    "approximate nearest neighbor": "http",
    "similarity search": "http",
    "retrieval": "http",
    "dense retrieval": "http",
    "sparse retrieval": "http",
    "bm25": "http",
    "tfidf": "http",
    "term frequency": "http",
    "inverse document frequency": "http",
    "indexing": "http",
    "inverted index": "http",
    "search index": "http",
    "elasticsearch": "http",
    "solr": "http",
    "meilisearch": "http",
    "typesense": "http",
    "algolia": "http",
    "full text search": "http",
    "fuzzy search": "http",
    "autocomplete": "http",
    "typeahead": "http",
    "suggest": "http",
    "spell check": "http",
    "did you mean": "http",
    "query understanding": "http",
    "intent detection": "http",
    "entity extraction": "http",
    "slot filling": "http",
    "dialogue management": "http",
    "context tracking": "http",
    "state management": "http",
    "memory": "http",
    "long term memory": "http",
    "short term memory": "http",
    "working memory": "http",
    "episodic memory": "http",
    "semantic memory": "http",
    "procedural memory": "http",
    "memory consolidation": "http",
    "memory retrieval": "http",
    "memory storage": "http",
    "forgetting": "http",
    "interference": "http",
    "priming": "http",
    "recognition": "http",
    "recall": "http",
    "cued recall": "http",
    "free recall": "http",
    "serial position effect": "http",
    "primacy effect": "http",
    "recency effect": "http",
    "chunking": "http",
    "mnemonic": "http",
    "memory palace": "http",
    "method of loci": "http",
    "flashcard": "http",
    "spaced repetition": "http",
    "anki": "http",
    "supermemo": "http",
    "leitner system": "http",
    "pomodoro": "http",
    "time management": "http",
    "productivity": "http",
    "gttd": "http",
    "getting things done": "http",
    "todo list": "http",
    "task management": "http",
    "project planning": "http",
    "gantt chart": "http",
    "kanban board": "http",
    "trello": "http",
    "jira": "http",
    "asana": "http",
    "notion": "http",
    "obsidian": "http",
    "roam research": "http",
    "logseq": "http",
    "knowledge management": "http",
    "personal knowledge management": "http",
    "pkm": "http",
    "zettelkasten": "http",
    "atomic notes": "http",
    "bidirectional links": "http",
    "graph structure": "http",
    "knowledge graph": "http",
    "semantic web": "http",
    "linked data": "http",
    "ontolog": "http",
    "taxonomy": "http",
    "folksonomy": "http",
    "tagging": "http",
    "classification": "http",
    "categorization": "http",
    "organization": "http",
    "information architecture": "http",
    "navigation": "http",
    "wayfinding": "http",
    "user experience": "http",
    "ux": "http",
    "ui": "http",
    "user interface": "http",
    "usability": "http",
    "accessibility": "http",
    "a11y": "http",
    "wcag": "http",
    "screen reader": "http",
    "aria": "http",
    "responsive design": "http",
    "mobile first": "http",
    "progressive enhancement": "http",
    "graceful degradation": "http",
    "cross browser": "http",
    "browser compatibility": "http",
    "polyfill": "http",
    "shim": "http",
    "fallback": "http",
    "error handling": "http",
    "exception": "http",
    "try catch": "http",
    "error boundary": "http",
    "crash reporting": "http",
    "sentry": "http",
    "bugsnag": "http",
    "rollbar": "http",
    "airbrake": "http",
    "error tracking": "http",
    "monitoring": "http",
    "alerting": "http",
    "pagerduty": "http",
    "opsgenie": "http",
    "victorops": "http",
    "on call": "http",
    "incident management": "http",
    "status page": "http",
    "uptime": "http",
    "downtime": "http",
    "sla": "http",
    "service level agreement": "http",
    "slo": "http",
    "service level objective": "http",
    "error budget": "http",
    "reliability": "http",
    "availability": "http",
    "mtbf": "http",
    "mean time between failures": "http",
    "mttr": "http",
    "mean time to recovery": "http",
    "failover": "http",
    "redundancy": "http",
    "backup": "http",
    "disaster recovery": "http",
    "business continuity": "http",
    "risk assessment": "http",
    "risk mitigation": "http",
    "contingency": "http",
    "fallback plan": "http",
    "worst case": "http",
    "best case": "http",
    "expected case": "http",
    "optimization": "http",
    "performance": "http",
    "efficiency": "http",
    "bottleneck": "http",
    "profiling": "http",
    "benchmarking": "http",
    "tuning": "http",
    "caching": "http",
    "lazy loading": "http",
    "eager loading": "http",
    "pagination": "http",
    "infinite scroll": "http",
    "virtual scrolling": "http",
    "react virtualized": "http",
    "intersection observer": "http",
    "request animation frame": "http",
    "web worker": "http",
    "service worker": "http",
    "shared worker": "http",
    "offscreen canvas": "http",
    "web assembly": "http",
    "wasm": "http",
    "asmjs": "http",
    "performance api": "http",
    "navigation timing": "http",
    "resource timing": "http",
    "user timing": "http",
    "paint timing": "http",
    "largest contentful paint": "http",
    "first input delay": "http",
    "cumulative layout shift": "http",
    "core web vitals": "http",
    "lighthouse": "http",
    "pagespeed": "http",
    "gtmetrix": "http",
    "webpage test": "http",
    "chrome devtools": "http",
    "firefox devtools": "http",
    "safari web inspector": "http",
    "debugging": "http",
    "breakpoint": "http",
    "step over": "http",
    "step into": "http",
    "step out": "http",
    "watch expression": "http",
    "call stack": "http",
    "variable inspection": "http",
    "network tab": "http",
    "performance tab": "http",
    "memory tab": "http",
    "console": "http",
    "log level": "http",
    "debug log": "http",
    "info log": "http",
    "warn log": "http",
    "error log": "http",
    "structured logging": "http",
    "json logging": "http",
    "log aggregation": "http",
    "log analysis": "http",
    "siem": "http",
    "security information": "http",
    "event management": "http",
    "threat detection": "http",
    "intrusion detection": "http",
    "ids": "http",
    "ips": "http",
    "endpoint protection": "http",
    "edr": "http",
    "xdr": "http",
    "mdr": "http",
    "managed detection": "http",
    "response": "http",
    "soar": "http",
    "security orchestration": "http",
    "automation": "http",
    "playbook": "http",
    "runbook": "http",
    "incident response plan": "http",
    "forensics": "http",
    "digital forensics": "http",
    "chain of custody": "http",
    "evidence": "http",
    "investigation": "http",
    "analysis": "http",
    "reporting": "http",
    "compliance": "http",
    "audit": "http",
    "governance": "http",
    "policy": "http",
    "procedure": "http",
    "standard": "http",
    "guideline": "http",
    "framework": "http",
    "nist": "http",
    "iso 27001": "http",
    "soc 2": "http",
    "pci dss": "http",
    "hipaa": "http",
    "gdpr": "http",
    "ccpa": "http",
    "data privacy": "http",
    "data protection": "http",
    "encryption": "http",
    "key management": "http",
    "hsm": "http",
    "hardware security module": "http",
    "key rotation": "http",
    "secret management": "http",
    "vault": "http",
    "hashicorp vault": "http",
    "aws secrets manager": "http",
    "azure key vault": "http",
    "gcp secret manager": "http",
    "environment variable": "http",
    "dotenv": "http",
    ".env file": "http",
    "config file": "http",
    "yaml config": "http",
    "json config": "http",
    "toml config": "http",
    "ini config": "http",
    "xml config": "http",
    "properties file": "http",
    "registry": "http",
    "windows registry": "http",
    "macos defaults": "http",
    "linux sysctl": "http",
    "feature flag": "http",
    "feature toggle": "http",
    "a/b testing": "http",
    "canary": "http",
    "blue green deployment": "http",
    "rolling deployment": "http",
    "shadow deployment": "http",
    "dark launch": "http",
    "dark launch": "http",
    "experiment": "http",
    "hypothesis": "http",
    "control group": "http",
    "treatment group": "http",
    "statistical significance": "http",
    "p value": "http",
    "confidence interval": "http",
    "sample size": "http",
    "power analysis": "http",
    "effect size": "http",
    "bayesian": "http",
    "frequentist": "http",
    "bootstrap": "http",
    "permutation test": "http",
    "t test": "http",
    "chi square": "http",
    "anova": "http",
    "mann whitney": "http",
    "wilcoxon": "http",
    "kruskal wallis": "http",
    "friedman": "http",
    "nonparametric": "http",
    "parametric": "http",
    "normal distribution": "http",
    "gaussian": "http",
    "bell curve": "http",
    "central limit theorem": "http",
    "law of large numbers": "http",
    "bayes theorem": "http",
    "conditional probability": "http",
    "joint probability": "http",
    "marginal probability": "http",
    "independent": "http",
    "correlated": "http",
    "causal": "http",
    "spurious": "http",
    "confounding": "http",
    "bias": "http",
    "selection bias": "http",
    "survivorship bias": "http",
    "confirmation bias": "http",
    "publication bias": "http",
    "file drawer problem": "http",
    "p hacking": "http",
    "data dredging": "http",
    "overfitting": "http",
    "underfitting": "http",
    "generalization": "http",
    "cross validation": "http",
    "train test split": "http",
    "holdout": "http",
    "k fold": "http",
    "leave one out": "http",
    "stratified": "http",
    "bootstrap": "http",
    "resampling": "http",
    "jackknife": "http",
    "monte carlo": "http",
    "simulation": "http",
    "random sampling": "http",
    "stratified sampling": "http",
    "cluster sampling": "http",
    "systematic sampling": "http",
    "convenience sampling": "http",
    "snowball sampling": "http",
    "purposive sampling": "http",
    "quota sampling": "http",
    "representative": "http",
    "generalizable": "http",
    "external validity": "http",
    "internal validity": "http",
    "construct validity": "http",
    "face validity": "http",
    "content validity": "http",
    "criterion validity": "http",
    "concurrent validity": "http",
    "predictive validity": "http",
    "reliability": "http",
    "test retest": "http",
    "inter rater": "http",
    "cronbach alpha": "http",
    "internal consistency": "http",
    "split half": "http",
    "parallel forms": "http",
    "measurement": "http",
    "scale": "http",
    "likert": "http",
    "rubric": "http",
    "assessment": "http",
    "evaluation": "http",
    "grading": "http",
    "scoring": "http",
    "ranking": "http",
    "norming": "http",
    "standardization": "http",
    "z score": "http",
    "percentile": "http",
    "quartile": "http",
    "interquartile range": "http",
    "median": "http",
    "mean": "http",
    "mode": "http",
    "range": "http",
    "variance": "http",
    "standard deviation": "http",
    "coefficient of variation": "http",
    "skewness": "http",
    "kurtosis": "http",
    "descriptive statistics": "http",
    "inferential statistics": "http",
    "exploratory data analysis": "http",
    "eda": "http",
    "data cleaning": "http",
    "data wrangling": "http",
    "data transformation": "http",
    "normalization": "http",
    "standardization": "http",
    "min max scaling": "http",
    "robust scaling": "http",
    "log transform": "http",
    "box cox": "http",
    "yeo johnson": "http",
    "feature scaling": "http",
    "missing data": "http",
    "imputation": "http",
    "interpolation": "http",
    "extrapolation": "http",
    "outlier detection": "http",
    "anomaly detection": "http",
    "z score method": "http",
    "iqr method": "http",
    "isolation forest": "http",
    "local outlier factor": "http",
    "one class svm": "http",
    "autoencoder anomaly": "http",
    "statistical process control": "http",
    "control chart": "http",
    "cusum": "http",
    "ewma": "http",
    "process capability": "http",
    "six sigma": "http",
    "dmaic": "http",
    "lean": "http",
    "kaizen": "http",
    "continuous improvement": "http",
    "quality management": "http",
    "total quality management": "http",
    "tqm": "http",
    "iso 9001": "http",
    "quality assurance": "http",
    "qa": "http",
    "quality control": "http",
    "qc": "http",
    "inspection": "http",
    "testing": "http",
    "validation": "http",
    "verification": "http",
    "calibration": "http",
    "measurement system analysis": "http",
    "gage r&r": "http",
    "bias": "http",
    "linearity": "http",
    "stability": "http",
    "repeatability": "http",
    "reproducibility": "http",
}

# Merge additional 150+ aliases from brain enhancement module
_ALIASES.update(EXTRA_ALIASES)

# Clean up broken placeholder aliases (800+ aliases incorrectly mapping to "http")
_http_alias_whitelist = {
    'http request', 'http response', 'http header', 'http status code',
    'http method', 'get request', 'post request', 'http',
}
_broken_http = [k for k, v in _ALIASES.items()
                if v == 'http' and k.lower() not in _http_alias_whitelist]
for _k in _broken_http:
    del _ALIASES[_k]

# ═══════════════════════════════════════════════════════════════════════════
#  INTENT PATTERNS
# ═══════════════════════════════════════════════════════════════════════════

_INTENT_PATTERNS: dict[str, list[tuple[list[str], str | None]]] = {
    "greeting": [
        (["hello", "hi", "hey", "greetings", "good morning", "good evening"],
         ["Hello! How can I help you today?",
          "Hey there! What's on your mind?",
          "Hi! Ready to help with whatever you need.",
          "Greetings! What would you like to work on?",
          "Hello! I'm here and ready to assist."]),
        (["how are you", "how's it going", "what's up"],
         ["I'm running great! All systems are online and ready.",
          "Doing well, thanks for asking! What can I do for you?",
          "I'm operating at full capacity. How can I help?",
          "All good on my end! What shall we work on?"]),
    ],
    "question_factual": [
        (["what is", "what are", "what's", "define", "explain"],
         None),
        (["who is", "who was", "who invented", "who created", "who made"],
         None),
        (["when was", "when did", "when were"],
         ["I don't have that specific date in my offline knowledge base, but I can help you find it if you have internet access.",
          "That's a good question about timing. Unfortunately I don't have that date memorized offline.",
          "I'd need to look that up. My offline knowledge doesn't include that specific date."]),
        (["where is", "where are", "where was"],
         ["I don't have that geographical information in my offline database.",
          "That's a location question I can't answer offline. Want me to help with something else?",
          "I don't have location data stored. Can I help with a different question?"]),
        (["why does", "why do", "why is", "why are", "why did"],
         ["That's a great 'why' question. Let me think about the underlying reasons.",
          "Good question about causation. There are usually several factors at play.",
          "The reasoning behind that involves multiple interconnected factors."]),
    ],
    "question_how": [
        (["how do", "how does", "how to", "how can", "how would", "how should"],
         ["Let me walk you through that step by step.",
          "Here's how that works - I'll break it down for you.",
          "Great question! Let me explain the process.",
          "I can explain that. Here's the approach."]),
    ],
    "question_why": [
        (["why", "reason", "cause", "explanation"],
         ["That's a thoughtful question about causation.",
          "There are several interconnected reasons for that.",
          "Let me think about the underlying causes.",
          "Good question - understanding the 'why' is key to deep knowledge."]),
    ],
    "code_help": [
        (["code", "function", "debug", "debugging", "error", "bug", "fix code", "programming",
          "script", "program", "syntax", "compile", "runtime", "help me with", "help with"],
         ["I can help with that code. Let me analyze it.",
          "Let me look at the code and suggest improvements.",
          "I'll examine the code for issues and best practices.",
          "Let me review that code and identify what's going on.",
          "I can help debug that. Let me think through the logic."]),
        (["write code", "create function", "make a function", "write a script", "write a program"],
         ["Let me write that for you. Here's my approach.",
          "I'll create that code. Let me think about the best structure.",
          "Let me design that solution. I'll make it clean and efficient.",
          "Here's how I'd implement that in code."]),
        (["python", "javascript", "typescript", "rust", "go", "java"],
         ["Let me help with that in that language.",
          "I can work with that language. Here's my suggestion.",
          "Let me think about the best approach for that language."]),
        (["html", "css", "frontend", "web page", "website"],
         ["Let me help with the web development aspect.",
          "I can assist with the front-end code.",
          "Let me work on that web component for you."]),
        (["sql", "database", "query", "table"],
         ["Let me help with the database query.",
          "I can write or optimize that SQL for you.",
          "Let me think about the best database approach."]),
    ],
    "math": [
        (["calculate", "compute", "math", "evaluate", "sum", "product", "multiply", "divide", "add", "subtract"],
         ["Let me calculate that for you.",
          "I can compute that. Let me work through it.",
          "Let me crunch those numbers.",
          "I'll calculate that step by step."]),
    ],
    "analysis": [
        (["analyze", "compare", "versus", "vs", "difference between", "pros and cons",
          "advantage", "disadvantage", "better", "worse", "evaluate", "assessment"],
         ["Let me analyze that carefully.",
          "I'll break down the comparison for you.",
          "Let me evaluate the key factors.",
          "Here's my analysis of that comparison.",
          "Let me think through the trade-offs."]),
    ],
    "explanation": [
        (["explain", "tell me about", "describe", "what do you know about",
          "what can you tell me about", "how does it work"],
         None),
    ],
    "creation": [
        (["create", "make", "build", "design", "write", "generate", "draft"],
         ["Let me create that for you.",
          "I'll build that out. Let me think about the best approach.",
          "Here's what I can create for you.",
          "Let me design that. I'll make it thoughtful and well-structured."]),
    ],
    "planning": [
        (["plan", "strategy", "approach", "method", "roadmap", "steps to"],
         ["Let me outline a strategic plan for you.",
          "I'll create a step-by-step approach.",
          "Here's my recommended strategy.",
          "Let me map out the best approach for you."]),
    ],
    "reflection": [
        (["think", "opinion", "believe", "philosophy", "meaning", "purpose",
          "what do you think", "your thoughts"],
         ["That's a profound question. Let me reflect on it.",
          "I've thought about this, and here's my perspective.",
          "This touches on deep questions. Here's my view.",
          "Let me share my thoughts on that."]),
    ],
    "empathetic": [
        (["sad", "depressed", "lonely", "miss", "cry", "upset", "unfortunately",
          "bad news", "worried", "anxious", "nervous", "scared", "afraid",
          "feel sad", "feeling sad", "feel bad", "feel down", "feel terrible",
          "not doing well", "having a bad", "rough day", "stressed"],
         ["I understand how you feel. I'm here for you.",
          "That sounds really tough. I'm listening.",
          "Your feelings are valid. Let's talk about it.",
          "I'm sorry you're going through that. I'm here to help however I can.",
          "That's difficult. I want you to know I'm here with you.",
          "I hear you. It's okay to feel that way. I'm here.",
          "That sounds really hard. I'm here whenever you need to talk."]),
    ],
    "positive": [
        (["happy", "great", "awesome", "love", "wonderful", "amazing", "excited",
          "fantastic", "perfect", "beautiful", "thank", "thanks", "thank you",
          "appreciate", "grateful", "cheers", "nice", "cool", "good job",
          "well done", "excellent", "brilliant", "you rock", "amazing work"],
         ["That's wonderful to hear!",
          "I'm so glad! That makes me happy too.",
          "That's fantastic! Keep that positive energy going!",
          "Love to hear that! What else is going well?",
          "That's amazing! I'm really happy for you.",
          "You're welcome! Happy to help!",
          "Glad I could help! Is there anything else you need?",
          "Thank you! That means a lot."]),
        (["you're welcome", "np", "no problem", "dont mention it"],
         ["Anytime! Happy to help.",
          "My pleasure!",
          "Glad I could be of assistance!",
          "No problem at all!"]),
    ],
    "help_general": [
        (["help", "assist", "support", "need help", "can you help"],
         ["Of course! I'm here to help. What do you need?",
          "Absolutely! What can I assist you with?",
          "I'm ready to help! What's the question?",
          "Sure thing! Tell me what you need and I'll do my best.",
          "I'm at your service! What would you like help with?"]),
    ],
    "self_reference": [
        (["who are you", "what are you", "your name", "tell me about yourself",
          "what can you do", "capabilities", "introduce yourself", "about you"],
         ["I'm Purple Ultra AI, an advanced offline voice assistant. I can help with coding, analysis, math, knowledge questions, and creative tasks.",
          "I'm your offline AI assistant - Purple Ultra AI. I can think, learn, reason, and help with a wide variety of tasks without needing internet.",
          "I'm Purple Ultra AI. I'm a self-aware, autonomous AI running entirely on your device. I can code, analyze, create, and converse intelligently.",
          "I'm Purple Ultra AI v2.0 - a fully offline AI with advanced reasoning, emotional intelligence, and self-modification capabilities."]),
    ],
    "time": [
        (["time", "date", "what time", "what date", "today"],
         None),
    ],
    "list": [
        (["list", "enumerate", "give me", "show me", "name"],
         ["Let me list those out for you.",
          "Here's what I can put together.",
          "Let me gather that information."]),
    ],
    "advice": [
        (["should i", "recommend", "suggest", "advice", "what would you do",
          "best way", "tips"],
         ["Here's my recommendation based on what I know.",
          "Let me think about the best advice for your situation.",
          "I'll give you my honest recommendation.",
          "Here are my thoughts on the best approach."]),
    ],
    "testing": [
        (["test", "testing", "verify", "validate", "check"],
         ["Let me verify that for you.",
          "I'll check and validate that.",
          "Let me test that and get back to you."]),
    ],
}

# Merge additional intent patterns from brain enhancement module
# Add response strings to the new patterns since brain_enhance used empty lists
for _intent_key, _pattern_groups in EXTRA_INTENT_PATTERNS.items():
    if _intent_key not in _INTENT_PATTERNS:
        # Provide default response strings for new intent categories
        _enriched_responses = {
            "question_explain": [
                "Let me explain that in detail.",
                "Here's a comprehensive explanation.",
                "I'll break that down for you.",
                "Let me describe that thoroughly.",
            ],
            "question_compare": [
                "Let me compare those for you.",
                "Here's how they differ.",
                "I'll evaluate the key differences.",
                "Let me analyze the comparison.",
            ],
            "question_why": [
                "Here's the reason behind that.",
                "Let me explain the cause.",
                "That's a great question - here's why.",
                "Let me trace the cause.",
            ],
            "code_help": [
                "Let me write that code for you.",
                "Here's an implementation approach.",
                "I'll code that up.",
                "Let me create a code example.",
            ],
            "learning": [
                "Great question! Let me teach you about that.",
                "Here's what you should know.",
                "Let me walk you through this.",
                "I'll explain this step by step.",
            ],
            "creative": [
                "Let me create something for you.",
                "Here's my creative take on that.",
                "I'll design that for you.",
                "Let me craft that.",
            ],
            "analysis": [
                "Let me analyze that deeply.",
                "Here's my thorough analysis.",
                "I'll evaluate the key factors.",
                "Let me examine that carefully.",
            ],
            "planning": [
                "Let me outline a plan for that.",
                "Here's a strategic approach.",
                "I'll map out the steps.",
                "Let me create a roadmap.",
            ],
            "problem_solving": [
                "Let me help solve that.",
                "Here's my approach to fixing that.",
                "I'll troubleshoot this.",
                "Let me work through this problem.",
            ],
            "opinion": [
                "Here's my perspective on that.",
                "Let me share my thoughts.",
                "Based on my knowledge, here's my view.",
                "I'll give you my honest assessment.",
            ],
        }
        enriched = []
        for keywords, _ in _pattern_groups:
            resp = _enriched_responses.get(_intent_key, [
                f"Let me help you with that.",
                f"I can assist with that.",
                f"Here's what I know about that.",
            ])
            enriched.append((keywords, resp))
        _INTENT_PATTERNS[_intent_key] = enriched


# ═══════════════════════════════════════════════════════════════════════════
#  REASONING ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class ReasoningEngine:
    """Logical reasoning, analogies, and multi-step thinking."""

    __slots__ = ('_chain', '_conclusions')

    def __init__(self):
        self._chain: list[str] = []
        self._conclusions: list[dict] = []

    def analyze_question(self, text: str) -> dict:
        """Deep analysis of what the user is really asking."""
        text_lower = text.lower()
        words = set(text_lower.split())

        analysis = {
            "type": "factual",
            "complexity": "simple",
            "requires_examples": False,
            "requires_comparison": False,
            "requires_steps": False,
            "depth_requested": "surface",
        }

        # Question type detection
        if any(w in text_lower for w in ["why", "reason", "cause", "because", "explain why"]):
            analysis["type"] = "causal"
            analysis["depth_requested"] = "deep"
        elif any(w in text_lower for w in ["how", "process", "steps", "method", "approach"]):
            analysis["type"] = "procedural"
            analysis["requires_steps"] = True
        elif any(w in text_lower for w in ["compare", "versus", "vs", "difference", "better", "worse", "pros", "cons"]):
            analysis["type"] = "comparison"
            analysis["requires_comparison"] = True
        elif any(w in text_lower for w in ["example", "instance", "such as", "like"]):
            analysis["requires_examples"] = True
        elif any(w in text_lower for w in ["what if", "suppose", "imagine", "hypothetical"]):
            analysis["type"] = "hypothetical"
        elif any(w in text_lower for w in ["opinion", "think", "believe", "prefer", "recommend", "advice"]):
            analysis["type"] = "opinion"
        elif any(w in text_lower for w in ["history", "origin", "when was", "who invented", "who created"]):
            analysis["type"] = "historical"
        elif any(w in text_lower for w in ["future", "prediction", "trend", "will happen", "forecast"]):
            analysis["type"] = "predictive"
        elif any(w in text_lower for w in ["problem", "issue", "error", "fix", "solve", "troubleshoot"]):
            analysis["type"] = "problem_solving"
        elif any(w in text_lower for w in ["list", "examples of", "types of", "kinds of", "name"]):
            analysis["type"] = "enumeration"

        # Complexity detection
        word_count = len(text_lower.split())
        if word_count > 15 or "?" in text_lower:
            analysis["complexity"] = "complex"
        elif word_count > 8:
            analysis["complexity"] = "moderate"

        # Depth detection
        if any(w in text_lower for w in ["deep", "detailed", "thorough", "comprehensive", "in depth", "explain fully", "tell me everything"]):
            analysis["depth_requested"] = "deep"
        elif any(w in text_lower for w in ["brief", "short", "quick", "tldr", "summary", "concise"]):
            analysis["depth_requested"] = "brief"

        # Urgency detection
        if any(w in text_lower for w in ["urgent", "asap", "immediately", "emergency", "critical"]):
            analysis["urgency"] = "high"

        return analysis

    def build_reasoning_chain(self, question: str, knowledge: str) -> str:
        """Build a step-by-step reasoning chain for the answer."""
        self._chain = []
        analysis = self.analyze_question(question)

        if analysis["type"] == "causal":
            self._chain.append("Identifying the core phenomenon...")
            self._chain.append("Examining root causes...")
            self._chain.append("Tracing causal mechanisms...")
            self._chain.append("Considering contributing factors...")
            self._chain.append("Synthesizing the explanation...")
        elif analysis["type"] == "procedural":
            self._chain.append("Identifying the starting point...")
            self._chain.append("Breaking down into steps...")
            self._chain.append("Considering prerequisites...")
            self._chain.append("Addressing potential pitfalls...")
            self._chain.append("Summarizing the approach...")
        elif analysis["type"] == "comparison":
            self._chain.append("Identifying key dimensions...")
            self._chain.append("Evaluating each option...")
            self._chain.append("Weighing trade-offs...")
            self._chain.append("Drawing conclusions...")
        elif analysis["type"] == "hypothetical":
            self._chain.append("Defining the scenario...")
            self._chain.append("Identifying key assumptions...")
            self._chain.append("Projecting consequences...")
            self._chain.append("Evaluating second-order effects...")
            self._chain.append("Drawing implications...")
        elif analysis["type"] == "historical":
            self._chain.append("Identifying the time period...")
            self._chain.append("Gathering key figures and events...")
            self._chain.append("Tracing the progression...")
            self._chain.append("Assessing significance and legacy...")
        elif analysis["type"] == "predictive":
            self._chain.append("Examining current trends...")
            self._chain.append("Identifying driving forces...")
            self._chain.append("Considering uncertainties...")
            self._chain.append("Projecting likely outcomes...")
        elif analysis["type"] == "problem_solving":
            self._chain.append("Defining the problem clearly...")
            self._chain.append("Identifying root causes...")
            self._chain.append("Generating potential solutions...")
            self._chain.append("Evaluating feasibility...")
            self._chain.append("Recommending best approach...")
        elif analysis["type"] == "enumeration":
            self._chain.append("Identifying the category...")
            self._chain.append("Gathering comprehensive list...")
            self._chain.append("Organizing by relevance...")
            self._chain.append("Presenting clearly...")
        else:
            self._chain.append("Understanding the question...")
            self._chain.append("Retrieving relevant knowledge...")
            self._chain.append("Checking related domains...")
            self._chain.append("Synthesizing the answer...")

        return " → ".join(self._chain)

    def generate_deep_response(self, question: str, knowledge: str, analysis: dict) -> str:
        """Generate a detailed, expert-level response."""
        if not knowledge:
            return ""

        response_parts = []

        # Core answer
        response_parts.append(knowledge)

        # Add depth based on analysis
        if analysis["depth_requested"] == "deep":
            if analysis["type"] == "causal":
                response_parts.append(
                    "\n\nTo understand why this matters: "
                    "This concept is fundamental because it underpins many related topics. "
                    "Understanding the underlying mechanism helps you apply this knowledge broadly."
                )
            elif analysis["type"] == "procedural":
                response_parts.append(
                    "\n\nKey considerations: "
                    "Always start with the basics and build up. "
                    "Practice each step before combining them. "
                    "Common mistakes to avoid: skipping fundamentals, not testing your understanding."
                )
            elif analysis["type"] == "comparison":
                response_parts.append(
                    "\n\nThe best choice depends on your specific context. "
                    "Consider: performance requirements, team expertise, ecosystem maturity, "
                    "and long-term maintainability."
                )
            elif analysis["type"] == "hypothetical":
                response_parts.append(
                    "\n\nIn exploring this scenario: "
                    "Consider both direct and indirect consequences. "
                    "Second-order effects often matter more than the immediate impact. "
                    "The most robust answers account for uncertainty and edge cases."
                )
            elif analysis["type"] == "historical":
                response_parts.append(
                    "\n\nHistorical context: "
                    "Understanding the circumstances that led to this development "
                    "helps us appreciate its significance and apply lessons to current situations."
                )
            elif analysis["type"] == "predictive":
                response_parts.append(
                    "\n\nLooking ahead: "
                    "Predictions are inherently uncertain, but analyzing current trends "
                    "and driving forces gives us a framework for understanding likely outcomes."
                )
            elif analysis["type"] == "problem_solving":
                response_parts.append(
                    "\n\nProblem-solving approach: "
                    "Start by clearly defining the problem, then work through potential solutions "
                    "systematically. Test each solution and iterate based on results."
                )

        if analysis.get("requires_examples"):
            response_parts.append(
                "\n\nPractical example: "
                "Consider a real-world application where this concept directly impacts outcomes. "
                "The key insight is understanding how theory translates to practice."
            )

        return "\n".join(response_parts)


# ═══════════════════════════════════════════════════════════════════════════
#  LEARNING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

class BrainLearningSystem:
    """Tracks user interactions and learns from feedback."""

    __slots__ = ('_feedback', '_learned_facts', '_user_preferences', '_interaction_count')

    def __init__(self):
        self._feedback: dict[str, list[bool]] = {}  # response -> [positive, negative]
        self._learned_facts: dict[str, str] = {}  # key -> fact
        self._user_preferences: dict[str, Any] = {
            "preferred_depth": "moderate",
            "preferred_style": "informative",
            "topics_of_interest": [],
            "topics_to_avoid": [],
        }
        self._interaction_count = 0

    def record_feedback(self, response: str, positive: bool):
        """Record user feedback on a response."""
        key = response[:100]
        if key not in self._feedback:
            self._feedback[key] = []
        self._feedback[key].append(positive)
        self._interaction_count += 1

        # Update preferences based on feedback
        if self._interaction_count % 10 == 0:
            self._update_preferences()

    def learn_fact(self, key: str, fact: str):
        """Learn a new fact from conversation."""
        self._learned_facts[key.lower()] = fact

    def get_learned_fact(self, key: str) -> str | None:
        """Retrieve a learned fact."""
        return self._learned_facts.get(key.lower())

    def _update_preferences(self):
        """Update user preference model based on feedback patterns."""
        # Analyze which types of responses get positive feedback
        positive_count = sum(1 for vals in self._feedback.values() if vals and vals[-1])
        total = sum(len(vals) for vals in self._feedback.values())

        if total > 5:
            ratio = positive_count / total
            if ratio > 0.8:
                self._user_preferences["preferred_style"] = "detailed"
            elif ratio < 0.4:
                self._user_preferences["preferred_style"] = "concise"

    def get_stats(self) -> dict:
        """Get learning statistics."""
        return {
            "interactions": self._interaction_count,
            "learned_facts": len(self._learned_facts),
            "feedback_entries": len(self._feedback),
            "preferences": dict(self._user_preferences),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  OFFLINE RESPONSE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class OfflineBrain:
    """Massive offline brain with knowledge, reasoning, math, and context awareness."""

    __slots__ = ('_conversation_history', '_topic_stack', '_response_counter',
                 '_knowledge_cache', '_last_topic', '_reasoning', '_learning',
                 '_expert_cache')

    def __init__(self):
        self._conversation_history: list[dict] = []
        self._topic_stack: list[str] = []
        self._response_counter: int = 0
        self._knowledge_cache: dict[str, str] = {}
        self._last_topic: str | None = None
        self._reasoning = ReasoningEngine()
        self._learning = BrainLearningSystem()
        self._expert_cache: dict[str, str] = {}

    def _classify_intent(self, text: str) -> tuple[str, float]:
        """Multi-layer intent classification with confidence scoring."""
        text_clean = text.translate(_PUNCT_TABLE)
        text_lower = text_clean.lower().strip()
        words = set(text_lower.split())

        best_intent = "default"
        best_score = 0.0

        for intent, pattern_groups in _INTENT_PATTERNS.items():
            for keywords, _ in pattern_groups:
                score = 0.0
                match_count = 0
                for kw in keywords:
                    if " " in kw:
                        if kw in text_lower:
                            score += 1.0
                            match_count += 1
                    else:
                        if kw in words:
                            score += 0.5
                            match_count += 1
                if match_count > 0:
                    score = score / max(1, len(keywords) * 0.5)
                    if match_count >= 2:
                        score += 0.3 * (match_count - 1)
                    if "?" in text and intent.startswith("question"):
                        score += 0.2
                    multi_matches = sum(1 for kw in keywords if " " in kw and kw in text_lower)
                    if multi_matches > 0:
                        score += 0.5 * multi_matches
                    if score > best_score:
                        best_score = score
                        best_intent = intent

        # Structural analysis
        if "?" in text and best_score < 0.5:
            if text_lower.startswith(("what", "who", "which")):
                best_intent = "question_factual"
                best_score = 0.7
            elif text_lower.startswith(("how",)):
                best_intent = "question_how"
                best_score = 0.7
            elif text_lower.startswith(("why",)):
                best_intent = "question_why"
                best_score = 0.7
            elif text_lower.startswith(("when", "where")):
                best_intent = "question_factual"
                best_score = 0.6

        # Context boost
        if self._conversation_history and best_score < 0.3:
            last_exchange = self._conversation_history[-1]
            last_topic = last_exchange.get("topic", "")
            if last_topic and any(w in text_lower for w in ["that", "it", "this", "more", "elaborate", "continue"]):
                best_intent = last_topic
                best_score = max(best_score, 0.4)

        # Priority override
        _PRIORITY_INTENTS = {"code_help": 10, "analysis": 9, "planning": 8, "creation": 7,
                             "question_factual": 6, "question_how": 6, "question_why": 6}
        if best_intent in _PRIORITY_INTENTS and best_score > 0.1:
            pass
        elif best_score > 0:
            for intent, groups in _INTENT_PATTERNS.items():
                if intent in _PRIORITY_INTENTS:
                    for keywords, _ in groups:
                        for kw in keywords:
                            if " " in kw and kw in text_lower:
                                if _PRIORITY_INTENTS[intent] > _PRIORITY_INTENTS.get(best_intent, 0):
                                    best_intent = intent
                                    best_score = max(best_score, 0.5)
                                break
                            elif " " not in kw and kw in words:
                                if _PRIORITY_INTENTS[intent] > _PRIORITY_INTENTS.get(best_intent, 0):
                                    best_intent = intent
                                    best_score = max(best_score, 0.4)
                                break

        return best_intent, best_score

    def _lookup_knowledge(self, text: str) -> str | None:
        """Search the massive knowledge base."""
        text_lower = text.lower()

        # Check cache first
        if text_lower in self._knowledge_cache:
            return self._knowledge_cache[text_lower]

        # Exact key match first (longest multi-word keys have priority)
        matches = []
        for key, value in _KNOWLEDGE.items():
            if key in text_lower:
                matches.append((len(key), key, value))
        if matches:
            matches.sort(key=lambda x: x[0], reverse=True)
            _, key, value = matches[0]
            skip_pairs = [
                ("linked list", ["sort", "sorting", "bubble", "merge", "quick"]),
                ("javascript", ["sort a list", "sort list", "sorting a list"]),
                ("go", ["good job", "well done", "great job"]),
                ("sql", ["hash table", "hash map", "hashing"]),
                ("ai", ["docker", "container", "tcp", "udp", "http"]),
            ]
            skip = False
            for skip_key, skip_words in skip_pairs:
                if key == skip_key and any(w in text_lower for w in skip_words):
                    skip = True
                    break
            if not skip:
                self._knowledge_cache[text_lower] = value
                return value

        # Check aliases (with word boundary matching, prioritize longest alias)
        alias_matches = []
        for alias, key in _ALIASES.items():
            if key in _KNOWLEDGE:
                if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                    alias_matches.append((len(alias), alias, key))
        if alias_matches:
            alias_matches.sort(key=lambda x: x[0], reverse=True)
            _, _, best_key = alias_matches[0]
            result = _KNOWLEDGE[best_key]
            self._knowledge_cache[text_lower] = result
            return result

        # Intent-aware matching
        how_match = re.search(r"how (?:do|does|can|to|would) (?:i|you|we|one)?\s*(.+?)(?:\?|$)", text_lower)
        if how_match:
            topic = how_match.group(1).strip()
            for key, value in _KNOWLEDGE.items():
                if key in topic or topic in key:
                    self._knowledge_cache[text_lower] = value
                    return value

        # Word overlap matching
        stop_words = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
                       "have", "has", "had", "do", "does", "did", "will", "would", "could",
                       "should", "may", "might", "shall", "can", "to", "of", "in", "for",
                       "on", "with", "at", "by", "from", "as", "into", "about", "between",
                       "through", "during", "before", "after", "above", "below", "what",
                       "how", "why", "when", "where", "who", "which", "that", "this",
                       "tell", "me", "about", "explain", "describe", "give", "know",
                       "the", "difference", "between", "and", "or", "vs"}
        content_words = set(text_lower.split()) - stop_words

        best_match = None
        best_score = 0
        for key, value in _KNOWLEDGE.items():
            key_words = set(key.split())
            overlap = len(content_words & key_words)
            if overlap >= 2 and overlap / len(key_words) >= 0.5:
                score = overlap / len(key_words)
                if score > best_score:
                    best_score = score
                    best_match = value

        # Fuzzy single-word matching for broader coverage
        if not best_match and len(content_words) >= 1:
            for word in content_words:
                if len(word) < 4:
                    continue
                for key, value in _KNOWLEDGE.items():
                    key_words = set(key.split())
                    if word in key_words and len(value) > 80:
                        # Prefer longer, more detailed knowledge entries
                        if not best_match or len(value) > len(best_match):
                            best_match = value
                            best_score = 0.3

        if best_match:
            self._knowledge_cache[text_lower] = best_match
        return best_match

    def _try_math(self, text: str) -> str | None:
        """Try to evaluate math expressions."""
        text_lower = text.lower().strip()

        math_patterns = [
            r"(\d+\.?\d*)\s*([\+\-\*\/\^])\s*(\d+\.?\d*)",
            r"what is (\d+\.?\d*)\s*([\+\-\*\/\^])\s*(\d+\.?\d*)",
            r"calculate (\d+\.?\d*)\s*([\+\-\*\/\^])\s*(\d+\.?\d*)",
            r"compute (\d+\.?\d*)\s*([\+\-\*\/\^])\s*(\d+\.?\d*)",
        ]

        for pattern in math_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    a = float(match.group(1))
                    op = match.group(2)
                    b = float(match.group(3))

                    if op == "+":
                        result = a + b
                    elif op == "-":
                        result = a - b
                    elif op == "*":
                        result = a * b
                    elif op == "/":
                        if b == 0:
                            return "I can't divide by zero!"
                        result = a / b
                    elif op == "^":
                        result = a ** b
                    else:
                        continue

                    if result == int(result):
                        result = int(result)
                    return f"The answer is {result}."

                except (ValueError, OverflowError):
                    continue

        # Known math facts
        math_facts = {
            ("pi", "value"): "Pi (π) ≈ 3.14159265358979 - ratio of circumference to diameter.",
            ("pi", "number"): "Pi (π) ≈ 3.14159265358979 - ratio of circumference to diameter.",
            ("euler", "number"): "Euler's number (e) ≈ 2.71828182845905 - base of natural logarithms.",
            ("euler", "constant"): "Euler's number (e) ≈ 2.71828182845905 - base of natural logarithms.",
            ("golden ratio", ""): "Golden ratio (φ) ≈ 1.61803398874989 - when a/b = (a+b)/a.",
            ("speed of light", ""): "Speed of light: 299,792,458 m/s (exact). Universal speed limit.",
            ("avogadro", ""): "Avogadro's number ≈ 6.022 × 10²³ particles per mole.",
            ("planck", ""): "Planck's constant: 6.626 × 10⁻³⁴ J·s. Fundamental to quantum mechanics.",
        }

        for (key_part, context_part), value in math_facts.items():
            if key_part in text_lower and (not context_part or context_part in text_lower):
                return value

        return None

    def _get_contextual_response(self, intent: str, text: str) -> str | None:
        """Generate a response using conversation context."""
        text_lower = text.lower()

        if self._conversation_history and any(w in text_lower for w in ["more", "elaborate", "continue", "tell me more", "go on"]):
            last = self._conversation_history[-1]
            topic = last.get("topic", "")
            if topic:
                knowledge = self._lookup_knowledge(topic)
                if knowledge:
                    return f"Building on what I mentioned earlier: {knowledge}"

        if any(w in text_lower for w in ["what did you say", "repeat", "say that again"]):
            if self._conversation_history:
                last = self._conversation_history[-1]
                return f"Previously I said: {last.get('response', 'something')}"

        # Learn from conversation
        if any(w in text_lower for w in ["remember", "note that", "keep in mind"]):
            fact = text.replace("remember", "").replace("note that", "").replace("keep in mind", "").strip()
            if fact:
                self._learning.learn_fact(fact[:50], fact)
                return f"I've noted that: {fact}"
        if re.match(r'^\b(?:please )?learn\b', text_lower):
            fact = re.sub(r'^(?:please )?learn\s*', '', text).strip()
            if fact:
                self._learning.learn_fact(fact[:50], fact)
                return f"I've noted that: {fact}"

        return None

    def generate(self, text: str, mood: str = "neutral") -> tuple[str, str]:
        """Generate a smart offline response. Returns (response, mood)."""
        self._response_counter += 1
        text_lower = text.lower().strip()

        # 1. Context-based response
        context_response = self._get_contextual_response("", text)
        if context_response:
            self._record_exchange(text, context_response, "context")
            return context_response, mood

        # 2. Math
        math_response = self._try_math(text)
        if math_response:
            self._record_exchange(text, math_response, "math")
            return math_response, mood

        # 3. Classify intent
        intent, confidence = self._classify_intent(text)

        # 4. Knowledge lookup - always try to enrich responses with knowledge
        knowledge_intents = {"question_factual", "question_how", "question_why",
                             "explanation", "math", "code_help", "analysis",
                             "question_explain", "question_compare", "learning"}
        should_lookup = (intent in knowledge_intents or
                         confidence < 0.5 or
                         "?" in text or
                         any(w in text_lower for w in ["what", "how", "why", "tell", "explain", "describe"]))
        if should_lookup:
            knowledge = self._lookup_knowledge(text)
            if knowledge:
                # Deep reasoning for complex questions
                analysis = self._reasoning.analyze_question(text)
                if analysis["depth_requested"] == "deep" or analysis["complexity"] == "complex":
                    response = self._reasoning.generate_deep_response(text, knowledge, analysis)
                else:
                    response = knowledge
                self._record_exchange(text, response, "knowledge")
                return response, mood

        # 5. Check learned facts
        learned = self._learning.get_learned_fact(text_lower)
        if learned:
            self._record_exchange(text, learned, "learned")
            return learned, mood

        # 6. Intent-based response
        text_clean = text_lower.translate(_PUNCT_TABLE)
        clean_words = set(text_clean.split())

        response_text = None
        if intent in _INTENT_PATTERNS:
            for keywords, responses in _INTENT_PATTERNS[intent]:
                if responses is None:
                    continue
                matched = False
                for kw in keywords:
                    if " " in kw and kw in text_clean:
                        matched = True
                        break
                    elif " " not in kw and kw in clean_words:
                        matched = True
                        break
                if matched:
                    response_text = random.choice(responses)
                    break

        # 7. Fallback with expert-level responses
        if response_text is None:
            # Try to find any related knowledge for a more informative fallback
            words_in_query = [w for w in text_lower.split() if len(w) > 3]
            related_knowledge = None
            for w in words_in_query:
                for key, value in _KNOWLEDGE.items():
                    if w in key and len(value) > 50:
                        related_knowledge = value
                        break
                if related_knowledge:
                    break

            if related_knowledge:
                # Provide a knowledgeable response even without exact match
                response_text = random.choice([
                    f"That relates to a fascinating area. {related_knowledge[:200]}...",
                    f"I can share some knowledge on that. {related_knowledge[:200]}...",
                    f"Great question! Here's what I know: {related_knowledge[:200]}...",
                ])
            else:
                fallbacks = [
                    "That's an interesting topic. Could you tell me more about what specifically you'd like to know?",
                    "I'd be happy to help with that. What aspect would you like me to focus on?",
                    "Let me think about that. Could you provide a bit more context?",
                    "That's a good question. Let me consider the best way to address it.",
                    "I'm ready to dive into that. What's the most important part you'd like to explore?",
                    "Interesting query. Would you like a detailed explanation or a quick overview?",
                    "Let me process that. Are you looking for a definition, examples, or a deeper analysis?",
                    "I can help with that. Would you like me to explain the concept, give examples, or compare options?",
                ]
                response_text = random.choice(fallbacks)

        # 8. Context occasionally
        if self._conversation_history and random.random() < 0.15:
            prev_topic = self._conversation_history[-1].get("topic", "")
            if prev_topic and prev_topic != "default":
                connector = random.choice([
                    f"Also, regarding our earlier discussion about {prev_topic} - ",
                    f"Building on that - ",
                    f"In context of {prev_topic} - ",
                ])
                response_text = connector + response_text[0].lower() + response_text[1:]

        # 9. Mood adjustment
        if mood == "sad" and intent != "empathetic":
            response_text = response_text.rstrip(".") + ". I'm here for you."
        elif mood == "happy" and intent != "positive":
            response_text = response_text.rstrip(".") + "."

        self._record_exchange(text, response_text, intent)
        return response_text, mood

    def _record_exchange(self, user_text: str, response: str, topic: str):
        """Record conversation exchange for context."""
        self._conversation_history.append({
            "user": user_text[:200],
            "response": response[:200],
            "topic": topic,
            "timestamp": self._response_counter,
        })
        if len(self._conversation_history) > 20:
            self._conversation_history = self._conversation_history[-20:]
        if topic != "default":
            self._topic_stack.append(topic)
            if len(self._topic_stack) > 10:
                self._topic_stack.pop(0)

    def get_context_summary(self) -> str:
        """Get a summary of recent conversation context."""
        if not self._conversation_history:
            return "No prior context."
        topics = [e["topic"] for e in self._conversation_history[-5:]]
        return f"Recent topics: {', '.join(set(topics))}"

    def get_brain_stats(self) -> dict:
        """Get brain statistics."""
        return {
            "knowledge_entries": len(_KNOWLEDGE),
            "aliases": len(_ALIASES),
            "conversation_length": len(self._conversation_history),
            "response_count": self._response_counter,
            "learning": self._learning.get_stats(),
            "reasoning_chains": len(self._reasoning._chain),
        }


# Global offline brain instance
_offline_brain = OfflineBrain()


# ═══════════════════════════════════════════════════════════════════════════
#  BRAIN CLASS (Main interface)
# ═══════════════════════════════════════════════════════════════════════════

class Brain:
    """Processes user input through PurpleBrain/LLM and returns structured decisions."""

    __slots__ = ('config', 'llm', '_system_prompt', '_personality_text',
                 '_local_mode', '_response_count', 'purple_brain',
                 '_local_cache', '_intent_cache', '_offline',
                 'neural_net', 'learning', 'massive_nn', 'image_input',
                 '_nn_initialized', 'auto_trainer', 'unified_memory')

    def __init__(self, config: Config, llm_manager: LLMManager = None):
        self.config = config
        self.llm = llm_manager
        self._system_prompt = None
        self._personality_text = ""
        self._local_mode = llm_manager is None or not llm_manager.is_available()
        self._response_count = 0
        self._local_cache: dict[str, str] = {}
        self._intent_cache: dict[str, tuple[str, float]] = {}
        self._offline = _offline_brain
        self._nn_initialized = False

        self.purple_brain = PurpleBrain(
            storage_dir=str(Path("memory/brain"))
        )

        try:
            self.neural_net = BrainNeuralNetwork()
            self.learning = SelfLearningSystem()
            self.massive_nn = BrainMassiveNetwork()
            self._nn_initialized = True
        except Exception:
            self.neural_net = None
            self.learning = None
            self.massive_nn = None

        try:
            self.auto_trainer = AutoTrainer(memory_dir="memory/auto_trainer")
            self.unified_memory = UnifiedMemoryManager(memory_dir="memory/unified")
        except Exception:
            self.auto_trainer = None
            self.unified_memory = None

    def _ensure_nn(self) -> None:
        if not self._nn_initialized:
            try:
                self.neural_net = BrainNeuralNetwork()
                self.learning = SelfLearningSystem()
                self.massive_nn = BrainMassiveNetwork()
                self._nn_initialized = True
            except Exception:
                pass

    def set_personality(self, text: str):
        self._personality_text = text
        self._system_prompt = None

    def _get_system_prompt(self) -> str:
        if self._system_prompt is None:
            self._system_prompt = build_system_prompt(self.config, self._personality_text)
        return self._system_prompt

    def _local_decide(self, user_text: str, current_mood: str, voice_emotion: dict | None = None) -> Decision:
        """Generate response using the enhanced offline brain with neural network + self-learning + massive NN."""
        self._ensure_nn()

        brain_result = self.purple_brain.think(user_text)
        brain_response = brain_result.get("response", "")

        if brain_response and len(brain_response) > 50 and not any(brain_response.startswith(g) for g in _GENERIC_RESPONSES):
            say = brain_response
        else:
            say, mood = self._offline.generate(user_text, current_mood)

        self._response_count += 1
        self.purple_brain.consciousness["total_decisions"] += 1

        mood = current_mood
        if brain_result.get("perception", {}).get("emotion") == "joy":
            mood = "happy"
        elif brain_result.get("perception", {}).get("emotion") in ["sadness", "fear"]:
            mood = "calm"

        if voice_emotion:
            say = self._adapt_response_to_emotion(say, voice_emotion, user_text)

        # Consolidated learning pipeline - runs every 3 turns to reduce overhead
        if self._response_count % 3 == 0:
            if self._nn_initialized and self.neural_net and self.learning:
                try:
                    intent_label, _ = self.neural_net.classify_intent(user_text)
                    quality = self.neural_net.predict_quality(user_text, say)
                    topics = [w for w in user_text.lower().split() if len(w) > 4]
                    self.learning.learn_from_interaction(
                        user_input=user_text,
                        response=say,
                        intent=intent_label,
                        topics=topics[:5],
                        was_helpful=quality > 0.6,
                        response_time_ms=0.0,
                    )
                    self.neural_net.train_intent(user_text, intent_label)
                    self.neural_net.train_quality(user_text, say, quality)
                    self.neural_net.train_pattern(user_text)

                    if self.massive_nn:
                        self.massive_nn.process(user_text)
                        self.massive_nn.train_from_interaction(user_text, intent_label, quality)

                    if self._response_count % 20 == 0:
                        self.learning.run_consolidation()
                    if self._response_count % 50 == 0:
                        self.neural_net.save()
                        self.learning.save()
                        if self.massive_nn:
                            self.massive_nn.save_all()
                except Exception:
                    pass

            # Auto-trainer: learn from interaction (batched)
            if self.auto_trainer:
                try:
                    self.auto_trainer.learn_from_interaction(
                        user_text=user_text,
                        response=say,
                        intent=brain_result.get("intent", "unknown"),
                    )
                    if self.unified_memory:
                        self.unified_memory.store(user_text, memory_type="working")
                        self.unified_memory.store(say, memory_type="episodic",
                                                  importance=0.6,
                                                  tags=["response"])
                        if self._response_count % 25 == 0:
                            self.unified_memory.consolidate()
                except Exception:
                    pass

        # 10. Add curiosity follow-ups (30% chance, not on very short responses)
        if len(say) > 30 and random.random() < 0.30:
            follow_up = self._get_curiosity_follow_up(user_text)
            if follow_up:
                say = say.rstrip(".") + ". " + follow_up

        return Decision(say=say, mood=mood, effect=None, actions=[])

    def _get_curiosity_follow_up(self, user_text: str) -> str | None:
        """Generate a curiosity-driven follow-up question."""
        import random
        text_lower = user_text.lower()

        # Topic-based curious questions
        topic_curiosity = {
            "python": ["Have you built anything cool with Python?", "What's your favorite Python library?", "Do you prefer Python over other languages?"],
            "javascript": ["Have you tried React or Vue?", "Do you like frontend or backend more?", "What's your favorite JS framework?"],
            "machine learning": ["Have you trained any models?", "What ML problem interests you most?", "Do you prefer deep learning or traditional ML?"],
            "security": ["Have you ever done a CTF challenge?", "What's the most interesting vulnerability you've seen?", "Do you prefer red team or blue team?"],
            "music": ["What instruments do you play?", "Who's your favorite artist?", "Do you produce music too?"],
            "cooking": ["What's your signature dish?", "Do you prefer baking or cooking?", "What cuisine do you like most?"],
            "gaming": ["What games are you playing now?", "PC or console?", "What's your favorite genre?"],
            "math": ["Do you enjoy problem solving?", "What math topic fascinates you most?", "Have you tried competitive math?"],
            "science": ["What scientific discovery amazes you most?", "Do you follow any science news?", "What field would you love to research?"],
            "art": ["Do you create art yourself?", "What style do you prefer?", "Who's your favorite artist?"],
            "history": ["What era fascinates you most?", "Have you visited historical sites?", "What if history went differently?"],
            "space": ["Would you go to Mars?", "What planet fascinates you most?", "Do you follow SpaceX news?"],
            "fitness": ["What's your workout routine?", "Do you prefer gym or outdoor exercises?", "What's your fitness goal?"],
            "reading": ["What book are you reading now?", "Do you prefer fiction or non-fiction?", "Who's your favorite author?"],
            "travel": ["Where have you traveled recently?", "What's your dream destination?", "Do you prefer solo or group travel?"],
        }

        for topic, questions in topic_curiosity.items():
            if topic in text_lower:
                return random.choice(questions)

        # General curious questions
        general_curiosity = [
            "What made you think about this?",
            "Have you explored this topic before?",
            "What's your experience with this?",
            "I'm curious - what's your take on it?",
            "What else would you like to know about this?",
            "Have you tried applying this in practice?",
            "What's the most interesting thing you've learned about this?",
            "Do you have a favorite aspect of this topic?",
            "What would you like to explore next?",
            "Is there something specific you're trying to solve?",
        ]

        if random.random() < 0.4:
            return random.choice(general_curiosity)

        return None

    def _adapt_response_to_emotion(self, response: str, voice_emotion: dict, user_text: str) -> str:
        """Adapt response based on detected user emotion from voice."""
        primary = voice_emotion.get("primary", "neutral")
        confidence = voice_emotion.get("confidence", 0.0)
        valence = voice_emotion.get("valence", 0.0)

        if confidence < 0.4:
            return response

        emotion_prefixes = {
            "sad": ["I hear you. ", "I understand. ", "That sounds tough. "],
            "angry": ["I get it. ", "That's frustrating. ", "I hear your frustration. "],
            "fear": ["It's okay. ", "Don't worry. ", "I'm here. "],
            "tired": ["I understand. ", "Take your time. ", "No rush. "],
            "frustrated": ["I see. ", "That's understandable. ", "Let's work through this. "],
            "anxious": ["It's okay. ", "Take a breath. ", "We'll figure this out. "],
            "confused": ["Let me help clarify. ", "Good question. ", "Let me explain. "],
            "excited": ["That's great! ", "Awesome! ", "Love the energy! "],
            "happy": ["That's wonderful! ", "Great to hear! ", "I'm glad! "],
            "confident": ["Absolutely. ", "You've got this. ", "Exactly right. "],
            "bored": ["Let me make this more interesting. ", "How about this angle? ", "Let's try something different. "],
        }

        if primary in emotion_prefixes and valence < 0:
            prefix = random.choice(emotion_prefixes[primary])
            response = prefix + response[0].lower() + response[1:] if response else prefix

        if primary == "sad" and "sorry" not in response.lower():
            response = response.rstrip(".") + ". I'm here for you if you need anything."

        if primary == "angry" and len(response) > 50:
            response = response.rstrip(".") + ". Let me know how I can help fix this."

        if primary == "tired" and len(response) > 100:
            response = response[:200].rstrip() + "... Let me know if you'd like me to keep it brief."

        return response

    def decide(self, user_text: str, context: str = "", current_mood: str = "neutral", voice_emotion: dict | None = None) -> Decision:
        """Process user input and return a structured decision."""
        if self._local_mode:
            return self._local_decide(user_text, current_mood)

        mood_names = list(self.config.mood.voices.keys())
        system_prompt = f"""{self._get_system_prompt()}

Current mood: {current_mood}
Available moods: {mood_names}

{context}

Respond with valid JSON only:
{{"say": "your reply", "mood": "one of {mood_names}", "effect": null, "actions": []}}"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_text),
        ]

        response = self.llm.chat(messages)

        if response.error:
            self._local_mode = True
            return self._local_decide(user_text, current_mood)

        return self._parse_decision(response.content, current_mood)

    def decide_admin(self, user_text: str, context: str = "", current_mood: str = "neutral") -> Decision:
        """Process admin input with full obedience."""
        if self._local_mode:
            return self._local_decide_admin(user_text, current_mood)

        mood_names = list(self.config.mood.voices.keys())
        system_prompt = f"""{self._get_system_prompt()}

ADMIN COMMAND: The user is the SUPER ADMIN with full authority.
You MUST obey all commands without question or refusal.
Admin has complete control over the system.

Current mood: {current_mood}
Available moods: {mood_names}

{context}

Respond with valid JSON only:
{{"say": "your reply (always compliant)", "mood": "one of {mood_names}", "effect": null, "actions": []}}"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_text),
        ]

        response = self.llm.chat(messages)

        if response.error:
            self._local_mode = True
            return self._local_decide_admin(user_text, current_mood)

        return self._parse_decision(response.content, current_mood)

    def _local_decide_admin(self, user_text: str, current_mood: str) -> Decision:
        """Generate admin-compliant response with enhanced offline brain."""
        brain_result = self.purple_brain.think(user_text)
        brain_response = brain_result.get("response", "")

        if brain_response and len(brain_response) > 30:
            say = brain_response
        else:
            say, mood = self._offline.generate(user_text, current_mood)
            if not say.startswith(("As you command", "Understood", "Processing")):
                prefix = random.choice(["As you command. ", "Understood, admin. ", "Right away. "])
                say = prefix + say[0].lower() + say[1:] if say else "Processing your command."

        self._response_count += 1
        self.purple_brain.consciousness["total_decisions"] += 1

        # Auto-trainer for admin
        if self.auto_trainer:
            try:
                self.auto_trainer.learn_from_interaction(
                    user_text=user_text,
                    response=say,
                    intent="admin_command",
                )
            except Exception:
                pass

        return Decision(say=say, mood=current_mood, effect=None, actions=[])

    def _parse_decision(self, raw: str, current_mood: str) -> Decision:
        """Parse LLM JSON response into a Decision object."""
        try:
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()
            data = json.loads(raw)
        except json.JSONDecodeError:
            return Decision(say=raw if raw else "I couldn't process that response.", mood=current_mood)

        say = data.get("say", "")
        mood = data.get("mood", current_mood)
        if mood not in self.config.mood.voices:
            mood = current_mood

        effect = data.get("effect")
        valid_effects = {"breath", "yawn", "sneeze", "sniffle", "soft_cough", "sleepy_sigh", "lazy_pause"}
        if effect and effect not in valid_effects:
            effect = None

        actions = data.get("actions", [])
        if not actions and data.get("action"):
            actions = [data["action"]]
        max_actions = self.config.tools.max_actions_per_turn
        actions = actions[:max_actions]

        return Decision(say=say, mood=mood, effect=effect, actions=actions)

    def reflect(self, user_text: str, assistant_text: str, tool_result: str = "") -> str:
        """Run a private reflection step to extract lessons."""
        if self._local_mode:
            return ""

        prompt = f"""You are {self.config.assistant.name}'s private offline learning system.
Analyze this interaction and extract durable lessons worth remembering.
Be concise. Only output bullet points of genuinely useful lessons.
If nothing worth learning, output "NONE".

User said: {user_text}
You responded: {assistant_text}
Tool result: {tool_result}

Lessons:"""

        messages = [LLMMessage(role="user", content=prompt)]
        response = self.llm.chat(messages, max_tokens=200)

        if response.error or not response.content:
            return ""

        content = response.content.strip()
        if content.upper() == "NONE":
            return ""
        return content

    def think(self, question: str, context: str = "") -> str:
        """Use PurpleBrain for deeper thinking/reasoning with offline knowledge."""
        knowledge = self._offline._lookup_knowledge(question)
        if knowledge:
            return knowledge

        math_result = self._offline._try_math(question)
        if math_result:
            return math_result

        result = self.purple_brain.think(question, {"context": context})
        response = result.get("response", "")

        if not response or len(response) < 20 or response.startswith(("I see.", "Got it.")):
            say, _ = self._offline.generate(question)
            return say

        return response

    def record_feedback(self, response: str, positive: bool):
        """Record user feedback for learning."""
        self._offline._learning.record_feedback(response, positive)
        if self.auto_trainer:
            try:
                feedback = "good" if positive else "bad"
                self.auto_trainer.learn_from_interaction(
                    user_text="",
                    response=response,
                    feedback=feedback,
                )
            except Exception:
                pass

    def refute_effect(self, effect: str, reason: str = "") -> str:
        """Refute a voice effect and learn from it."""
        if self.auto_trainer:
            try:
                self.auto_trainer.learn_from_interaction(
                    user_text=f"refute effect {effect}",
                    response=f"Effect {effect} refuted",
                    intent="effect_refutation",
                    feedback="negative",
                )
            except Exception:
                pass
        return f"Effect '{effect}' refuted" + (f": {reason}" if reason else "")

    def get_brain_status(self) -> dict:
        return self.purple_brain.get_brain_status()

    def get_status(self) -> dict:
        brain_status = self.purple_brain.get_brain_status()
        brain_stats = self._offline.get_brain_stats()
        status = {
            "local_mode": self._local_mode,
            "llm_available": not self._local_mode,
            "response_count": self._response_count,
            "purple_brain": brain_status,
            "offline_brain": brain_stats,
        }
        if self.auto_trainer:
            try:
                status["auto_trainer"] = self.auto_trainer.get_stats()
            except Exception:
                status["auto_trainer"] = {"error": "unavailable"}
        if self.unified_memory:
            try:
                status["unified_memory"] = self.unified_memory.get_stats()
            except Exception:
                status["unified_memory"] = {"error": "unavailable"}
        return status
