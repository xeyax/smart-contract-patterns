# System Design Approaches — Research

Research conducted: 2026-03-06. Landscape of methodologies for designing software systems, with focus on relevance to our q-tree skill.

## Related to q-tree (researched separately)

| Approach | Relevance |
|----------|-----------|
| **Question-Based Architecture Derivation** (Muller et al., 2011) | Direct academic precedent — questions + pattern catalogue → architecture |
| **ADD** (SEI) | Recursive decomposition mirrors our depth-first exploration |
| **ATAM** (SEI) | Sensitivity points + trade-offs → our consistency checker |
| **QAW** (SEI) | Facilitated elicitation → our batch question format |
| **GQM** (Basili) | Goal → questions → metrics hierarchy |
| **Natural Questions in SA** (arXiv 2506.23898, 2025) | Question lifecycle: inception → discussion → decided → re-emerged |
| **Tree of Thoughts** | LLM branching exploration with backtracking |

What we borrowed: sensitivity points, re-emergence, suggested-by-default, dependency ordering.

---

## Classical / Enterprise

### ADD — Attribute-Driven Design (SEI)
Recursive decomposition driven by quality attribute scenarios. Each step: select element → identify ASRs → choose tactic/pattern → verify → decompose further.
- **When:** Systems where NFRs are critical drivers
- **Artifacts:** Quality attribute scenarios, decomposition structures, pattern/tactic rationale
- **+** Systematic, repeatable, links decisions to quality requirements
- **−** Needs well-defined QA scenarios upfront, rigid

### ATAM — Architecture Tradeoff Analysis Method (SEI)
Architecture *evaluation* (not design). Stakeholders analyze scenarios against architecture → reveals trade-offs, sensitivity points, risks.
- **When:** Evaluating existing/proposed architecture
- **Artifacts:** Utility tree, sensitivity/trade-off points, risk catalog
- **+** Structured, reveals hidden trade-offs
- **−** Evaluation only, needs architecture to exist, expensive workshops

### 4+1 View Model (Kruchten, 1995)
Architecture through 5 views: Logical, Process, Development, Physical + Scenarios (use cases).
- **When:** Large enterprise, many stakeholders needing different perspectives
- **Artifacts:** 5 view diagrams, use case models, deployment diagrams
- **+** Multi-perspective, forces thinking about runtime/deployment separately
- **−** Heavyweight, bureaucratic for small teams

### TOGAF
Enterprise architecture framework. ADM (Architecture Development Method) = iterative phases for enterprise-wide architecture.
- **When:** Organization-level transformation, business-IT alignment
- **Artifacts:** Architecture vision, business/data/app/tech architecture docs, governance
- **+** Industry standard EA, comprehensive governance
- **−** Very heavyweight, too abstract for individual system design

### Zachman Framework
Ontology (not methodology) — 6×6 grid: What/How/When/Who/Where/Why × perspectives (executive→implementer).
- **When:** Organizing existing architectural documentation
- **Artifacts:** Classification matrix
- **+** Comprehensive taxonomy
- **−** No process, purely organizational

### DoDAF
US Department of Defense architecture framework. Specific views, products, steps for systems-of-systems.
- **When:** Defense/government mandated
- **−** Extremely heavyweight, impractical outside defense

---

## Modern / Industry Popular

### DDD — Domain-Driven Design (Evans)
Business domain at center. Strategic: bounded contexts, context mapping, ubiquitous language. Tactical: entities, aggregates, domain events.
- **When:** Complex business domains, microservices decomposition
- **Artifacts:** Domain model, bounded context map, ubiquitous language, aggregate definitions
- **+** Aligns software with business, natural microservice boundaries
- **−** Steep learning curve, needs domain experts, overkill for CRUD

### Event Storming (Brandolini)
Workshop: domain events on timeline (sticky notes) → commands → aggregates → policies → bounded contexts.
- **When:** Domain discovery, microservice boundaries, monolith decomposition
- **Artifacts:** Event timeline, aggregates, bounded contexts, hotspots
- **+** Collaborative, accessible to non-tech, fast (hours), reveals unknowns
- **−** Facilitator-dependent, informal notation, needs translation to formal artifacts
- **Relevance to q-tree:** Could be alternative input — events (transactions for smart contracts) → aggregates → questions about boundaries

