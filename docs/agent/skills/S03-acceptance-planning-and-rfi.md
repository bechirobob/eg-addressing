# S03 — Acceptance-Criteria Planning and Decision Control

## Invoke when

Every work order, design task, implementation task, or SDA remediation.

## Required inputs

- active work order;
- acceptance criteria and required evidence;
- applicable standards and ADRs;
- S01 scope matrix;
- S02 impact analysis when applicable;
- current review findings for remediation.

## Procedure

### 1. Translate each criterion into observable truth

For every acceptance criterion, answer:

```text
What must be observably true?
What must remain observably false?
Which authority or policy governs it?
Which source/model/code change creates it?
Which positive test proves it?
Which negative test proves its boundary?
Which evidence will be tied to the exact head?
What would make the criterion fail?
```

### 2. Build the criterion matrix

| AC | Observable result | Change | Positive test | Negative test | Authority check | Evidence | Risk/RFI |
|---|---|---|---|---|---|---|---|

Each row must use criterion-specific language. “See design pack,” “CI passes,” or “artifact exists” is not sufficient.

### 3. Identify decision points

Classify each decision:

- already decided by work order or ADR;
- delegated implementation detail;
- SDA technical decision needed;
- Programme Owner/institutional decision needed;
- legal/privacy/security/GIS/publication authority decision needed.

Do not ask for confirmation on already-decided items. Do not silently decide reserved items.

### 4. Define implementation sequence

Order work so that each step has a validation checkpoint. Use expand–migrate–contract when data or contracts change.

### 5. Define evidence before implementation

Design tests and expected artefacts before coding. Expected outputs must be independent of the implementation logic.

### 6. Define rollback or forward recovery

For each state-changing unit, specify:

- whether rollback is safe;
- whether forward recovery is required;
- which data or external effect may persist;
- how idempotency and retries behave.

## Outputs

- criterion-mapped plan;
- decision classification list;
- test/evidence design;
- implementation sequence;
- rollback/forward-recovery notes;
- RFIs where required.

## Stop or RFI conditions

Stop when:

- a criterion cannot be expressed as observable behavior;
- expected evidence depends on the implementation generator;
- a no-loss claim lacks executable value and relationship checks;
- a breaking change lacks transition and recovery;
- multiple criteria are bulk-mapped to one generic proof;
- a reserved decision is being embedded in SQL, code, fixtures, or a generator.

## Evidence gate

Before implementation, every acceptance criterion must have:

- a unique row;
- positive and negative proof;
- authority check;
- evidence artifact;
- failure condition;
- explicit status of any unresolved RFI.

## Anti-patterns

- Copying the same plan sentence into every criterion row.
- Marking a criterion PASS because all expected files exist.
- Adding tests after implementation and tailoring them to current output.
- Treating an RFI as optional documentation after the decision is already encoded.
- Using counts to prove no-loss transformation without value and relationship reconciliation.
