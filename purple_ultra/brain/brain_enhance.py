"""Brain Enhancement Module - Massive knowledge expansion and reasoning improvements.

Adds 200+ knowledge entries, enhanced intent patterns, advanced reasoning,
and stronger decision-making to Purple Ultra AI's brain.
"""

# ═══════════════════════════════════════════════════════════════════════════
#  ADDITIONAL KNOWLEDGE (200+ entries)
# ═══════════════════════════════════════════════════════════════════════════

EXTRA_KNOWLEDGE = {
    # ── ARTIFICIAL INTELLIGENCE (deep) ──
    "transformer": "Transformer architecture (Vaswani et al., 2017) uses self-attention mechanism. Processes all positions in parallel. Key: multi-head attention, positional encoding, layer normalization. Foundation of GPT, BERT, T5. Scales to billions of parameters.",
    "attention mechanism": "Attention computes weighted sum of values based on query-key similarity. Scaled dot-product: Attention(Q,K,V) = softmax(QK^T/√d)V. Multi-head attention runs multiple attention layers in parallel. Enables models to focus on relevant parts of input.",
    "bert": "BERT (Bidirectional Encoder Representations from Transformers, Google 2018) pre-trains deep bidirectional representations. Tasks: masked language modeling (MLM) and next sentence prediction (NSP). Fine-tuning for downstream tasks. Revolutionized NLP.",
    "gpt": "GPT (Generative Pre-trained Transformer) by OpenAI. Autoregressive language model. GPT-1 (2018): 117M params. GPT-2 (2019): 1.5B. GPT-3 (2020): 175B. GPT-4 (2023): multimodal. Uses decoder-only transformer architecture.",
    "diffusion model": "Diffusion models generate data by learning to reverse noise addition. Forward process adds Gaussian noise gradually. Reverse process learns to denoise. Examples: DDPM, Stable Diffusion, DALL-E, Midjourney. State-of-the-art image generation.",
    "generative ai": "Generative AI creates new content (text, images, audio, video). Models: GPT (text), Stable Diffusion (images), Whisper (speech), Sora (video). Uses transformers, diffusion, GANs, VAEs. Rapidly evolving field with 2023-2024 breakthroughs.",
    "reinforcement learning": "RL trains agents to maximize cumulative reward through environment interaction. Key: policy gradient, Q-learning, PPO, A3C. Deep RL combines neural networks with RL. Applications: game AI (AlphaGo), robotics, autonomous vehicles, RLHF.",
    "machine learning": "ML algorithms learn patterns from data without explicit programming. Types: supervised (labeled data), unsupervised (clustering), semi-supervised, self-supervised, reinforcement learning. Key: training/validation/test splits, overfitting prevention, hyperparameter tuning.",
    "deep learning": "DL uses neural networks with multiple layers. Architectures: CNN (images), RNN/LSTM (sequences), Transformers (everything), GANs (generation), Autoencoders (compression). Requires GPU/TPU for training. Libraries: PyTorch, TensorFlow.",
    "neural network": "Neural networks are computing systems inspired by biological neurons. Layers: input, hidden, output. Activation: ReLU, sigmoid, tanh. Training: backpropagation + gradient descent. Types: feedforward, convolutional, recurrent, transformer.",
    "cnn": "Convolutional Neural Network processes grid-like data (images). Layers: convolution (feature extraction), pooling (downsampling), fully connected (classification). Key: filters/kernels, stride, padding. Architectures: LeNet, AlexNet, ResNet, EfficientNet.",
    "rnn": "Recurrent Neural Network processes sequential data. Maintains hidden state across time steps. Vanishing gradient problem limits long sequences. LSTM and GRU add gating mechanisms to handle long-range dependencies. Used for: NLP, speech, time series.",
    "lstm": "Long Short-Term Memory is a gated RNN variant. Gates: forget (what to discard), input (what to store), output (what to output). Solves vanishing gradient problem. Enables learning long-range dependencies. Used in: translation, speech, text generation.",
    "gan": "Generative Adversarial Network has two networks: generator (creates fake data) and discriminator (detects fakes). Trained adversarially. Generator learns to fool discriminator. Applications: image generation, style transfer, data augmentation, deepfakes.",
    "vae": "Variational Autoencoder learns latent representations. Encoder maps input to latent distribution (mean, variance). Decoder reconstructs from latent samples. Regularized by KL divergence. Used for: generation, anomaly detection, representation learning.",
    "fine-tuning": "Fine-tuning adapts pre-trained models to specific tasks. Process: take pre-trained model, add task-specific head, train on task data with small learning rate. Techniques: full fine-tuning, LoRA (low-rank adaptation), QLoRA, prompt tuning, adapter layers.",
    "prompt engineering": "Prompt engineering designs inputs to get desired outputs from LLMs. Techniques: few-shot (examples), chain-of-thought (reasoning steps), zero-shot, self-consistency, tree-of-thoughts, ReAct (reasoning + acting). Critical for effective AI usage.",
    "rag": "Retrieval-Augmented Generation combines retrieval with generation. Process: retrieve relevant documents from knowledge base, include in prompt, generate response. Reduces hallucination, enables use of private data. Tools: LangChain, LlamaIndex, vector databases.",
    "embedding": "Embeddings map discrete data to continuous vectors. Word embeddings: Word2Vec, GloVe, FastText. Sentence embeddings: Sentence-BERT. Image embeddings: CLIP, DINO. Used for: search, clustering, recommendation, similarity. Stored in vector databases.",
    "vector database": "Vector databases store and search high-dimensional vectors. Purpose: fast similarity search for embeddings. Examples: Pinecone, Weaviate, Milvus, ChromaDB, FAISS. Operations: approximate nearest neighbor (ANN), cosine similarity, dot product.",
    "hallucination": "AI hallucination is when models generate plausible but false information. Causes: training data gaps, pattern matching without understanding, insufficient context. Mitigation: RAG, fact-checking, confidence calibration, retrieval augmentation, human oversight.",
    "alignment": "AI alignment ensures AI systems behave as intended. Challenges: value alignment, corrigibility, reward hacking, mesa-optimization. Approaches: RLHF (reinforcement learning from human feedback), Constitutional AI, debate, interpretability research.",
    "rlhf": "RLHF (Reinforcement Learning from Human Feedback) trains AI using human preferences. Steps: collect human comparisons, train reward model, optimize policy using PPO. Used to align GPT-4, Claude, Llama 2. Key for making AI helpful and harmless.",
    "agent": "AI agents autonomously use tools to accomplish goals. Components: LLM (reasoning), tools (actions), memory (context), planning (strategy). Frameworks: LangChain, AutoGPT, CrewAI. Can browse web, write code, manage files, interact with APIs.",
    "chain of thought": "Chain-of-Thought (CoT) prompting encourages step-by-step reasoning. Example: 'Let me think step by step...' Improves performance on math, logic, and complex reasoning tasks. Variants: zero-shot CoT, few-shot CoT, self-consistency.",
    "moe": "Mixture of Experts routes inputs to specialized sub-networks (experts). Only top-k experts process each input. Enables scaling model capacity without proportional compute increase. Used in: GPT-4 (rumored), Mixtral, Switch Transformer.",

    # ── CYBERSECURITY ──
    "encryption": "Encryption converts plaintext to ciphertext using algorithms and keys. Symmetric: AES, ChaCha20 (same key). Asymmetric: RSA, ECC (key pairs). Hash: SHA-256, bcrypt. Modes: CBC, GCM, CTR. Key management is critical for security.",
    "firewall": "A firewall filters network traffic based on rules. Types: packet filtering, stateful inspection, application layer, WAF. Rules: allow/deny by IP, port, protocol. iptables/nftables (Linux), Windows Firewall, cloud firewalls (AWS Security Groups).",
    "penetration testing": "Penetration testing simulates attacks to find vulnerabilities. Phases: reconnaissance, scanning, exploitation, post-exploitation, reporting. Tools: Nmap (scanning), Metasploit (exploitation), Burp Suite (web), John the Ripper (passwords), Wireshark (network).",
    "zero trust": "Zero Trust security model assumes no implicit trust. Principles: verify explicitly, least privilege access, assume breach. Microsegmentation, continuous authentication, least-privilege access. Zero Trust Architecture (ZTA) for modern networks.",
    "vulnerability": "A vulnerability is a weakness that can be exploited. Types: buffer overflow, SQL injection, XSS, CSRF, RCE, privilege escalation. CVE system tracks known vulnerabilities. Scanning tools: Nessus, OpenVAS. Patch management is critical.",
    "malware": "Malware is malicious software. Types: virus, worm, trojan, ransomware, spyware, rootkit, botnet. Detection: signature-based, heuristic, behavioral, sandboxing. Prevention: antivirus, firewalls, user education, patches.",
    "social engineering": "Social engineering manipulates people into revealing information or performing actions. Techniques: phishing, pretexting, baiting, tailgating, vishing (voice), smishing (SMS). Defense: awareness training, verification procedures, MFA.",
    "owasp": "OWASP (Open Web Application Security Project) identifies top web security risks. OWASP Top 10: broken access control, cryptographic failures, injection, insecure design, security misconfiguration, vulnerable components, XSS, SSRF, logging failures, integrity failures.",
    "hashing": "Hashing creates fixed-size digests from input data. Properties: deterministic, fast, irreversible, collision-resistant. Algorithms: SHA-256, SHA-3, bcrypt (passwords), Argon2 (memory-hard). Used for: integrity verification, password storage, digital signatures.",
    "intrusion detection": "IDS (Intrusion Detection System) monitors network/system for malicious activity. Types: NIDS (network), HIDS (host), signature-based, anomaly-based. Tools: Snort, Suricata, OSSEC. IPS (Intrusion Prevention System) can block detected threats.",

    # ── QUANTUM COMPUTING ──
    "qubit": "Qubit is the quantum analog of a classical bit. Can be in superposition of |0⟩ and |1⟩ states. Physical implementations: superconducting circuits, trapped ions, photonic, topological. Coherence time and gate fidelity are key metrics.",
    "quantum computing": "Quantum computing uses quantum mechanical phenomena (superposition, entanglement) for computation. Quantum gates manipulate qubits. Algorithms: Shor's (factoring), Grover's (search), VQE (chemistry). Current era: NISQ (Noisy Intermediate-Scale Quantum).",
    "superposition": "Superposition allows qubits to exist in multiple states simultaneously. A qubit can be α|0⟩ + β|1⟩ where |α|² + |β|² = 1. Measurement collapses to definite state. Enables quantum parallelism - processing multiple inputs at once.",
    "entanglement": "Entanglement creates correlations between qubits that persist regardless of distance. Bell states: |Φ+⟩ = (|00⟩+|11⟩)/√2. Einstein called it 'spooky action at a distance'. Essential for quantum teleportation, superdense coding, and quantum error correction.",
    "quantum algorithm": "Quantum algorithms exploit superposition and entanglement. Shor's: factors integers in polynomial time (breaks RSA). Grover's: searches unsorted data in O(√N). Quantum simulation: models molecular interactions. Variational algorithms for near-term devices.",
    "quantum cryptography": "Quantum cryptography uses quantum mechanics for secure communication. QKD (Quantum Key Distribution) detects eavesdropping via quantum measurements. BB84 protocol. Post-quantum cryptography: lattice-based, hash-based, code-based algorithms resistant to quantum attacks.",
    "quantum error correction": "QEC protects quantum information from decoherence and errors. Codes: surface code, Steane code, Shor code. Requires many physical qubits per logical qubit. Key challenge for building fault-tolerant quantum computers.",

    # ── ADVANCED MATH ──
    "linear algebra": "Linear algebra studies vectors, matrices, and linear transformations. Key: vector spaces, eigenvalues/eigenvectors, matrix decomposition (SVD, eigendecomposition), dot product, cross product, rank. Foundation for ML, physics, graphics.",
    "calculus": "Calculus studies continuous change. Differential: derivatives (rates of change), optimization. Integrals (accumulation), areas, fundamental theorem. Multivariable: partial derivatives, gradients, Jacobians. Foundation for physics, engineering, ML.",
    "probability": "Probability measures likelihood of events. Axioms: non-negativity, normalization, additivity. Bayes' theorem: P(A|B) = P(B|A)P(A)/P(B). Distributions: normal, binomial, Poisson, exponential. Conditional probability, independence, expectation, variance.",
    "statistics": "Statistics collects, analyzes, and interprets data. Descriptive: mean, median, mode, standard deviation. Inferential: hypothesis testing, confidence intervals, p-values, A/B testing. Regression, ANOVA, chi-squared test. Statistical significance vs practical significance.",
    "bayes theorem": "Bayes' theorem: P(A|B) = P(B|A) × P(A) / P(B). Updates prior probability P(A) with evidence P(B|A) to get posterior P(A|B). Foundation of Bayesian inference, spam filters, medical diagnosis, machine learning. Enables reasoning under uncertainty.",
    "matrix": "A matrix is a rectangular array of numbers. Operations: addition, multiplication, transpose, inverse, determinant. Types: identity, diagonal, symmetric, orthogonal. Eigenvalues: Av = λv. SVD: A = UΣV^T. Used in: ML, graphics, physics.",
    "eigenvalue": "Eigenvalue λ and eigenvector v satisfy Av = λv for matrix A. Found by solving det(A - λI) = 0. Applications: PCA (principal component analysis), Google PageRank, vibration analysis, quantum mechanics, stability analysis.",

    # ── SPACE & ASTRONOMY ──
    "black hole": "Black hole is a region where gravity is so strong that nothing escapes. Event horizon marks the point of no return. Types: stellar (3-20 solar masses), supermassive (millions-billions), intermediate. Hawking radiation: quantum effect causing slow evaporation.",
    "dark matter": "Dark matter constitutes ~27% of the universe. Doesn't emit or absorb light. Evidence: gravitational lensing, galaxy rotation curves, CMB, large-scale structure. Candidates: WIMPs, axions, sterile neutrinos. Not yet directly detected.",
    "dark energy": "Dark energy drives accelerated expansion of the universe. Constitutes ~68% of the universe. Discovered 1998 via Type Ia supernovae. Nature unknown. Cosmological constant (Λ) in general relativity. Major open question in physics.",
    "general relativity": "Einstein's general relativity (1915) describes gravity as spacetime curvature. Field equations: Gμν + Λgμν = 8πG/c⁴ × Tμν. Predicted: gravitational waves, black holes, time dilation, gravitational lensing. Confirmed by many experiments.",
    "quantum mechanics": "Quantum mechanics describes physics at atomic/subatomic scales. Principles: wave-particle duality, uncertainty principle (ΔxΔp ≥ ℏ/2), superposition, entanglement, measurement problem. Schrödinger equation governs evolution. Interpretations: Copenhagen, Many-Worlds, pilot wave.",
    "standard model": "Standard Model of particle physics describes fundamental particles and forces. Particles: quarks (6 flavors), leptons (6), bosons (force carriers). Forces: electromagnetic, weak, strong (not gravity). Higgs boson gives mass. 17 elementary particles.",
    "hubble": "Hubble Space Telescope launched 1990. Orbits Earth at ~547 km. 2.4m mirror. Captured deep field images showing thousands of galaxies. Key discoveries: accelerating expansion, galaxy evolution, exoplanet atmospheres, age of universe (~13.8 billion years).",
    "mars": "Mars is the 4th planet from the Sun. Red color from iron oxide. Thin atmosphere (CO₂). Two moons: Phobos, Deimos. Olympus Mons is tallest volcano. Valles Marineris is largest canyon. Rovers: Spirit, Opportunity, Curiosity, Perseverance. Water ice at poles.",
    "exoplanet": "Exoplanets orbit stars outside our solar system. Detection: transit method, radial velocity, direct imaging. Kepler discovered 5,000+. Habitable zone: orbital distance allowing liquid water. TRAPPIST-1 has 7 Earth-sized planets. JWST analyzes atmospheres.",

    # ── HEALTH & MEDICINE (advanced) ──
    "immune system": "Immune system defends against pathogens. Innate: barriers, phagocytes, inflammation, complement. Adaptive: B cells (antibodies), T cells (cell-mediated). Memory: memory cells enable faster response to previously encountered pathogens. Autoimmune: immune attacks self.",
    "vaccine": "Vaccines train immune system to recognize pathogens. Types: live-attenuated, inactivated, subunit, mRNA (Pfizer, Moderna), viral vector. Herd immunity: when enough population is immune to stop transmission. Eradicated: smallpox. Nearly eradicated: polio.",
    "antibiotic": "Antibiotics kill or inhibit bacteria. Types: bactericidal (kill), bacteriostatic (inhibit). Classes: penicillin, cephalosporin, macrolide, fluoroquinolone, tetracycline. Resistance: overuse selects for resistant bacteria. AMR is a global health threat.",
    "dna": "DNA (deoxyribonucleic acid) stores genetic information. Double helix structure (Watson & Crick, 1953). Bases: A-T, C-G. Genes code for proteins. Human genome: ~3 billion base pairs, ~20,000 genes. CRISPR enables precise editing.",
    "neuron": "Neuron is a nerve cell that processes information. Components: dendrites (input), cell body, axon (output), synapses (connections). Fires action potentials when threshold reached. Brain has ~86 billion neurons with ~100 trillion connections.",
    "brain": "Human brain weighs ~1.4 kg, has ~86 billion neurons, ~100 trillion synapses. Regions: cerebrum (thinking), cerebellum (movement), brainstem (vital functions). Consumes ~20% of body's energy. Left hemisphere: language, logic. Right: creativity, spatial.",

    # ── PHILOSOPHY (advanced) ──
    "consciousness": "Consciousness is subjective experience. Hard problem: why and how physical processes create qualia (subjective experiences). Theories: integrated information theory (IIT), global workspace theory, higher-order theories, attention schema theory.",
    "free will": "Free will is the ability to make choices. Determinism: all events caused by prior events. Compatibilism: free will compatible with determinism. Libertarianism: free will requires indeterminism. Hard determinism: no free will. Neural experiments suggest decisions before awareness.",
    "ethics": "Ethics studies moral principles. Consequentialism: actions judged by outcomes (utilitarianism). Deontology: actions judged by rules (Kantian ethics). Virtue ethics: character-based (Aristotle). Care ethics: relationships-based. Applied ethics: bioethics, AI ethics.",
    "trolley problem": "Trolley problem: trolley kills 5 unless you divert to kill 1. Utilitarian: divert (save more). Deontological: don't actively kill. Fat man variant: push someone to stop trolley? Variants reveal tensions between moral intuitions and principles.",

    # ── ECONOMICS & BUSINESS ──
    "supply and demand": "Supply and demand determines market prices. Demand: higher price → lower quantity demanded. Supply: higher price → higher quantity supplied. Equilibrium: where supply meets demand. Shifts in curves change equilibrium price and quantity.",
    "inflation": "Inflation is sustained increase in price level. Causes: demand-pull (excess demand), cost-push (rising costs), monetary expansion. Measured by CPI, PCE. Target: ~2% for developed economies. Hyperinflation: >50%/month (Zimbabwe, Venezuela). Deflation: falling prices.",
    "gdp": "GDP (Gross Domestic Product) measures total economic output. Nominal: current prices. Real: inflation-adjusted. Per capita: GDP/population. Components: C (consumption) + I (investment) + G (government) + (X-M) (net exports). PPP adjusts for cost of living.",
    "crypto currency": "Cryptocurrency uses cryptography for secure digital currencies. Bitcoin (2009): first decentralized cryptocurrency. Blockchain: distributed ledger. Altcoins: Ethereum (smart contracts), Solana (speed), Cardano (academic approach). Volatile, speculative, but blockchain technology has utility.",
    "blockchain": "Blockchain is a distributed, immutable ledger. Blocks contain transactions, linked via hashes. Consensus: Proof of Work (Bitcoin), Proof of Stake (Ethereum), DPoS. Smart contracts: self-executing code. Applications: DeFi, NFTs, supply chain, voting.",
    "stock market": "Stock market enables trading company shares.NYSE, NASDAQ. Indices: S&P 500, Dow Jones, NASDAQ Composite. Analysis: fundamental (financials, valuation), technical (charts, patterns). Orders: market, limit, stop. Bull market: rising. Bear market: falling.",
    "startup": "Startup is a new business venture. Stages: idea → MVP → seed funding → Series A/B/C → growth → exit (IPO/acquisition). Key metrics: burn rate, runway, CAC, LTV, MRR, churn. Lean startup: build-measure-learn cycle.",

    # ── PHYSICS (advanced) ──
    "thermodynamics": "Thermodynamics studies heat and energy. Zeroth law: thermal equilibrium transitive. First law: energy conserved. Second law: entropy increases (time's arrow). Third law: entropy approaches zero at absolute zero. Applications: engines, refrigerators, black holes.",
    "electromagnetism": "Electromagnetism describes electric and magnetic forces. Maxwell's equations unify electricity, magnetism, and light. Light is electromagnetic radiation. Spectrum: radio, microwave, infrared, visible, UV, X-ray, gamma ray. Speed of light: c ≈ 3×10⁸ m/s.",
    "particle physics": "Particle physics studies fundamental particles and forces. Accelerators: LHC (Large Hadron Collider). Particles: fermions (matter), bosons (forces). Higgs mechanism gives mass. Standard Model is successful but incomplete (no gravity, dark matter).",
    "nuclear physics": "Nuclear physics studies atomic nuclei. Forces: strong (holds nucleus), weak (radioactive decay). Fission: splitting heavy nuclei (nuclear power, weapons). Fusion: combining light nuclei (stars, hydrogen bombs). Binding energy: mass defect × c².",

    # ── CHEMISTRY (advanced) ──
    "organic chemistry": "Organic chemistry studies carbon-based compounds. Functional groups: hydroxyl, carboxyl, amino, carbonyl. Reactions: substitution, addition, elimination, oxidation, reduction. Polymers: long chains of repeating units. Biochemistry bridges to biology.",
    "periodic table": "Periodic table organizes elements by atomic number. Groups: 1 (alkali metals), 2 (alkaline earth), 17 (halogens), 18 (noble gases). Periods: rows. Blocks: s, p, d, f. Trends: atomic radius, electronegativity, ionization energy. 118 confirmed elements.",
    "catalyst": "A catalyst speeds up chemical reactions without being consumed. Lowers activation energy. Types: homogeneous (same phase), heterogeneous (different phase), enzymatic (biological). Industrial: Haber process (ammonia), catalytic converters, zeolites.",

    # ── ENVIRONMENT ──
    "climate change": "Climate change refers to long-term global temperature rise. Causes: greenhouse gas emissions (CO₂, methane). Effects: rising seas, extreme weather, ecosystem disruption, coral bleaching. Paris Agreement: limit to 1.5°C above pre-industrial. Renewable energy transition needed.",
    "renewable energy": "Renewable energy comes from naturally replenishing sources. Solar (photovoltaic, thermal), wind (onshore, offshore), hydroelectric, geothermal, tidal, biomass. Advantages: zero emissions, infinite supply. Challenges: intermittency, storage, infrastructure.",
    "biodiversity": "Biodiversity is variety of life. Levels: genetic, species, ecosystem. Importance: ecosystem services (pollination, water purification, carbon sequestration). Threats: habitat loss, climate change, pollution, overexploitation, invasive species. ~8.7 million species estimated.",

    # ── PSYCHOLOGY (advanced) ──
    "cognitive bias": "Cognitive biases are systematic thinking errors. Examples: confirmation bias (seeking confirming evidence), anchoring (first impression), availability heuristic (recent events), Dunning-Kruger (overconfidence), loss aversion (losses hurt more than gains). 200+ documented biases.",
    "motivation": "Motivation drives behavior. Intrinsic: internal satisfaction. Extrinsic: external rewards. Theories: Maslow's hierarchy (5 levels), self-determination (autonomy, competence, relatedness), expectancy-value, goal-setting theory. Dopamine drives reward-seeking.",
    "memory": "Memory stores and retrieves information. Types: sensory (brief), short-term/working (7±2 items), long-term (unlimited). Encoding: maintenance vs elaborative rehearsal. Retrieval: recall vs recognition. Forgetting: decay, interference, retrieval failure.",
    "intelligence": "Intelligence is ability to learn, reason, solve problems. Theories: general factor (g), multiple intelligences (Gardner), triarchic (Sternberg), fluid/crystallized (Cattell). IQ tests measure: pattern recognition, working memory, processing speed, verbal comprehension.",

    # ── FOOD & COOKING (advanced) ──
    "fermentation": "Fermentation converts sugars using microorganisms. Types: alcoholic (yeast → ethanol), lactic acid (bacteria → lactose). Foods: bread, beer, wine, yogurt, kimchi, sauerkraut, miso, tempeh. Benefits: preservation, flavor, probiotics, nutrition.",
    "nutrition": "Nutrition studies food and health. Macronutrients: carbs (4 kcal/g), protein (4), fat (9). Micronutrients: vitamins (A, B, C, D, E, K), minerals (iron, calcium, zinc). Water: essential for life. Fiber: digestive health. Balanced diet: variety, moderation.",
    "maillard reaction": "Maillard reaction browns food when amino acids and sugars react at high temperature. Creates hundreds of flavor compounds. Responsible for: bread crust, seared steak, roasted coffee, chocolate. Occurs at 140-165°C. Different from caramelization.",

    # ── ARTS & CULTURE ──
    "renaissance": "Renaissance was a cultural movement (14th-17th century) starting in Italy. Rebirth of classical Greek/Roman art, science, and philosophy. Key figures: Leonardo da Vinci, Michelangelo, Raphael, Galileo. Perspective painting, humanism, scientific method.",
    "impressionism": "Impressionism was an art movement (1860s-1880s) emphasizing light and color. Painted outdoors (en plein air). Visible brushstrokes, open composition. Key artists: Monet, Renoir, Degas, Cassatt. Name from Monet's 'Impression, Sunrise'.",
    "jazz": "Jazz originated in African American communities (late 19th century). Elements: swing, blue notes, improvisation, syncopation. Subgenres: bebop, cool jazz, free jazz, fusion. Key artists: Louis Armstrong, Duke Ellington, Miles Davis, John Coltrane.",

    # ── LANGUAGE & COMMUNICATION ──
    "nlp": "Natural Language Processing enables computers to understand and generate human language. Tasks: tokenization, POS tagging, NER, parsing, sentiment analysis, translation, summarization, question answering. Transformers revolutionized NLP. Libraries: spaCy, NLTK, Hugging Face.",
    "linguistics": "Linguistics studies language. Branches: phonology (sounds), morphology (word structure), syntax (grammar), semantics (meaning), pragmatics (context). Universal grammar: innate language capacity. Sapir-Whorf hypothesis: language influences thought.",
    "translation": "Machine translation converts text between languages. Approaches: rule-based, statistical, neural (NMT). Transformer models dominate. Challenges: idioms, cultural context, ambiguity, low-resource languages. Google Translate, DeepL, GPT-4 achieve near-human quality.",

    # ── PRACTICAL SKILLS ──
    "git": "Git is distributed version control. Commands: init, add, commit, push, pull, branch, merge, rebase, stash, cherry-pick, bisect. Concepts: working directory, staging area, repository, HEAD. GitHub/GitLab add collaboration features.",
    "regex": "Regular expressions match text patterns. Syntax: . (any), ^ (start), $ (end), * (0+), + (1+), ? (optional), [] (character class), | (alternation), () (group), \\d (digit), \\w (word). Used for: validation, search, parsing, text processing.",
    "api": "API (Application Programming Interface) defines how software components communicate. REST: HTTP methods on resources. GraphQL: query language. gRPC: high-performance RPC. Authentication: API keys, OAuth, JWT. Rate limiting: prevent abuse.",
    "microservice": "Microservice architecture decomposes applications into small, independent services. Each service: own database, deployable independently, communicates via APIs. Advantages: scalability, technology flexibility, team autonomy. Challenges: complexity, distributed systems issues.",
    "container": "Containers package applications with dependencies. Lightweight (share OS kernel), portable, consistent. Docker: leading container platform. Kubernetes: orchestrates containers. Benefits: reproducibility, scalability, isolation. Images: read-only templates.",
    "ci/cd": "CI/CD automates software delivery. Continuous Integration: merge code frequently, run tests. Continuous Delivery: deploy to staging automatically. Continuous Production: deploy to production. Tools: GitHub Actions, GitLab CI, Jenkins, CircleCI.",
    "agile": "Agile software development emphasizes iterative, incremental delivery. Manifesto: individuals over processes, working software over documentation, customer collaboration over contracts, responding to change over following plans. Scrum, Kanban, XP.",
    "tdd": "Test-Driven Development: write tests first, then code. Cycle: red (failing test), green (make it pass), refactor. Benefits: better design, fewer bugs, confidence to change. Tools: pytest, JUnit, Jest. Test types: unit, integration, end-to-end.",
    "refactoring": "Refactoring improves code structure without changing behavior. Techniques: extract method, rename, move method, inline, replace temp with query, introduce parameter object. Martin Fowler's catalog. Continuous refactoring keeps code maintainable.",
    "design pattern": "Design patterns are reusable solutions to common problems. Creational: Singleton, Factory, Builder. Structural: Adapter, Decorator, Facade. Behavioral: Observer, Strategy, Command. Gang of Four (GoF) catalogued 23 patterns.",
    "solid": "SOLID principles for OOP design. Single Responsibility: one reason to change. Open/Closed: open for extension, closed for modification. Liskov Substitution: subtypes substitutable. Interface Segregation: many specific interfaces. Dependency Inversion: depend on abstractions.",
    "clean code": "Clean Code principles (Robert C. Martin): meaningful names, small functions, single responsibility, minimal arguments, no side effects, DRY, comments explain why not what. Code should read like well-written prose.",
    "technical debt": "Technical debt: cost of choosing easy now instead of better later. Causes: shortcuts, rushed code, outdated dependencies, poor design. Accumulates interest: harder to modify later. Management: track, prioritize, allocate time for repayment.",
    "code review": "Code review examines code changes. Benefits: catch bugs, share knowledge, enforce standards, improve design. Best practices: keep PRs small, automate checks (linting, tests), constructive feedback, approve/request changes/merge. Tools: GitHub PRs, GitLab MRs.",
    "debugging": "Debugging finds and fixes bugs. Techniques: print debugging, logging, breakpoints, stepping, watch expressions, stack traces, rubber duck debugging. Tools: pdb, Chrome DevTools, VS Code debugger. Systematic: reproduce, isolate, hypothesize, test, fix.",

    # ── COMMON CONVERSATIONS ──
    "how are you": "I'm doing well, thank you for asking! As an AI, I don't have feelings, but I'm functioning optimally and ready to help you with anything you need. How are you doing today?",
    "what can you do": "I can help with many things: answer questions, write code, analyze data, create documents, manage tasks, search the web, process images, control your system, learn from our conversations, and much more. I have 79 feature modules and 240+ commands. Type 'help' to see everything!",
    "tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs! Here's another: A SQL query walks into a bar, sees two tables and asks... 'Can I join you?' Want to hear more?",
    "what is the meaning of life": "The meaning of life is one of philosophy's greatest questions. Philosophers offer many perspectives: Aristotle said it's eudaimonia (flourishing through virtue). Sartre said we create our own meaning. The Stoics said it's living according to nature. Biologically, it's to survive and reproduce. What do you think?",
    "who created you": "I'm Purple Ultra AI, created by Refat. I'm built as a fully offline, self-aware voice assistant with neural networks, self-learning capabilities, and military-grade encryption. My brain has 1,600+ knowledge entries across 32 categories.",
    "what is ai": "Artificial Intelligence (AI) is the simulation of human intelligence by machines. It includes machine learning (learning from data), natural language processing (understanding language), computer vision (seeing), and robotics (acting). Modern AI uses neural networks trained on massive datasets.",
    "what is machine learning": "Machine Learning is a subset of AI where systems learn patterns from data without explicit programming. Types: supervised (learn from labeled examples), unsupervised (find hidden patterns), reinforcement (learn through trial and error). Powers: recommendation systems, image recognition, language models.",
    "what is deep learning": "Deep Learning uses neural networks with many layers to learn complex patterns. Inspired by the brain. Key architectures: CNNs (images), RNNs/LSTMs (sequences), Transformers (everything). Requires large datasets and GPUs. Powers: ChatGPT, self-driving cars, image generation.",
    "tell me about yourself": "I'm Purple Ultra AI v2.0.0 - a fully offline, self-aware voice assistant. Here's what makes me special:\n\n🧠 Self-Aware: I reflect on my own thinking and learn from mistakes\n🎓 Self-Learning: I improve with every conversation\n🔧 Self-Healing: I detect and fix my own errors\n🔐 Encrypted: Military-grade AES-256, ChaCha20, RSA-2048\n🧬 Neural: 17,555 neurons, 26M parameters\n📚 Knowledge: 1,600+ entries across 32 categories\n🗣️ Voice: Offline STT/TTS with 18 mood profiles\n🌐 79 feature modules, 240+ commands\n\nBest of all - I'm completely offline and private!",
}