### C4 Model (Simon Brown)
4 levels of architecture diagrams: Context → Container → Component → Code. "Google Maps for code."
- **When:** Any project needing clear architecture diagrams
- **Artifacts:** Context, Container, Component, Code diagrams
- **+** Easy to learn, 81% use (2025 survey), developer-friendly
- **−** Visualization only, not a design method, keeping diagrams current is #1 challenge

### arc42 (Starke & Hruschka)
12-section documentation template. Process-agnostic, everything optional.
- **When:** Structured architecture documentation for any project
- **Artifacts:** 12 sections: goals, constraints, context, strategy, building blocks, runtime, deployment, cross-cutting, decisions, quality, risks, glossary
- **+** Lightweight, practical, standardized structure
- **−** Template only, no design process

### ADRs — Architecture Decision Records (Nygard, 2011)
Each decision = Markdown file: Title, Status, Context, Decision, Consequences. In version control.
- **When:** Preserving "why" behind decisions, teams with turnover
- **Variants:** MADR (extended with options), Y-Statements (one-sentence format)
- **+** Extremely lightweight, lives with code, captures rationale
- **−** Captures decisions only, no generation/evaluation process

### Hexagonal / Clean / Onion Architecture
Dependency inversion — all deps point inward to core business logic. Ports & adapters (Hexagonal), layers (Onion), entities/use cases (Clean).
- **When:** Strong testability needed, framework independence, multiple delivery mechanisms
- **+** Excellent testability, core logic protected from infra churn
- **−** Over-engineered for CRUD, boilerplate

### CQRS + Event Sourcing
Separate read/write models. State = append-only event sequence. Often combined with event-driven architecture.
- **When:** Audit trails, temporal queries, scaling read/write independently, financial systems
- **+** Full audit trail, temporal queries, independent scaling
- **−** Significant complexity, eventual consistency, overkill for simple apps

---

## Agile / Lightweight

### Risk-Driven Architecture (Fairbanks)
Design effort proportional to risk. Identify risks → select techniques → evaluate risk reduction. "Just enough architecture."
- **When:** Any project. Especially: "how much design upfront?"
- **Artifacts:** Risk register, technique selection rationale
- **+** Scales effort to risk, pragmatic, compatible with agile
- **−** Subjective risk assessment, needs experienced architects
- **Relevance to q-tree:** Could prioritize branches by risk level — deep exploration for high-risk, suggested answers for low-risk

### Evolutionary Architecture (Ford, Parsons, Kua — ThoughtWorks)
Fitness functions (automated tests/metrics) protect architectural characteristics as system evolves. No big upfront design.
- **When:** Mature CI/CD, uncertain requirements, avoiding architecture rot
- **Artifacts:** Fitness functions, dimension definitions, incremental change backlog
- **+** Embraces change, automated governance
- **−** Needs mature CI/CD, hard to define fitness functions for some qualities
- **Relevance to q-tree:** Post-q-tree, generate fitness functions as testable contract invariants

### Strangler Fig (Fowler)
Incremental migration: Transform → Coexist → Eliminate. New services "strangle" the monolith.
- **When:** Monolith to microservices, legacy modernization
- **+** Low risk, continuous delivery during migration
- **−** Strategy only, prolonged dual-system maintenance

### Design Thinking for Architecture
Empathize → Define → Ideate → Prototype → Test, applied to architecture.
- **When:** User-facing products, stakeholder buy-in needed
- **+** Ensures architecture serves real user needs
- **−** Too abstract for deep technical concerns

---

## AI-Assisted (2024-2025)

### LLM-Assisted ADD
LLM guided by ADD methodology to collaboratively produce architecture with human architect.
- **Status:** Academic/experimental (arXiv 2506.22688, June 2025)
- **+** Accelerates drafting, explores more alternatives
- **−** Can produce plausible but incorrect designs, needs validation

### ARLO (Requirements → Architecture via LLM + Optimization)
LLM extracts ASRs from NL requirements → integer linear programming → optimal architecture choice.
- **Status:** New (2024), not battle-tested
- **+** Systematic, uses formal optimization (ILP), grounded in ISO 25010
- **−** Depends on LLM quality, may miss nuances

