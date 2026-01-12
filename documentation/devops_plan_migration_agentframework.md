# DevOps Plan: FinRobot Modernization & Structural Refactor

## 🚩 EPIC: Architectural Refactor & A2A System Implementation

**Jira Epic**: [FR-1](https://lgcorzo.atlassian.net/browse/FR-1)
**Goal**: Transform the legacy FinRobot system into a production-grade, asynchronous AI Agent platform following the `llmops-python-package` architectural pattern, implementing an **AI-Native Engineering Team** architecture, and migrating from `autogen` to `microsoft/agent-framework`.
**Assignee**: `lgcorzo@gmail.com`
**Start Date**: Jan 20, 2026

---

## 🛠️ Feature 1: LLMOps Package Standardization

**Jira Key**: [FR-2](https://lgcorzo.atlassian.net/browse/FR-2)
**Description**: Standardize the project structure to support scalability, automated testing, and CI/CD best practices.
**Estimated Time**: 3 Days (Jan 20 - Jan 22, 2026)

### 👤 User Story (Feature 1)

_As a DevOps Engineer, I want the FinRobot project to follow the `src` layout and use centralized Pydantic settings, so that I can manage deployments and environment variables consistently across the cluster._

### ✅ Tasks (Feature 1)

- [ ] **T1.1**: Initialize the new package structure under `src/finrobot_team/`.
- [ ] **T1.2**: Author a `pyproject.toml` to manage dependencies (agent-framework, litellm, pydantic-settings).
- [ ] **T1.3**: Implement `src/finrobot_team/settings.py` for environment-specific configuration (LiteLLM endpoints, database URIs).
- [ ] **T1.4**: Setup `confs/` directory for declarative YAML configuration management.

---

## 🤖 Feature 2: Migration to Microsoft AgentFramework

**Jira Key**: [FR-3](https://lgcorzo.atlassian.net/browse/FR-3)
**Description**: Replace the deprecated `autogen` library with the high-performance, asynchronous `microsoft/agent-framework`.
**Estimated Time**: 5 Days (Jan 23 - Jan 29, 2026)

### 👤 User Story (Feature 2)

_As an AI Developer, I want to use the modern `agent-framework` abstractions and specialized roles (Researcher, Reasoner, Critic, Gatekeeper), so that our agents can communicate asynchronously and handle long-horizon engineering tasks._

### ✅ Tasks (Feature 2)

- [ ] **T2.1**: Implement a base `AgentModel` and a specialized `ResearcherAgent` for automated state-of-the-art discovery.
- [ ] **T2.2**: Refactor existing agents into `Reasoner` (Coder) and `Critic` (Evaluator) roles using async patterns.
- [ ] **T2.3**: Map legacy toolsets to the new framework's tool-calling signature.
- [ ] **T2.4**: Implement the `Gatekeeper` agent for semantic novelty judging and archive management.

---

## 📡 Feature 3: Agent-to-Agent (A2A) Communication via LiteLLM

**Jira Key**: [FR-4](https://lgcorzo.atlassian.net/browse/FR-4)
**Description**: Enable secure, direct communication between specialized agents using LiteLLM as the unified security gateway.
**Estimated Time**: 4 Days (Jan 30 - Feb 4, 2026)

### 👤 User Story (Feature 3)

_As a Financial Analyst, I want the Market Analyst agent to directly handover findings to the Reporting agent, so that the report generation is faster and the communication is tracked for audit compliance._

### ✅ Tasks (Feature 3)

- [ ] **T3.1**: Configure LiteLLM for the `llm-apps` namespace to handle internal agent-to-agent traffic.
- [ ] **T3.2**: Implement the `A2ACommunication` pattern to allow direct peer-to-peer message passing.
- [ ] **T3.3**: Inject OpenTelemetry headers in all A2A calls for full observability in **Langfuse**.
- [ ] **T3.4**: Secure all internal communication using **OpenZiti** "Dark" services (no exposed ports).

---

## 🏎️ Feature 4: Declarative Financial Jobs & Tasks

**Jira Key**: [FR-5](https://lgcorzo.atlassian.net/browse/FR-5)
**Description**: Implement a job-based execution model where complex financial workflows are defined in YAML and executed by a runner.
**Estimated Time**: 5 Days (Feb 5 - Feb 11, 2026)

### 👤 User Story (Feature 4)

_As a User, I want to define a "Daily Market Report" job in a YAML file and run it via a single command, so that I can automate repeatable financial workflows without writing new code._

### ✅ Tasks (Feature 4)

- [ ] **T4.1**: Implement `ReportJob` and `ForecasterJob` as **Evolutionary Loops** (MAP-Elites) in `src/finrobot_team/jobs/`.
- [ ] **T4.2**: Implement the `Island Model` for parallel exploration of different financial strategy families.
- [ ] **T4.3**: Integrate `Stateful Memory` with MongoDB for lineage tracking and backtracking in long tasks.
- [ ] **T4.4**: Implement a high-performance `Runner` that manages the evolutionary compute budget.

---

## 📈 Success Metrics & Deployment

| Metric                     | Target                                                              |
| :------------------------- | :------------------------------------------------------------------ |
| **Framework Migration**    | 100% replacement of `autogen` with `agent-framework`.               |
| **Security**               | 0 public listening ports; 100% usage of Sealed Secrets via LiteLLM. |
| **Observability**          | 100% of agent steps traced in Langfuse with tool-call details.      |
| **Operational Efficiency** | < 10 minutes to setup and run a new job type via YAML.              |

---

## 📅 Project Calendar (2026)

| Phase     | Activity                            | Start  | End    |
| :-------- | :---------------------------------- | :----- | :----- |
| **P1**    | Feature 1: Package Standardization  | Jan 20 | Jan 22 |
| **P2**    | Feature 2: AgentFramework Migration | Jan 23 | Jan 29 |
| **P3**    | Feature 3: A2A via LiteLLM          | Jan 30 | Feb 4  |
| **P4**    | Feature 4: Financial Jobs & Runner  | Feb 5  | Feb 11 |
| **Final** | Full System Verification & Delivery | Feb 12 | Feb 13 |