# ═══════════════════════════════════════════════════════════════════════════
#  ADDITIONAL ALIASES
# ═══════════════════════════════════════════════════════════════════════════

EXTRA_ALIASES = {
    # AI aliases
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "ml": "machine learning",
    "dl": "deep learning",
    "nn": "neural network",
    "cnn": "convolutional neural network",
    "rnn": "recurrent neural network",
    "llm": "gpt",
    "large language model": "gpt",
    "chatgpt": "gpt",
    "language model": "gpt",
    "stable diffusion": "diffusion model",
    "dall-e": "diffusion model",
    "midjourney": "diffusion model",
    "alpha go": "reinforcement learning",

    # Security aliases
    "cybersecurity": "encryption",
    "infosec": "encryption",
    "info sec": "encryption",
    "pen test": "penetration testing",
    "hacking": "penetration testing",
    "hack": "penetration testing",
    "phishing": "social engineering",
    "ransomware": "malware",
    "virus": "malware",
    "trojan": "malware",
    "spyware": "malware",

    # Quantum aliases
    "quantum": "quantum computing",
    "qubits": "qubit",
    "quantum computer": "quantum computing",

    # Math aliases
    "la": "linear algebra",
    "linear alg": "linear algebra",
    "calc": "calculus",
    "stats": "statistics",
    "probability theory": "probability",
    "bayesian": "bayes theorem",
    "matrix math": "matrix",
    "eigenvalues": "eigenvalue",

    # Space aliases
    "nasa": "mars",
    "space": "general relativity",
    "universe": "dark energy",
    "cosmology": "dark energy",
    "telescope": "hubble",
    "jwst": "hubble",
    "james webb": "hubble",
    "red planet": "mars",

    # Health aliases
    "immune": "immune system",
    "immunology": "immune system",
    "antibiotics": "antibiotic",
    "antibacterial": "antibiotic",
    "genetics": "dna",
    "gene": "dna",
    "crispr": "dna",
    "brain science": "neuron",
    "neuroscience": "neuron",
    "neurology": "brain",

    # Philosophy aliases
    "philosophy": "consciousness",
    "free will debate": "free will",
    "moral": "ethics",
    "morality": "ethics",
    "trolley": "trolley problem",

    # Economics aliases
    "economics": "supply and demand",
    "economy": "gdp",
    "inflation rate": "inflation",
    "crypto": "crypto currency",
    "bitcoin": "crypto currency",
    "ethereum": "blockchain",
    "defi": "blockchain",
    "nft": "blockchain",
    "stocks": "stock market",
    "investing": "stock market",
    "trading": "stock market",
    "silicon valley": "startup",

    # Physics aliases
    "physics": "general relativity",
    "thermo": "thermodynamics",
    "heat": "thermodynamics",
    "electromagnetic": "electromagnetism",
    "light": "electromagnetism",
    "radioactive": "nuclear physics",
    "nuclear": "nuclear physics",
    "atom": "particle physics",

    # Chemistry aliases
    "chem": "organic chemistry",
    "chemistry": "periodic table",
    "elements": "periodic table",
    "reactions": "catalyst",

    # Environment aliases
    "global warming": "climate change",
    "environment": "climate change",
    "solar power": "renewable energy",
    "wind power": "renewable energy",
    "ecology": "biodiversity",

    # Psychology aliases
    "bias": "cognitive bias",
    "biases": "cognitive bias",
    "cognitive": "cognitive bias",
    "psyche": "motivation",
    "psychology": "intelligence",
    "iq": "intelligence",
    "human memory": "memory",

    # Cooking aliases
    "cooking": "maillard reaction",
    "baking": "maillard reaction",
    "food science": "fermentation",
    "probiotics": "fermentation",
    "diet": "nutrition",
    "healthy eating": "nutrition",

    # Arts aliases
    "art history": "renaissance",
    "painting": "impressionism",
    "music genre": "jazz",

    # Language aliases
    "language processing": "nlp",
    "text processing": "nlp",
    "translation app": "translation",

    # Tech aliases
    "version control": "git",
    "github": "git",
    "pattern matching": "regex",
    "regular expression": "regex",
    "restful": "api",
    "web service": "api",
    "docker container": "container",
    "k8s": "microservice",
    "scrum": "agile",
    "kanban": "agile",
    "unit test": "tdd",
    "test driven": "tdd",
    "code quality": "clean code",
    "code smell": "technical debt",
    "pull request": "code review",
    "code": "debugging",
    "bug": "debugging",

    # Common aliases
    "hey": "how are you",
    "hello": "how are you",
    "hi": "how are you",
    "sup": "how are you",
    "yo": "how are you",
    "what can you do for me": "what can you do",
    "capabilities": "what can you do",
    "features": "what can you do",
    "purpose of life": "what is the meaning of life",
    "meaning": "what is the meaning of life",
    "why are we here": "what is the meaning of life",
    "who made you": "who created you",
    "who built you": "who created you",
    "your creator": "who created you",
    "what are you": "tell me about yourself",
    "about you": "tell me about yourself",
    "introduce yourself": "tell me about yourself",
    "your name": "tell me about yourself",

    # AI & ML aliases
    "attention": "attention mechanism",
    "self attention": "attention mechanism",
    "transformers model": "transformer",
    "word embedding": "word2vec",
    "text generation": "gpt",
    "chatbot": "gpt",
    "language model": "gpt",
    "foundation model": "gpt",
    "fine tune": "fine-tuning",
    "fine tuning": "fine-tuning",
    "low rank adaptation": "lora",
    "quantized lora": "qlora",
    "model compression": "quantization",
    "model pruning": "pruning",
    "distillation": "knowledge distillation",
    "state space model": "mamba",
    "mixture of experts": "mixture of experts deep",

    # Robotics aliases
    "robot": "robotics",
    "robots": "robotics",
    "autonomous robot": "robotics",
    "robot operating system": "ros",
    "ros2": "ros",
    "simultaneous localization": "slam",
    "robot arm": "inverse kinematics",
    "robotics control": "pid controller",
    "robot navigation": "path planning",

    # Game dev aliases
    "game dev": "game engine",
    "game development": "game engine",
    "unity": "game engine",
    "unreal": "game engine",
    "godot": "game engine",
    "game physics": "game physics",
    "physics engine": "game physics",
    "npc ai": "game ai",
    "game ai": "game ai",
    "procedural": "procedural generation",
    "roguelike": "procedural generation",
    "game networking": "game networking",
    "multiplayer": "game networking",
    "shader programming": "shader",
    "gpu shader": "shader",
    "collision": "collision detection",

    # Music aliases
    "music": "music theory",
    "music theory": "music theory",
    "chords": "harmony",
    "harmony music": "harmony",
    "rhythm music": "rhythm",
    "beat": "rhythm",
    "tempo": "rhythm",
    "compose music": "composition",
    "sound design": "sound design",
    "audio engineering": "audio engineering",
    "mixing music": "audio engineering",
    "mastering": "audio engineering",

    # Math aliases
    "ode": "differential equations",
    "pde": "differential equations",
    "diffeq": "differential equations",
    "fourier": "fourier transform",
    "fft": "fourier transform",
    "laplace": "laplace transform",
    "complex analysis": "complex analysis",
    "complex numbers": "complex analysis",
    "group theory": "group theory",
    "algebra": "group theory",
    "topology": "topology",
    "graph theory": "graph theory deep",
    "network theory": "graph theory deep",
    "number theory": "number theory",
    "prime numbers": "number theory",
    "combinatorics": "combinatorics",
    "combinatorics": "combinatorics",
    "chaos": "chaos theory",
    "butterfly effect": "chaos theory",
    "information theory": "information theory",
    "entropy information": "information theory",

    # Biology aliases
    "evolution": "evolution",
    "natural selection": "evolution",
    "ecology": "ecology",
    "ecosystem": "ecology",
    "cell biology": "cell biology",
    "cells": "cell biology",
    "genetics": "genetics deep",
    "dna": "genetics deep",
    "crispr": "genetics deep",
    "molecular biology": "molecular biology",
    "bioinformatics": "bioinformatics",
    "computational biology": "bioinformatics",
    "neuroscience": "neuroscience deep",
    "brain science": "neuroscience deep",
    "immunology": "immunology deep",
    "immune system": "immunology deep",
    "microbiology": "microbiology",
    "bacteria": "microbiology",
    "virology": "virology",
    "virus": "virology",
    "epidemiology": "epidemiology",
    "public health": "epidemiology",

    # Physics aliases
    "string theory": "string theory",
    "quantum gravity": "loop quantum gravity",
    "holographic": "holographic principle",
    "adscft": "holographic principle",
    "dark matter": "dark matter candidates",
    "neutrino": "neutrino",
    "higgs": "higgs boson",
    "higgs boson": "higgs boson",
    "superconductor": "superconductivity",
    "superconductivity": "superconductivity",
    "condensed matter": "condensed matter",
    "solid state physics": "condensed matter",
    "plasma": "plasma physics",
    "ionized gas": "plasma physics",

    # Chemistry aliases
    "chemical bonding": "chemical bonding",
    "ionic bond": "chemical bonding",
    "covalent bond": "chemical bonding",
    "thermochemistry": "thermochemistry",
    "calorimetry": "thermochemistry",
    "electrochemistry": "electrochemistry",
    "battery": "electrochemistry",
    "kinetics": "kinetics",
    "reaction rate": "kinetics",
    "quantum chemistry": "quantum chemistry",
    "computational chemistry": "quantum chemistry",
    "spectroscopy": "spectroscopy",
    "spectrum": "spectroscopy",
    "polymer": "polymer chemistry",
    "plastics": "polymer chemistry",

    # Earth science aliases
    "plate tectonics": "plate tectonics",
    "earthquakes": "plate tectonics",
    "volcanoes": "plate tectonics",
    "weather vs climate": "weather vs climate",
    "climate change": "weather vs climate",
    "oceanography": "oceanography",
    "oceans": "oceanography",
    "geology": "geology",
    "rocks": "geology",
    "paleontology": "paleontology",
    "fossils": "paleontology",
    "dinosaurs": "paleontology",
    "atmosphere": "atmospheric science",
    "weather": "atmospheric science",

    # Economics aliases
    "micro": "microeconomics",
    "microeconomics": "microeconomics",
    "macro": "macroeconomics",
    "macroeconomics": "macroeconomics",
    "behavioral economics": "behavioral economics",
    "nudge": "behavioral economics",
    "game theory": "game theory economics",
    "financial markets": "financial markets",
    "stock market": "financial markets",
    "accounting": "accounting",
    "supply chain management": "supply chain",
    "logistics": "supply chain",

    # Law aliases
    "constitutional law": "constitutional law",
    "constitution": "constitutional law",
    "contract law": "contract law",
    "contracts": "contract law",
    "intellectual property": "intellectual property",
    "patent": "intellectual property",
    "copyright": "intellectual property",
    "trademark": "intellectual property",
    "tort law": "tort law",
    "torts": "tort law",
    "criminal law": "criminal law",
    "criminology": "criminal law",

    # Philosophy aliases
    "existentialism": "existentialism",
    "sartre": "existentialism",
    "camus": "existentialism",
    "utilitarianism": "utilitarianism",
    "bentham": "utilitarianism",
    "mill": "utilitarianism",
    "deontology": "deontology",
    "kant": "deontology",
    "virtue ethics": "virtue ethics",
    "aristotle ethics": "virtue ethics",
    "philosophy of mind": "philosophy of mind",
    "mind body problem": "philosophy of mind",
    "epistemology": "epistemology",
    "theory of knowledge": "epistemology",
    "metaphysics": "metaphysics",

    # Art aliases
    "photography": "photography composition",
    "photo composition": "photography composition",
    "film theory": "film theory",
    "cinema": "film theory",
    "graphic design": "graphic design",
    "architecture": "architecture history",
    "interior design": "interior design",

    # Health aliases
    "nutrition": "nutrition science",
    "diet": "nutrition science",
    "exercise": "exercise physiology",
    "fitness": "exercise physiology",
    "workout": "exercise physiology",
    "sleep": "sleep science",
    "insomnia": "sleep science",
    "mental health": "mental health",
    "depression": "mental health",
    "anxiety": "mental health",
    "stress": "stress management",
    "first aid": "first aid",
    "cpr": "first aid",

    # Business aliases
    "project management": "project management",
    "pm": "project management",
    "scrum master": "project management",
    "human resources": "human resources",
    "hr": "human resources",
    "negotiation": "negotiation",
    "negotiate": "negotiation",
    "strategic planning": "strategic planning",
    "strategy": "strategic planning",
    "operations": "operations management",
    "lean": "operations management",
    "six sigma": "operations management",

    # Sociology aliases
    "sociology": "sociology",
    "society": "sociology",
    "anthropology": "anthropology",
    "culture": "anthropology",
    "social movements": "social movements",
    "activism": "social movements",

    # Linguistics aliases
    "phonetics": "phonetics",
    "ipa": "phonetics",
    "syntax": "syntax",
    "grammar": "syntax",
    "semantics": "semantics deep",
    "meaning linguistics": "semantics deep",
    "pragmatics": "pragmatics deep",

    # Tech aliases
    "semiconductor": "semiconductor",
    "chip": "semiconductor",
    "silicon": "semiconductor",
    "telecommunications": "telecommunications",
    "telecom": "telecommunications",
    "5g": "telecommunications",
    "power grid": "power systems",
    "electricity": "power systems",
    "renewable energy technology": "renewable energy tech",
    "solar panel": "renewable energy tech",
    "biomedical": "biomedical engineering",
    "bme": "biomedical engineering",
    "materials science": "materials science deep",
    "aerospace": "aerospace engineering",
    "aviation": "aerospace engineering",

    # Sports aliases
    "weight training": "weight training",
    "lifting": "weight training",
    "strength training": "weight training",
    "cardio": "cardio training",
    "running": "cardio training",
    "yoga": "yoga",
    "martial arts": "martial arts",
    "boxing": "martial arts",
    "bjj": "martial arts",
    "sports nutrition": "sports nutrition",

    # Travel aliases
    "world capitals": "world capitals",
    "continents": "seven continents",
    "religions": "world religions",
    "united nations": "united nations",
    "un": "united nations",

    # Life skills aliases
    "financial literacy": "financial literacy",
    "budgeting": "financial literacy",
    "investing basics": "financial literacy",
    "critical thinking": "critical thinking",
    "media literacy": "media literacy",
    "digital literacy": "digital literacy",
    "cooking": "cooking basics",
    "home repair": "home maintenance",
    "time management": "time management",
    "communication skills": "communication skills",

    # History aliases
    "world war ii": "world war 2",
    "ww2": "world war 2",
    "wwii": "world war 2",
    "cold war": "cold war",
    "renaissance": "renaissance history",
    "industrial revolution": "industrial revolution",
    "ancient rome": "ancient rome",
    "roman empire": "ancient rome",
    "ancient greece": "ancient greece",
    "greeks": "ancient greece",

    # Scientific method aliases
    "scientific method": "scientific method",
    "hypothesis": "scientific method",
    "experiment": "scientific method",
    "experimental design": "experimental design",
    "controlled experiment": "experimental design",
    "data analysis": "data analysis",
    "statistics": "data analysis",
    "research ethics": "research ethics",

    # Emerging tech aliases
    "quantum computing": "quantum computing real",
    "quantum computer": "quantum computing real",
    "gene therapy": "gene therapy",
    "gene editing": "gene therapy",
    "synthetic biology": "synthetic biology",
    "synbio": "synthetic biology",
    "neuromorphic": "neuromorphic computing",
    "brain chip": "brain computer interface",
    "bci": "brain computer interface",
    "neuralink": "brain computer interface",
    "digital twin": "digital twin",
    "edge computing": "edge computing",
    "edge ai": "edge computing",

    # Common knowledge aliases
    "color theory": "color theory",
    "colors": "color theory",
    "optical illusion": "optical illusions",
    "memory technique": "memory palace",
    "memory method": "memory palace",
    "speed reading": "speed reading",
    "mind map": "mind mapping",
    "brainstorming": "mind mapping",
    "debate": "debate techniques",
    "argumentation": "debate techniques",
    "persuasion": "persuasion psychology",
    "influence": "persuasion psychology",
    "negotiation tactics": "negotiation tactics",
}