### MAAD (Multi-Agent Architecture Design)
4 LLM agents: Analyst → Modeler → Designer → Evaluator. End-to-end, NOT interactive.
- **Status:** Published 2025, FSE conference
- **+** Agent decomposition, vector retrieval from authoritative sources
- **−** Not interactive (no human-in-the-loop)
- **Relevance:** Could borrow agent role decomposition as modes in q-tree

### LLM Co-Designer (General Practice)
44% of architects use LLMs (2025 survey) for diagrams, ADRs, "what if" scenarios.
- **+** Massively accelerates documentation
- **−** Code-level bias, struggles with strategic views, confidently wrong

---

## Smart Contract / Blockchain Specific

### OWASP SCSVS
Security verification standard. SCSVS-ARCH for secure design. Smart Contract Top 10 ($1.42B lost, 149 incidents, 2024).
- **When:** Any DeFi protocol. From design phase onward.
- **Artifacts:** Security checklist, threat model, vulnerability assessment
- **+** Practical, grounded in real incidents
- **−** Security-only, not complete system design

### Proxy / Diamond Patterns (EIP-2535)
Transparent, UUPS, Beacon, Diamond proxies. Separate storage/logic/routing for upgradeability.
- **When:** Contracts that will evolve post-deployment
- **+** Enables upgrades in immutable environment, modular
- **−** Security surface (storage collisions, admin keys), complexity

### Formal Verification
Mathematical proofs of correctness. Tools: Certora (SMT/Z3), K Framework, Coq (ConCert), Lean (Clear).
- **When:** High-value DeFi, governance contracts
- **+** Mathematical certainty for specified properties
- **−** Very expensive, specialized expertise, only verifies what you specify

---

## Visual / Collaborative

### Domain Storytelling (Hofer & Schwentner)
Domain experts tell work stories, facilitator draws pictographic diagrams. Immediate visual feedback.
- **When:** Early discovery, building shared understanding, precursor to DDD
- **+** Accessible to non-tech, lightweight, fast
- **−** Not a design method, informal

### Wardley Mapping (Simon Wardley)
Value chain + component evolution (Genesis → Custom → Product → Commodity). Strategic decisions.
- **When:** Build vs buy, technology investments, executive communication
- **+** Unique strategic perspective, reveals where to invest
- **−** Subjective, not implementation-level

### Example Mapping
Colored cards: rules (blue) → examples (green) → questions (red). 30-minute sessions.
- **When:** Story refinement, clarifying requirements
- **+** Extremely lightweight, reveals edge cases fast
- **−** Story-level, not system-level

### Collaborative Software Design (van Kelle et al., Manning 2024)
Integrates Event Storming + Example Mapping + Domain Storytelling + Wardley Mapping into one practice.
- **When:** Complex domains, multi-stakeholder alignment, DDD adoption
- **+** Answers "which method when?", holistic
- **−** Requires familiarity with all techniques, facilitator skill critical

---

## Formal Methods

### TLA+ (Lamport)
Formal specification for concurrent/distributed systems. Model checking with TLC. Used at AWS since 2011 (DynamoDB, S3, EBS).
- **When:** Distributed systems, consensus protocols, concurrency bugs
- **+** Catches 35+ step bugs, proven at AWS scale
- **−** Steep learning curve, doesn't verify implementation matches spec

### Alloy (Jackson, MIT)
Relational logic modeling. Automatic counterexample generation for assertions.
- **When:** Access control, data models, graph/relationship problems
- **+** Automatic counterexamples, visual, more accessible than TLA+
- **−** Less expressive than TLA+, not suited for temporal behavior

### STRIDE (Microsoft)
6 threat categories: Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege. Applied with DFDs.
- **When:** Security architecture review, shift-left security
- **+** Systematic, maps to CIA triad, accessible
- **−** Security only, large threat catalogs, needs updating as architecture evolves

---

## Ideas for Future Integration with q-tree

1. **Event Storming as input** — events (transactions) → aggregates → q-tree questions about contract boundaries
2. **Risk-Driven prioritization** — branch risk level → deep exploration for high-risk, suggested answers for low-risk
3. **Fitness Functions output** — after q-tree, generate testable invariants for contracts
4. **C4 diagrams** — summarizer could produce C4 Context + Container diagrams from resolved tree
5. **STRIDE integration** — consistency checker could apply STRIDE categories to smart contract architecture
