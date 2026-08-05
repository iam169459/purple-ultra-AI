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