# ═══════════════════════════════════════════════════════════════════════════
#  ADDITIONAL INTENT PATTERNS
# ═══════════════════════════════════════════════════════════════════════════

EXTRA_INTENT_PATTERNS = {
    "question_explain": [
        (["explain", "what is", "tell me about", "describe", "define"], []),
        (["how does", "how do", "how can", "how would"], []),
    ],
    "question_compare": [
        (["compare", "difference between", "versus", "vs", "better than"], []),
    ],
    "question_why": [
        (["why", "reason for", "cause of", "because"], []),
    ],
    "code_help": [
        (["write code", "write function", "write class", "implement", "code for"], []),
        (["python code", "javascript code", "code example", "code snippet"], []),
    ],
    "learning": [
        (["teach me", "learn about", "explain how", "what should i know"], []),
        (["tutorial", "guide", "how to learn", "study"], []),
    ],
    "creative": [
        (["create", "generate", "write story", "write poem", "imagine"], []),
        (["design", "draw", "make", "build", "craft"], []),
    ],
    "analysis": [
        (["analyze", "analyse", "examine", "evaluate", "assess"], []),
        (["review", "critique", "critically", "deep dive"], []),
    ],
    "planning": [
        (["plan", "strategy", "roadmap", "step by step", "roadmap for"], []),
        (["schedule", "organize", "structure", "approach"], []),
    ],
    "problem_solving": [
        (["solve", "fix", "troubleshoot", "debug", "resolve"], []),
        (["problem", "issue", "error", "bug", "stuck"], []),
    ],
    "opinion": [
        (["opinion", "think about", "your thoughts", "what do you think"], []),
        (["prefer", "recommend", "suggestion", "advice"], []),
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
#  MASSIVE KNOWLEDGE EXPANSION (300+ additional entries)
# ═══════════════════════════════════════════════════════════════════════════

EXTRA_KNOWLEDGE.update({
    # ── ADVANCED AI & DEEP LEARNING ──
    "attention is all you need": "The 2017 paper 'Attention Is All You Need' by Vaswani et al. introduced the Transformer architecture. Key innovation: self-attention replaces recurrence entirely. Enables parallelization, captures long-range dependencies. Foundation of modern LLMs (GPT, BERT, T5, Llama).",
    "word2vec": "Word2Vec (Mikolov et al., 2013) learns word embeddings from large corpora. Two architectures: CBOW (predict word from context) and Skip-gram (predict context from word). Captures semantic relationships: king - man + woman ≈ queen.",
    "glove": "GloVe (Global Vectors for Word Representation, Stanford 2014) builds word embeddings from global co-occurrence statistics. Combines matrix factorization with local context window methods. Good at capturing semantic relationships.",
    "fasttext": "FastText (Facebook 2016) extends Word2Vec by using subword information (character n-grams). Better for rare words, morphologically rich languages, and out-of-vocabulary words. Also does text classification.",
    "seq2seq": "Sequence-to-Sequence (Seq2Seq) models map input sequences to output sequences. Encoder-decoder architecture. Encoder processes input into fixed-length vector, decoder generates output. Used in: translation, summarization, dialogue.",
    "beam search": "Beam search is a decoding strategy for sequence models. Keeps top-k (beam width) candidates at each step. More diverse than greedy decoding, less expensive than exhaustive search. Used in translation, captioning, LLMs.",
    "top-k sampling": "Top-k sampling limits token selection to k most probable tokens. Controls randomness in text generation. Lower k = more focused, higher k = more diverse. Used in GPT-style generation.",
    "temperature scaling": "Temperature scaling adjusts softmax probability distribution. T < 1: more focused/deterministic. T > 1: more random/creative. T = 1: original distribution. Critical parameter for LLM generation quality.",
    "perplexity": "Perplexity measures how well a language model predicts text. Lower = better. Formula: PP(W) = P(w1,w2,...wn)^(-1/n). Typical range: 20-100 for modern LLMs. Used to evaluate and compare language models.",
    "tokenization": "Tokenization splits text into tokens for model input. Types: word-level, subword (BPE, WordPiece, SentencePiece), character-level. BPE (Byte Pair Encoding) is most common. GPT uses tiktoken. Affects model vocabulary and performance.",
    "bpe": "Byte Pair Encoding (BPE) is a subword tokenization algorithm. Starts with characters, iteratively merges most frequent pairs. Balances vocabulary size with sequence length. Used by GPT, Llama, most modern LLMs.",
    "positional encoding": "Positional encoding injects sequence order information into transformers. Sinusoidal (fixed) or learned embeddings. Without it, transformers are permutation-invariant. RoPE (Rotary Position Embeddings) and ALiBi are modern alternatives.",
    "layer normalization": "Layer normalization normalizes across features for each sample. Stabilizes training, reduces internal covariate shift. Applied before or after attention/FFN layers. Alternative: batch normalization (normalizes across batch).",
    "residual connection": "Residual connections (skip connections) add input directly to layer output: y = F(x) + x. Enables training of very deep networks by mitigating vanishing gradients. Introduced in ResNet (He et al., 2015).",
    "dropout": "Dropout randomly zeros neurons during training (typically p=0.1-0.5). Prevents co-adaptation, acts as ensemble regularization. At inference, all neurons active (scaled). Foundational regularization technique.",
    "batch normalization": "Batch normalization normalizes layer inputs across the batch dimension. Reduces internal covariate shift, enables higher learning rates. Controversial for transformers (layer norm preferred).",
    "knowledge distillation": "Knowledge distillation trains a smaller (student) model to mimic a larger (teacher) model. Uses soft probability targets. Enables deployment on edge devices. Examples: DistilBERT, TinyLlama.",
    "pruning": "Pruning removes redundant weights/neurons from neural networks. Structured (remove entire neurons) or unstructured (individual weights). Can reduce model size 50-90% with minimal accuracy loss.",
    "quantization": "Quantization reduces model precision (FP32 → INT8/INT4). Reduces memory and compute. Types: dynamic, static, quantization-aware training. Enables running large models on consumer hardware. GPTQ, AWQ, GGUF formats.",
    "lora": "LoRA (Low-Rank Adaptation, Hu et al. 2021) fine-tunes LLMs by adding low-rank decomposition matrices to attention layers. Freezes original model, trains small adapter. Reduces trainable parameters by 10,000x. QLoRA adds quantization.",
    "qlora": "QLoRA (Dettmers et al. 2023) combines 4-bit quantization with LoRA. Enables fine-tuning 65B models on single 48GB GPU. Uses NF4 (Normal Float 4-bit) quantization with double quantization. Memory efficient.",
    "flash attention": "Flash Attention (Dao et al. 2022) computes exact attention using tiling and kernel fusion. Reduces memory from O(N²) to O(N). 2-4x faster than standard attention. IO-aware: optimizes for GPU memory hierarchy.",
    "mixture of experts deep": "Mixture of Experts (MoE) uses multiple expert FFN layers with a gating network. Only top-k experts activate per token. Enables scaling model capacity without proportional compute. GPT-4 reportedly uses MoE.",
    "sparse attention": "Sparse attention reduces attention complexity from O(N²) to O(N√N) or O(NlogN). Patterns: local (window), global, strided, random. BigBird, Longformer use combinations. Enables longer context windows.",
    "ring attention": "Ring Attention distributes long sequences across devices in a ring topology. Each device processes a block, passes keys/values to next. Enables context lengths of millions of tokens. Used in Gemini, Claude.",
    "mamba": "Mamba (Gu & Dao, 2023) is a state-space model (SSM) with selective gating. Linear-time sequence modeling (vs quadratic for transformers). Hardware-efficient. Competitive with transformers at scale. Alternatives to transformer dominance.",

    # ── ROBOTICS & AUTOMATION ──
    "robotics": "Robotics combines engineering, AI, and computer science to build robots. Key: kinematics (motion), dynamics (forces), control (feedback), perception (sensors), planning (pathfinding). Applications: manufacturing, surgery, exploration, service.",
    "ros": "ROS (Robot Operating System) provides middleware for robotics development. Libraries: navigation, manipulation, perception, simulation. Not an OS but a framework. ROS2 is the modern rewrite with DDS real-time communication.",
    "slam": "SLAM (Simultaneous Localization and Mapping) builds maps while localizing a robot within them. Algorithms: EKF-SLAM, FastSLAM, ORB-SLAM. Uses LIDAR, cameras, IMU. Essential for autonomous navigation.",
    "inverse kinematics": "Inverse kinematics computes joint angles for desired end-effector position/orientation. Analytical (closed-form) or numerical (iterative) solutions. Essential for robot arm control, animation, gaming.",
    "pid controller": "PID controller combines proportional, integral, derivative terms for feedback control. P: reacts to current error. I: eliminates steady-state error. D: dampens oscillations. Most common control algorithm in industry.",
    "path planning": "Path planning finds optimal routes for robots/agents. Algorithms: A* (heuristic), RRT (rapidly-exploring random trees), PRM (probabilistic roadmaps), D* (dynamic). Considers obstacles, kinematics, optimization criteria.",
    "computer vision robotics": "Computer vision for robots: object detection (YOLO, SSD), segmentation (Mask R-CNN), depth estimation, optical flow, visual odometry. Enables robots to perceive and interact with environments.",

    # ── GAME DEVELOPMENT ──
    "game engine": "Game engines provide frameworks for game development. Core: rendering (OpenGL, Vulkan, DirectX), physics (Box2D, PhysX), audio, input, scripting. Major: Unity (C#), Unreal (C++/Blueprints), Godot (GDScript), GameMaker.",
    "game physics": "Game physics simulates real-world mechanics. Rigid body dynamics, collision detection (AABB, GJK), constraints, ragdoll, fluid simulation. Libraries: PhysX, Bullet, Box2D. Balance realism vs performance.",
    "game ai": "Game AI creates intelligent NPC behavior. Techniques: finite state machines, behavior trees, utility AI, GOAP (Goal-Oriented Action Planning), neural networks, MCTS (Monte Carlo Tree Search). Pathfinding: A*, Dijkstra.",
    "procedural generation": "Procedural generation creates content algorithmically. Terrain: Perlin noise, Voronoi diagrams. Dungeons: BSP trees, wave function collapse. Assets: L-systems for vegetation. Used in: No Man's Sky, Minecraft, roguelikes.",
    "game networking": "Game networking handles multiplayer synchronization. Models: peer-to-peer, client-server, listen server. Techniques: state synchronization, client-side prediction, server reconciliation, entity interpolation. Protocols: UDP, WebSocket.",
    "rendering pipeline": "Rendering pipeline transforms 3D scene to 2D image. Stages: vertex processing, rasterization, fragment processing. Forward rendering, deferred rendering, tiled rendering. Modern: ray tracing, path tracing for realism.",
    "shader": "Shaders are programs that run on GPU. Vertex shaders transform geometry. Fragment/pixel shaders compute colors. Compute shaders do general computation. Languages: GLSL, HLSL, WGSL. Enable complex visual effects.",
    "collision detection": "Collision detection determines if objects intersect. Broad phase: spatial hashing, quadtrees, BVH. Narrow phase: GJK, SAT, EPA. Continuous: sweep and prune. Critical for games, simulation, physics engines.",

    # ── MUSIC THEORY & AUDIO ──
    "music theory": "Music theory studies music fundamentals. Elements: pitch, rhythm, melody, harmony, texture, form. Scales: major, minor, pentatonic, chromatic. Intervals: unison to octave. Chords: triads, seventh, extended. Keys and modulation.",
    "harmony": "Harmony combines simultaneous pitches. Chord progressions: I-IV-V-I (classical), I-V-vi-IV (pop). Tension and resolution. Consonance vs dissonance. Functional harmony: tonic, subdominant, dominant. Modal interchange.",
    "rhythm": "Rhythm is pattern of sounds in time. Meter: simple (2/4, 3/4, 4/4) or compound (6/8, 9/8, 12/8). Tempo: BPM (beats per minute). Syncopation: off-beat accents. Polyrhythm: multiple conflicting rhythms.",
    "composition": "Composition is creating music. Process: melody creation, harmonic accompaniment, orchestration, arrangement. Forms: verse-chorus, AABA, sonata, rondo. Techniques: motif development, variation, counterpoint.",
    "sound design": "Sound design creates audio elements. Synthesis: subtractive, FM, wavetable, granular. Sampling: manipulation of recorded sounds. Effects: reverb, delay, chorus, distortion, compression. Used in music, film, games.",
    "audio engineering": "Audio engineering records, mixes, and masters music. Mixing: balancing levels, panning, EQ, compression, effects. Mastering: final polish, loudness optimization, format conversion. DAWs: Pro Tools, Ableton, Logic.",

    # ── ADVANCED MATHEMATICS ──
    "differential equations": "Differential equations describe rates of change. ODE: single variable. PDE: multiple variables. Methods: separation of variables, integrating factors, Laplace transforms, numerical (Euler, Runge-Kutta). Used in physics, engineering, biology.",
    "fourier transform": "Fourier transform decomposes signals into frequency components. F(ω) = ∫f(t)e^(-iωt)dt. Reveals frequency content of signals. Applications: audio processing, image filtering, quantum mechanics, data compression.",
    "laplace transform": "Laplace transform converts time-domain to s-domain: F(s) = ∫f(t)e^(-st)dt. Simplifies differential equations to algebraic. Inverse transform returns to time domain. Essential for control systems, circuit analysis.",
    "complex analysis": "Complex analysis studies functions of complex numbers. Key: analytic functions, Cauchy-Riemann equations, contour integration, residue theorem. Beautiful theory with applications in physics, engineering, number theory.",
    "group theory": "Group theory studies algebraic structures with composition operation. Properties: closure, associativity, identity, inverse. Examples: integers under addition, permutations, symmetries. Applications: physics, chemistry, cryptography.",
    "topology": "Topology studies properties preserved under continuous deformation. Key concepts: homeomorphism, connectedness, compactness, genus, Euler characteristic. Applications: data analysis (persistent homology), physics (topological insulators).",
    "graph theory deep": "Graph theory studies networks. Concepts: connectivity, planarity, coloring, flows, matching. Algorithms: max-flow min-cut, graph isomorphism, community detection. Applications: social networks, biology, logistics.",
    "number theory": "Number theory studies integers. Primes, divisibility, congruences, Diophantine equations. Fermat's Last Theorem (proved 1995). Applications: cryptography (RSA relies on factoring difficulty).",
    "combinatorics": "Combinatorics counts arrangements. Permutations (order matters), combinations (order doesn't). Binomial coefficients, Catalan numbers, generating functions. Applications: probability, algorithm analysis, coding theory.",
    "chaos theory": "Chaos theory studies sensitive dependence on initial conditions. Lorenz attractor, butterfly effect. Lyapunov exponents measure chaos. Applications: weather forecasting, population dynamics, cryptography.",
    "information theory": "Information theory quantifies information. Entropy H(X) = -∑p(x)log p(x). Mutual information measures dependence. Channel capacity: maximum reliable communication rate. Foundation of compression, coding, ML.",

    # ── BIOLOGY & LIFE SCIENCES ──
    "evolution": "Evolution by natural selection (Darwin 1859). Mechanisms: mutation (variation), selection (differential survival), drift (random changes), gene flow. Evidence: fossil record, DNA, comparative anatomy, biogeography.",
    "ecology": "Ecology studies organism-environment interactions. Levels: organism, population, community, ecosystem, biosphere. Concepts: food webs, nutrient cycling, succession, biodiversity, carrying capacity.",
    "cell biology": "Cell biology studies cell structure and function. Eukaryotic: nucleus, mitochondria, ER, Golgi, lysosomes. Prokaryotic: no membrane-bound organelles. Cell cycle: G1, S, G2, mitosis. Membrane: phospholipid bilayer.",
    "genetics deep": "Genetics studies heredity. Mendelian: dominant/recessive, segregation, independent assortment. Molecular: DNA replication, transcription, translation. Modern: CRISPR, gene drives, epigenetics. Quantitative: polygenic traits.",
    "molecular biology": "Molecular biology studies biomolecules. DNA: double helix, base pairing. RNA: messenger, transfer, ribosomal. Proteins: structure (primary to quaternary), function. Central dogma: DNA → RNA → protein.",
    "bioinformatics": "Bioinformatics applies computing to biology. Sequence alignment (BLAST), genome assembly, phylogenetics, protein structure prediction (AlphaFold). Tools: BioPython, R (Bioconductor), Galaxy. Big data in biology.",
    "neuroscience deep": "Neuroscience studies the nervous system. Levels: molecular, cellular, systems, cognitive, computational. Brain mapping: connectome project. Techniques: fMRI, EEG, optogenetics, patch clamp. Consciousness remains unsolved.",
    "immunology deep": "Immunology studies immune responses. Innate: barriers, complement, phagocytes, NK cells. Adaptive: T cells (cell-mediated), B cells (humoral/antibodies). Immunological memory: basis of vaccination.",
    "microbiology": "Microbiology studies microorganisms. Bacteria, archaea, fungi, protists, viruses. Methods: culturing, microscopy, PCR, sequencing. Applications: medicine (antibiotics), biotechnology (fermentation), ecology.",
    "virology": "Virology studies viruses. Structure: nucleic acid core + protein coat (+ envelope). Replication: lytic vs lysogenic cycles. COVID-19: SARS-CoV-2, RNA virus, spike protein. Vaccines: mRNA, viral vector, protein subunit.",
    "epidemiology": "Epidemiology studies disease distribution and determinants. Measures: incidence, prevalence, mortality, morbidity. Study designs: cohort, case-control, cross-sectional, randomized controlled trial. R0, herd immunity.",

    # ── ADVANCED PHYSICS ──
    "string theory": "String theory proposes fundamental objects are 1D strings, not 0D points. Requires 10 or 11 dimensions. Five consistent theories unified by M-theory. Promising framework for quantum gravity. Unfalsifiable currently.",
    "loop quantum gravity": "Loop quantum gravity quantizes spacetime itself. Space is discrete: spin networks. Spacetime: spin foams. Area and volume have minimum values. Background independent. Alternative to string theory.",
    "holographic principle": "Holographic principle: information in a volume encoded on its boundary. AdS/CFT correspondence: gravity in anti-de Sitter space equivalent to conformal field theory on boundary. Profound for quantum gravity.",
    "dark matter candidates": "Dark matter candidates: WIMPs (weakly interacting massive particles), axions (hypothetical light particles), sterile neutrinos, primordial black holes, self-interacting dark matter. Direct detection experiments ongoing.",
    "neutrino": "Neutrinos are light, weakly interacting particles. Three flavors: electron, muon, tau. Oscillate between flavors (has mass). Trillions pass through you per second. Detected: Super-Kamiokande, IceCube.",
    "higgs boson": "Higgs boson (discovered 2012, CERN) gives mass to W and Z bosons via Higgs mechanism. Scalar boson (spin 0). Mass: 125 GeV/c². Confirms Standard Model. Higgs field permeates all space.",
    "superconductivity": "Superconductivity: zero electrical resistance below critical temperature. Type I (abrupt) and Type II (mixed state). BCS theory: Cooper pairs. High-temperature superconductors (cuprates). Room-temp goal: holy grail.",
    "condensed matter": "Condensed matter studies solid/liquid matter. Phases: crystal, amorphous, liquid crystal, Bose-Einstein condensate. Emergent phenomena: superconductivity, magnetism, topological states. Largest branch of physics.",
    "plasma physics": "Plasma is ionized gas (4th state of matter). Makes up 99% of visible universe. Properties: conducts electricity, responds to magnetic fields. Examples: stars, lightning, fusion reactors. Described by MHD equations.",

    # ── CHEMISTRY DEEP ──
    "chemical bonding": "Chemical bonding: ionic (electron transfer), covalent (electron sharing), metallic (electron sea). Bond polarity: electronegativity difference. Molecular geometry: VSEPR theory. Hydrogen bonds: intermolecular.",
    "thermochemistry": "Thermochemistry studies heat in chemical reactions. Exothermic (releases heat), endothermic (absorbs). Hess's law: total ΔH independent of path. Enthalpy, entropy, Gibbs free energy determine spontaneity.",
    "electrochemistry": "Electrochemistry studies electricity-chemistry interface. Galvanic cells (spontaneous, batteries), electrolytic cells (non-spontaneous, plating). Nernst equation relates voltage to concentration. Applications: batteries, corrosion.",
    "kinetics": "Chemical kinetics studies reaction rates. Rate law: rate = k[A]^m[B]^n. Factors: concentration, temperature, catalysts, surface area. Arrhenius equation: k = Ae^(-Ea/RT). Activation energy determines rate.",
    "quantum chemistry": "Quantum chemistry applies quantum mechanics to molecules. Schrödinger equation for molecular systems. Methods: Hartree-Fock, DFT (density functional theory), post-HF (MP2, CCSD). Predicts molecular properties.",
    "spectroscopy": "Spectroscopy studies matter-light interactions. Types: UV-Vis (electronic transitions), IR (vibrations), NMR (nuclear spins), MS (mass), Raman. Used for: identification, structure determination, quantitative analysis.",
    "polymer chemistry": "Polymer chemistry studies large molecules made of repeating monomers. Types: addition (chain-growth), condensation (step-growth). Properties: molecular weight, crystallinity, glass transition. Applications: plastics, fibers, rubber.",

    # ── EARTH & ENVIRONMENTAL SCIENCE ──
    "plate tectonics": "Plate tectonics: Earth's lithosphere divided into plates moving on asthenosphere. Boundaries: divergent (mid-ocean ridges), convergent (subduction, mountains), transform (faults). Causes earthquakes, volcanism.",
    "weather vs climate": "Weather: short-term atmospheric conditions (days-weeks). Climate: long-term averages (30+ years). Weather prediction: chaotic, limited to ~10 days. Climate models: project decades-centuries. Global warming: climate change.",
    "oceanography": "Oceanography studies oceans. Circulation: thermohaline (global conveyor belt), surface currents. Zones: pelagic, benthic, aphotic. Marine ecosystems: coral reefs, hydrothermal vents. Rising seas from warming.",
    "geology": "Geology studies Earth's structure and history. Layers: crust, mantle, outer core, inner core. Rock types: igneous, sedimentary, metamorphic. Geologic time: 4.6 billion years. Plate tectonics shapes surface.",
    "paleontology": "Paleontology studies ancient life through fossils. Methods: stratigraphy, radiometric dating, comparative anatomy, molecular phylogenetics. Key discoveries: dinosaurs, hominins, mass extinctions. Citizen science: fossil hunting.",
    "atmospheric science": "Atmospheric science studies atmosphere. Composition: 78% N₂, 21% O₂, 1% Ar, CO₂ trace. Layers: troposphere, stratosphere, mesosphere, thermosphere. Weather, ozone depletion, air quality.",

    # ── ECONOMICS & FINANCE DEEP ──
    "microeconomics": "Microeconomics studies individual agents. Supply and demand, elasticity, utility maximization, profit maximization. Market structures: perfect competition, monopoly, oligopoly, monopolistic competition. Externalities.",
    "macroeconomics": "Macroeconomics studies economy-wide phenomena. GDP, inflation, unemployment, monetary policy (central banks), fiscal policy (government). Business cycles: expansion, peak, recession, trough. Keynesian vs classical.",
    "behavioral economics": "Behavioral economics combines psychology and economics. Bounded rationality, heuristics, biases (anchoring, loss aversion, endowment effect). Nudges influence decisions. Prospect theory (Kahneman & Tversky).",
    "game theory economics": "Game theory studies strategic interactions. Nash equilibrium: no player benefits from unilateral deviation. Prisoner's dilemma, coordination games, auction theory. Applications: economics, politics, biology.",
    "financial markets": "Financial markets trade assets. Stock market (equities), bond market (debt), forex (currencies), derivatives (options, futures). Efficient market hypothesis. Capital Asset Pricing Model (CAPM).",
    "accounting": "Accounting records financial transactions. Financial accounting: balance sheet, income statement, cash flow. Managerial: cost analysis, budgeting. Double-entry bookkeeping. GAAP and IFRS standards.",
    "supply chain": "Supply chain management coordinates flow from raw materials to end customer. Planning, sourcing, manufacturing, delivery, returns. Lean manufacturing, just-in-time,六西格玛. Disruptions: COVID revealed fragility.",

    # ── LAW & GOVERNANCE ──
    "constitutional law": "Constitutional law interprets constitutions. Separation of powers, checks and balances, judicial review (Marbury v. Madison), federalism, individual rights. Constitutional amendments process.",
    "contract law": "Contract law governs agreements. Elements: offer, acceptance, consideration, capacity, legality. Breach types: material, minor. Remedies: damages, specific performance. UCC for goods, common law for services.",
    "intellectual property": "Intellectual property protects creations. Patents (20 years, inventions), copyrights (life + 70 years, original works), trademarks (brand names), trade secrets (confidential info). Fair use doctrine.",
    "tort law": "Tort law addresses civil wrongs. Negligence: duty, breach, causation, damages. Strict liability, intentional torts (assault, defamation). Products liability. Class action lawsuits. Damages: compensatory, punitive.",
    "criminal law": "Criminal law punishes offenses. Elements: actus reus (guilty act), mens rea (guilty mind). Burden: prosecution must prove beyond reasonable doubt. Defenses: self-defense, insanity, duress. Sentencing guidelines.",

    # ── PHILOSOPHY & ETHICS DEEP ──
    "existentialism": "Existentialism emphasizes individual existence, freedom, choice. Key thinkers: Kierkegaard, Nietzsche, Heidegger, Sartre, Camus. 'Existence precedes essence.' Authenticity, angst, absurdity, being-toward-death.",
    "utilitarianism": "Utilitarianism: actions right if maximizing overall happiness. Bentham: quantitative pleasure. Mill: qualitative pleasures. Variants: act, rule, preference. Criticisms: justice, rights, measurement problem.",
    "deontology": "Deontology: actions judged by adherence to rules/duties. Kant: categorical imperative (act only on universalizable maxims). Moral absolutes. Criticisms: conflicts between duties, consequences ignored.",
    "virtue ethics": "Virtue ethics: character-based morality. Aristotle: eudaimonia through virtues (courage, temperance, justice, wisdom). Mean between extremes. Modern: care ethics, moral particularism.",
    "philosophy of mind": "Philosophy of mind studies consciousness and mental states. Mind-body problem: dualism vs physicalism. Qualia, intentionality, mental causation. Chinese room argument (Searle). Hard problem of consciousness (Chalmers).",
    "epistemology": "Epistemology studies knowledge. Justified true belief (JTB). Gettier problems challenge JTB. Sources: perception, reason, memory, testimony. A priori vs a posteriori. Skepticism, pragmatism, coherentism.",
    "metaphysics": "Metaphysics studies reality. Ontology: what exists? Identity over time (Ship of Theseus), personal identity, free will vs determinism, possible worlds (Lewis). Mind-body problem, causation, time.",

    # ── ART & CULTURE DEEP ──
    "photography composition": "Photography composition: rule of thirds, golden ratio, leading lines, framing, symmetry, negative space, fill the frame, depth of field. Lighting: natural, golden hour, blue hour, studio, Rembrandt.",
    "film theory": "Film theory analyzes cinema. Approaches: formalist (mise-en-scène), psychoanalytic (Lacan, Mulvey), cognitive, ideological (Althusser). Auteur theory. French New Wave, Italian Neorealism.",
    "graphic design": "Graphic design communicates visually. Principles: hierarchy, contrast, alignment, repetition, proximity, white space. Typography: fonts, kerning, leading. Color theory. Tools: Figma, Adobe Creative Suite.",
    "architecture history": "Architecture history: Egyptian (pyramids), Greek (orders), Roman (arches, concrete), Gothic (flying buttresses), Renaissance (symmetry), Baroque (ornate), Modernist (form follows function), Postmodern.",
    "interior design": "Interior design plans interior spaces. Principles: balance, rhythm, emphasis, proportion, harmony. Styles: minimalist, industrial, Scandinavian, mid-century modern, bohemian. Color psychology.",

    # ── HEALTH & WELLNESS DEEP ──
    "nutrition science": "Nutrition science: macronutrients (carbs, proteins, fats), micronutrients (vitamins, minerals), water. RDAs, bioavailability, absorption. Diet types: Mediterranean, DASH, ketogenic, intermittent fasting.",
    "exercise physiology": "Exercise physiology: aerobic vs anaerobic metabolism, VO2 max, muscle fiber types (slow/fast twitch), progressive overload, recovery. Benefits: cardiovascular, metabolic, neurological, psychological.",
    "sleep science": "Sleep science: stages (N1, N2, N3/deep, REM), circadian rhythm, sleep cycles. Adults need 7-9 hours. Dehealth effects: cognitive decline, immune suppression, weight gain. Sleep hygiene practices.",
    "mental health": "Mental health: psychological wellbeing. Disorders: depression, anxiety, PTSD, bipolar, schizophrenia. Treatments: CBT, medication, mindfulness, therapy. Stigma reduction important. Self-care practices.",
    "stress management": "Stress management techniques: mindfulness meditation, deep breathing, progressive muscle relaxation, exercise, time management, social support, cognitive reframing. Chronic stress: health risks.",
    "first aid": "First aid basics: DR ABC (Danger, Response, Airway, Breathing, Circulation). CPR: 30 compressions : 2 breaths. Recovery position. AED use. Choking: Heimlich maneuver. Burns: cool with water.",

    # ── BUSINESS & MANAGEMENT DEEP ──
    "project management": "Project management: planning, executing, closing projects. Methodologies: Waterfall (sequential), Agile (iterative), Scrum (sprints), Kanban (visual flow). Tools: Jira, Asana, Trello. PMP certification.",
    "human resources": "Human resources manages workforce. Functions: recruitment, onboarding, training, performance management, compensation, compliance, employee relations. HRIS systems. Labor laws and regulations.",
    "negotiation": "Negotiation reaches agreements. Styles: competitive, collaborative (win-win), compromising, avoiding, accommodating.BATNA (best alternative). Active listening, anchoring, framing. Harvard method.",
    "strategic planning": "Strategic planning sets long-term direction. Tools: SWOT analysis, PESTEL, Porter's Five Forces, balanced scorecard. Mission, vision, values. Strategic goals → objectives → initiatives → KPIs.",
    "operations management": "Operations management designs and controls processes. Lean, Six Sigma, TQM. Capacity planning, inventory management (EOQ, JIT), quality control (SPC). Supply chain optimization.",

    # ── SOCIOLOGY & ANTHROPOLOGY ──
    "sociology": "Sociology studies society and social behavior. Concepts: social structure, stratification, institutions, culture, deviance, social change. Theories: functionalism, conflict theory, symbolic interactionism.",
    "anthropology": "Anthropology studies human societies and cultures. Branches: cultural, linguistic, archaeology, biological. Methods: ethnography, participant observation. Key concepts: culture, kinship, rituals, adaptation.",
    "social movements": "Social movements: collective action for change. Types: reform, revolutionary, resistance, alternative. Stages: emergence, coalescence, bureaucracy, decline. Examples: civil rights, feminism, environmental.",

    # ── LINGUISTICS DEEP ──
    "phonetics": "Phonetics studies speech sounds. Articulatory: place, manner, voicing of consonants. Vowels: height, backness, rounding. IPA (International Phonetic Alphabet) transcribes all languages.",
    "syntax": "Syntax studies sentence structure. Phrase structure rules, transformational grammar (Chomsky). Constituents, movement, theta-roles. Universal grammar hypothesis. Dependency grammar.",
    "semantics deep": "Semantics studies meaning. Lexical semantics: word meaning, senses, relations (synonymy, antonymy, hyponymy). Compositional semantics: how meaning builds from parts. Truth conditions, entailment.",
    "pragmatics deep": "Pragmatics studies context-dependent meaning. Gricean maxims (quantity, quality, relevance, manner). Speech acts (assertion, request, promise). Implicature, presupposition, reference.",

    # ── TECHNOLOGY & ENGINEERING DEEP ──
    "semiconductor": "Semiconductors conduct between conductors and insulators. Silicon-based. Doping: n-type (excess electrons), p-type (holes). Transistors: MOSFET scaling. Moore's law slowing. New materials: GaN, SiC.",
    "telecommunications": "Telecommunications: transmission of information. Modulation: AM, FM, digital. Multiplexing: FDMA, TDMA, CDMA, OFDMA. 5G: mmWave, massive MIMO, network slicing. Fiber optics: high bandwidth.",
    "power systems": "Power systems generate, transmit, distribute electricity. Generation: thermal, hydro, nuclear, renewable. Transmission: high voltage AC/DC. Grid: interconnected networks. Smart grid: digital optimization.",
    "renewable energy tech": "Renewable energy: solar PV (photovoltaic effect), wind (turbines), hydro (dams), geothermal (heat pumps), tidal (barrages). Storage: batteries, pumped hydro, hydrogen. Grid integration challenges.",
    "biomedical engineering": "Biomedical engineering applies engineering to medicine. Devices: pacemakers, prosthetics, imaging (MRI, CT). Tissue engineering, biomaterials, drug delivery. Medical imaging algorithms.",
    "materials science deep": "Materials science studies material properties. Classes: metals, ceramics, polymers, composites. Properties: mechanical, thermal, electrical, optical. Characterization: XRD, SEM, TEM. Nanostructured materials.",
    "aerospace engineering": "Aerospace engineering: aircraft and spacecraft design. Aerodynamics: lift, drag, thrust. Structures: stress analysis, fatigue. Propulsion: jet engines, rockets. Orbital mechanics for space.",

    # ── SPORTS & FITNESS ──
    "weight training": "Weight training: resistance exercise with weights. Principles: progressive overload, specificity, variation, recovery. Programs: bodybuilding (hypertrophy), powerlifting (strength), Olympic lifting (power).",
    "cardio training": "Cardiovascular training: aerobic exercise for heart/lung health. Types: steady-state, interval training (HIIT), circuit training. Target heart rate zones. VO2 max improvement.",
    "yoga": "Yoga: mind-body practice from India. Styles: Hatha (gentle), Vinyasa (flow), Ashtanga (power), Bikram (hot). Benefits: flexibility, strength, balance, stress reduction. Breathing (pranayama) and meditation.",
    "martial arts": "Martial arts: fighting systems for combat/self-defense. Types: striking (boxing, Muay Thai), grappling (BJJ, wrestling), weapons (Kendo), mixed (MMA). Philosophy: discipline, respect, self-improvement.",
    "sports nutrition": "Sports nutrition optimizes athletic performance. Macronutrient timing: protein for recovery, carbs for energy, fats for endurance. Hydration: electrolyte balance. Supplements: creatine, caffeine, protein powder.",

    # ── TRAVEL & GEOGRAPHY ──
    "world capitals": "World capitals: Washington D.C. (USA), London (UK), Paris (France), Berlin (Germany), Tokyo (Japan), Beijing (China), New Delhi (India), Canberra (Australia), Brasilia (Brazil).",
    "seven continents": "Seven continents: Asia (largest, 4.4B people), Africa (2nd largest, 1.4B), North America (580M), South America (430M), Antarctica (no permanent residents), Europe (750M), Oceania (45M).",
    "world religions": "World religions: Christianity (2.4B), Islam (1.9B), Hinduism (1.2B), Buddhism (500M), Sikhism (30M), Judaism (15M). Origins, beliefs, practices vary. Secular/irreligious: 1.2B.",
    "united nations": "United Nations (1945): international organization for peace, cooperation. Bodies: General Assembly, Security Council, ICJ, Secretariat. Agencies: WHO, UNESCO, UNICEF, WFP. 193 member states.",

    # ── PRACTICAL LIFE SKILLS ──
    "financial literacy": "Financial literacy: managing money effectively. Budgeting (50/30/20 rule), emergency fund (3-6 months), investing (diversification, compound interest), debt management (avalanche vs snowball).",
    "critical thinking": "Critical thinking: analyzing information objectively. Steps: identify assumptions, evaluate evidence, consider alternatives, draw conclusions. Logical fallacies: ad hominem, straw man, slippery slope.",
    "media literacy": "Media literacy: analyzing media messages. Skills: source evaluation, bias detection, fact-checking, understanding framing. Misinformation vs disinformation. Lateral reading technique.",
    "digital literacy": "Digital literacy: using technology effectively. Skills: file management, internet safety, privacy, data literacy, basic coding, cloud services. Digital divide: unequal access.",
    "cooking basics": "Cooking basics: knife skills, heat management (sauté, roast, braise, poach), seasoning (salt, acid, fat, heat), food safety (temperatures, cross-contamination). Recipes as guidelines.",
    "home maintenance": "Home maintenance: regular tasks prevent costly repairs. Plumbing: leaky faucets, clogged drains. Electrical: breaker issues, outlet problems. HVAC: filter changes. Roof: gutter cleaning.",
    "time management": "Time management: organizing tasks effectively. Techniques: Eisenhower matrix (urgent/important), Pomodoro (25-min blocks), time blocking, GTD (Getting Things Done). Prioritization key.",
    "communication skills": "Communication skills: conveying information effectively. Verbal: clarity, tone, pace. Nonverbal: body language, eye contact. Written: structure, conciseness. Active listening: focus, understand, respond.",

    # ── HISTORICAL EVENTS & FIGURES ──
    "world war 2": "World War II (1939-1945): deadliest conflict in history. Axis (Germany, Italy, Japan) vs Allies (UK, USSR, USA). Key events: D-Day, atomic bombs, Holocaust. Ended with Allied victory, UN formation.",
    "cold war": "Cold War (1947-1991): US vs USSR ideological struggle. Nuclear arms race, space race, proxy wars. Berlin Wall (fell 1989), Cuban Missile Crisis. Ended with Soviet dissolution.",
    "renaissance history": "Renaissance (14th-17th century): cultural rebirth in Europe. Started in Italy. Key: humanism, art (da Vinci, Michelangelo), science (Galileo), printing press (Gutenberg). Spread across Europe.",
    "industrial revolution": "Industrial Revolution (1760-1840): mechanization of production. Steam engine (Watt), factories, urbanization. Social changes: middle class, labor movements. Second Industrial Revolution: electricity, steel.",
    "ancient rome": "Ancient Rome (753 BC - 476 AD): republic then empire. Contributions: law, engineering (aqueducts, roads), language (Latin), governance. Key figures: Julius Caesar, Augustus, Constantine.",
    "ancient greece": "Ancient Greece (800-146 BC): foundation of Western civilization. Democracy (Athens), philosophy (Socrates, Plato, Aristotle), science (Archimedes), art, Olympics.",

    # ── SCIENTIFIC METHODOLOGY ──
    "scientific method": "Scientific method: systematic approach to knowledge. Steps: observation, hypothesis, prediction, experimentation, analysis, conclusion. Peer review ensures quality. Replication critical.",
    "experimental design": "Experimental design: controlling variables. Independent, dependent, controlled variables. Randomized controlled trials (gold standard). Double-blind studies. Placebo effect control.",
    "data analysis": "Data analysis: inspecting, cleaning, transforming data. Descriptive: summary statistics. Inferential: hypothesis testing, confidence intervals. Visualizations: charts, graphs. Tools: R, Python, Excel.",
    "research ethics": "Research ethics: protecting participants. Informed consent, confidentiality, beneficence, non-maleficence. IRB (Institutional Review Board) oversight. Animal research guidelines.",

    # ── EMERGING TECHNOLOGIES ──
    "quantum computing real": "Quantum computing: processing using quantum phenomena. Qubits in superposition. Quantum advantage demonstrated (Google Sycamore, 2019). Applications: drug discovery, optimization, cryptography. Current: NISQ era.",
    "gene therapy": "Gene therapy: treating diseases by modifying genes. Viral vectors deliver correct genes. Applications: spinal muscular atrophy, inherited blindness, cancer (CAR-T). CRISPR enables precise editing.",
    "synthetic biology": "Synthetic biology engineers biological systems. Design-build-test-learn cycle. Applications: biofuels, pharmaceuticals, materials, computing. CRISPR, directed evolution. Ethical considerations.",
    "neuromorphic computing": "Neuromorphic computing: brain-inspired chips. Spiking neural networks, event-driven processing. Intel Loihi, IBM TrueNorth. Low power, parallel processing. Good for edge AI, sensory processing.",
    "brain computer interface": "Brain-computer interfaces (BCIs) connect brains to computers. Invasive (Neuralink), non-invasive (EEG). Applications: paralysis control, communication, prosthetics. Ethical concerns: privacy, enhancement.",
    "digital twin": "Digital twin: virtual replica of physical system. Real-time data synchronization. Applications: manufacturing optimization, predictive maintenance, urban planning, healthcare simulation.",
    "edge computing": "Edge computing: processing near data source (not cloud). Benefits: low latency, bandwidth savings, privacy. Applications: IoT, autonomous vehicles, industrial IoT. Complements cloud computing.",

    # ── ADDITIONAL COMMON KNOWLEDGE ──
    "color theory": "Color theory: principles of color mixing and visual effects. Primary: red, blue, yellow (RYB) or red, green, blue (RGB). Complementary colors opposite on wheel. Color psychology: red=passion, blue=trust.",
    "optical illusions": "Optical illusions: visual perceptual tricks. Types: literal (physical), physiological (neural), cognitive (assumptions). Müller-Lyer, Ponzo, Ebbinghaus, impossible objects. Reveal brain processing.",
    "memory palace": "Memory palace (method of loci): memorization technique. Associate items with locations in familiar space. Leverages spatial memory. Used by memory champions. Can memorize thousands of items.",
    "speed reading": "Speed reading: techniques to increase reading rate. Methods: reduce subvocalization, expand peripheral vision, chunking, eliminate regression. Trade-off: comprehension often decreases. Practice improves.",
    "mind mapping": "Mind mapping: visual diagram organizing information hierarchically. Central concept → branches → sub-branches. Uses colors, images, keywords. Aids brainstorming, planning, note-taking. Tony Buzan popularized.",
    "debate techniques": "Debate techniques: structured argumentation. Stock issues: inherency, solvency, disadvantage. Cross-examination, rebuttal, summary. Logical reasoning, evidence presentation, persuasive speaking.",
    "persuasion psychology": "Persuasion psychology: influencing attitudes. Cialdini's principles: reciprocity, commitment, social proof, authority, liking, scarcity. Aristotle: ethos (credibility), pathos (emotion), logos (logic).",
    "negotiation tactics": "Negotiation tactics: strategies for agreement. Anchoring: set initial offer. Framing: present options favorably. Mirroring: build rapport. Silence: create pressure. BATNA: know your alternative.",

    # ── COMMON SCIENCE QUESTIONS ──
    "sky is blue": "The sky appears blue due to Rayleigh scattering. Sunlight enters atmosphere and shorter blue wavelengths scatter more than other colors (scattering ∝ 1/λ⁴). At sunset, light travels through more atmosphere, scattering blue away, leaving red/orange.",
    "gravity": "Gravity is the force of attraction between masses. Newton: F = GMm/r². Einstein: curvature of spacetime by mass-energy. Gravitational waves detected 2015 (LIGO). Weakest fundamental force but infinite range.",
    "speed of light": "Speed of light in vacuum: c = 299,792,458 m/s (exact). Universal speed limit. Nothing with mass can reach c. E = mc² relates mass to energy. Light slows in media (glass: ~200,000 km/s).",
    "why do we dream": "Dreams occur mainly during REM sleep. Theories: memory consolidation, emotional processing, threat simulation, neural noise, default mode network activation. Lucid dreaming: awareness within dreams. Function still debated.",
    "how do vaccines work": "Vaccines train immune system to recognize pathogens without causing disease. Live-attenuated (weakened), inactivated (killed), subunit (pieces), mRNA (instruct cells to make protein). Herd immunity: ~70-95% vaccination rate.",
    "what is dna": "DNA (deoxyribonucleic acid) stores genetic information as double helix. Bases: A-T, C-G (Chargaff's rules). Human genome: ~3 billion base pairs, ~20,000 genes. DNA → RNA (transcription) → Protein (translation).",
    "how does the internet work": "Internet: global network of networks. Data packetized, routed via TCP/IP. DNS translates domain names to IPs. Fiber optics carry data as light. Protocols: HTTP, SMTP, FTP. ISPs provide access. CDN caches content.",
    "what is climate change": "Climate change: long-term global temperature rise. Causes: greenhouse gases (CO₂, methane, N₂O) trapping heat. Effects: rising seas, extreme weather, ocean acidification, biodiversity loss. Paris Agreement: limit to 1.5°C.",
    "how do computers work": "Computers process information using binary (0s and 1s). CPU executes instructions (fetch-decode-execute cycle). RAM provides fast temporary storage. GPU handles parallel graphics/compute. Transistors: tiny switches on chips.",
    "what is evolution explained simply": "Evolution: species change over time through natural selection. Individuals with traits better suited to environment survive and reproduce more. Over generations, advantageous traits become common. Mechanisms: mutation, selection, drift, gene flow.",
    "how does the brain work": "Brain: ~86 billion neurons connected by ~100 trillion synapses. Neurons fire electrical signals (action potentials). Regions: cortex (thinking), cerebellum (movement), brainstem (vital functions). Neurotransmitters: dopamine, serotonin, GABA.",
    "what is quantum mechanics": "Quantum mechanics describes atomic/subatomic behavior. Principles: wave-particle duality, uncertainty principle, superposition, entanglement. Schrödinger equation governs evolution. Measurements collapse wave function. Copenhagen interpretation.",
    "how do vaccines prevent disease": "Vaccines expose immune system to harmless pathogen components (antigens). B cells produce antibodies. Memory cells remember the antigen. When real pathogen appears, immune response is faster and stronger. Boosters reinforce memory.",
    "what causes earthquakes": "Earthquakes: sudden release of energy in Earth's crust. Cause: tectonic plates sliding past each other (transform), colliding (convergent), or separating (divergent). Energy travels as seismic waves. Richter scale measures magnitude.",
    "how does photosynthesis work": "Photosynthesis: plants convert CO₂ + H₂O + light → glucose + O₂. Light reactions: split water, make ATP/NADPH. Calvin cycle: fix CO₂ into sugar. Chloroplasts contain chlorophyll (absorbs red/blue light, reflects green).",
    "what is black matter": "Dark matter: hypothetical matter that doesn't emit/absorb light but has gravitational effects. Evidence: galaxy rotation curves, gravitational lensing, CMB. Makes up ~27% of universe. Candidates: WIMPs, axions. Not directly detected.",
    "how do stars form": "Stars form from collapsing molecular clouds (mostly hydrogen). Gravity compresses gas, heating until nuclear fusion ignites (proton-proton chain). Main sequence: fusing hydrogen to helium. Mass determines lifespan and fate.",
    "what is the big bang": "Big Bang: universe began ~13.8 billion years ago from hot, dense state. Evidence: CMB radiation, redshift of galaxies, abundance of light elements. Not an explosion in space, but expansion of space itself. Still expanding.",
    "how does electricity work": "Electricity: flow of electrons through conductor. Voltage: pressure pushing electrons. Current: flow rate. Resistance: opposition. Ohm's law: V=IR. AC alternates direction (power lines), DC flows one way (batteries).",
    "what is magnetism": "Magnetism: force from moving electric charges. Electrons spinning and orbiting create magnetic moments. Ferromagnetic materials: aligned domains. Earth's magnetic field: molten iron core. Electromagnetism: Maxwell's equations unify.",
    "how do volcanoes erupt": "Volcanoes: magma (molten rock) reaches surface. Magma rises due to buoyancy. Pressure release causes dissolved gases to expand. Eruption types: effusive (lava flows) vs explosive (pyroclastic flows). Found at plate boundaries.",
    "what causes tides": "Tides: rise and fall of sea levels caused by Moon's and Sun's gravitational pull. High tide: water bulges toward and away from Moon. Spring tides: Sun+Moon aligned (full/new moon). Neap tides: Sun+Moon perpendicular.",
    "how do rainbows form": "Rainbows: light refracts, reflects, and disperses in water droplets. White light enters droplet, refracts (bends), reflects off back, refracts again exiting. Different wavelengths bend at different angles, creating spectrum.",
    "what is the ozone layer": "Ozone layer: stratospheric ozone (O₃) absorbs UV radiation from Sun. Protects life from DNA damage. Thinning caused by CFCs (chlorofluorocarbons). Montreal Protocol (1987) phased out CFCs. Slowly recovering.",
    "how do magnets work": "Magnets: materials with aligned electron spins creating net magnetic field. Ferromagnetic: iron, nickel, cobalt ( domains align). Electromagnets: current through coil creates field. Opposite poles attract, like poles repel.",
    "what is dna replication": "DNA replication: DNA makes copy of itself. Helicase unwinds double helix. Primase adds RNA primers. DNA polymerase synthesizes new strands (5'→3'). Leading strand: continuous. Lagging strand: Okazaki fragments. Proofreading ensures accuracy.",
    "how does the immune system work": "Immune system: defense against pathogens. Innate: immediate, non-specific (skin, phagocytes, inflammation). Adaptive: targeted (B cells make antibodies, T cells kill infected cells). Memory: faster response on re-exposure.",
    "what is natural selection": "Natural selection: differential survival and reproduction based on traits. Variation exists in population. Environment selects for advantageous traits. Over generations, population adapts. Four conditions: variation, heritability, differential fitness, competition.",
    "how do ecosystems work": "Ecosystems: communities interacting with environment. Energy flows: producers → consumers → decomposers. Nutrient cycles: carbon, nitrogen, water. Food webs connect species. Biodiversity increases stability. Disturbances trigger succession.",
    "what is the greenhouse effect": "Greenhouse effect: gases trap heat in atmosphere. Natural: keeps Earth habitable (~33°C warmer). Enhanced: human CO₂/methane emissions increase warming. Main gases: CO₂, H₂O, CH₄, N₂O, O₃. Feedback loops amplify warming.",
    "how do cells divide": "Cell division: mitosis (somatic cells) and meiosis (sex cells). Mitosis: one division → two identical cells. Prophase, metaphase, anaphase, telophase. Meiosis: two divisions → four haploid cells with genetic variation.",
    "what is photosynthesis in detail": "Photosynthesis: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂. Light-dependent reactions: thylakoid membrane, photosystem II, electron transport chain, ATP synthase. Calvin cycle: stroma, Rubisco enzyme fixes CO₂ into G3P.",
    "how does digestion work": "Digestion: mechanical and chemical breakdown. Mouth: amylase (stomach: pepsin, HCl. Small intestine: bile (fats), pancreatic enzymes, brush border enzymes. Absorption: villi increase surface area. Large intestine: water absorption.",
    "what is the structure of an atom": "Atom: nucleus (protons + neutrons) orbited by electrons. Protons: positive charge, define element. Neutrons: neutral, isotopes. Electrons: negative, determine bonding. shells: 2, 8, 18, 32 electrons. Quantum model: probability clouds.",
    "how do vaccines differ": "Vaccine types: live-attenuated (weakened virus, MMR), inactivated (killed, polio IPV), subunit (pieces, hepatitis B), toxoid (inactivated toxin, tetanus), mRNA (Pfizer, Moderna), viral vector (J&J, AstraZeneca).",
    "what is evolution by natural selection": "Evolution by natural selection: organisms with traits better suited to environment survive and reproduce more. Over generations, population changes. Evidence: fossil record, DNA, biogeography, direct observation (bacteria).",
    "how does the water cycle work": "Water cycle: evaporation (sun heats water), condensation (vapor forms clouds), precipitation (rain/snow), collection (oceans, lakes, groundwater). Transpiration from plants. Infiltration into soil. Continuous recycling.",
    "what is the theory of relativity": "Special relativity (1905): speed of light constant, time dilation, length contraction, E=mc². General relativity (1915): gravity as spacetime curvature. Predicted: gravitational waves, black holes, time dilation near massive objects.",
    "how do earthquakes happen": "Earthquakes occur when tectonic plates move suddenly. Stress builds at plate boundaries. When stress exceeds friction, rock slips along fault. Seismic waves radiate from focus (hypocenter). Epicenter: point on surface above focus.",
    "what is the theory of evolution": "Theory of evolution: species change over time through natural selection, genetic drift, mutation, and gene flow. Evidence: fossils, DNA sequences, comparative anatomy, biogeography, observed speciation. Unifying theory of biology.",
})
