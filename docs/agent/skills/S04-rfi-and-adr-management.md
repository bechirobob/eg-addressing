# S04 — RFI and ADR Management

## Invoke when

- the task reaches a reserved architecture question;
- institutional authority is unknown;
- two or more viable designs have materially different consequences;
- a new identifier, role, data class, lifecycle, external dependency, source of truth, publication rule, or retention rule is proposed;
- an existing ADR is incomplete or contradicted by evidence.

## Required inputs

- active work order’s reserved questions;
- current ADRs and RFIs;
- relevant standards;
- concrete implementation/model evidence;
- institutional owner or authority, if known.

## Procedure

### 1. Decide whether an RFI or ADR is required

Use an **RFI** when an external or reserved authority must decide. Use an **ADR** when the SDA can make a durable technical decision. Use both when a technical design depends on an institutional choice.

### 2. Frame one decision per record

Do not bundle unrelated decisions. State:

- exact question;
- why it blocks safe progress;
- affected criteria, domains, data, users, and environments;
- decision owner;
- consequence of no decision.

### 3. Analyze real alternatives

For each option include:

- behavior and model;
- benefits;
- costs and operational burden;
- security/privacy effects;
- authority and legal effects;
- migration and compatibility effects;
- performance/scaling effects;
- failure modes;
- reversibility;
- required evidence.

Avoid generic options such as “keep current,” “use proposal,” and “use new model” without the actual mechanics.

### 4. Make a recommendation

The recommendation must cite work-order criteria and standards. A recommendation is not approval.

### 5. Link the decision to implementation controls

An accepted ADR must identify:

- model or code identifiers affected;
- constraints and invariants;
- migration consequences;
- acceptance tests;
- unresolved RFIs;
- superseded ADRs or prior decisions.

### 6. Maintain decision coverage

For work orders with reserved questions, maintain a matrix:

| Question | ADR/RFI | Owner | Status | Blocking effect | Implementation artifact |
|---|---|---|---|---|---|

No reserved question may exist only in draft SQL or a diagram.

## Outputs

- formal RFI and/or ADR;
- decision coverage matrix;
- implementation constraints and acceptance tests;
- explicit blocking/non-blocking status.

## Stop or RFI conditions

Stop when:

- the accountable authority is not identified;
- the recommendation assumes legislation, government hierarchy, publication authority, data ownership, or retention policy;
- a “temporary” implementation would become irreversible national identity or public-code behavior;
- the decision is being embedded in generated output rather than maintained as reviewed source;
- the ADR claims a safeguard not represented by a named passing assertion.

## Evidence gate

An ADR is not ready for acceptance unless:

- alternatives are specific and technically credible;
- consequences are domain-specific;
- failure modes are explicit;
- migration and operational effects are clear;
- acceptance checks exist and can fail;
- open institutional decisions remain visible.

## Anti-patterns

- Generating ADR prose from one shared template and treating it as reviewed analysis.
- Marking an ADR accepted while its defining test still fails or does not exist.
- Using an RFI merely to record a decision already silently made in code.
- Asking every authority to decide every issue instead of naming one accountable owner.
- Rewriting an accepted ADR rather than explicitly superseding it.
