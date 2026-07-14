# NLI Agent Failure-Prevention Rules

These rules are derived from recurring implementation and SDA review failures. They are mandatory safeguards, not stylistic preferences.

## 1. Do not confuse coverage with correctness

- One mapping row per source field does not prove a correct mapping.
- One target field per source field does not prove no loss.
- A target field that exists may still be semantically wrong.
- A controlled-value map must use observed source values and valid target values.
- Grouped facts such as latitude, longitude, accuracy, method, and time must be tested as one output object where the target model requires one geometry observation.

## 2. Do not generate authority from heuristics

Do not infer national semantics from:

- field suffixes such as `_id`;
- route-path words;
- table names;
- text keywords used for classification;
- vocabulary ordering;
- file presence;
- count thresholds.

Heuristics may identify items for review. They may not become the reviewed decision automatically.

## 3. Expected results must be independently controlled

Do not create an “expected” policy, mapping, schema, or projection by copying the observed output during the same run.

Expected registries must be separately reviewed source data. Validation compares observed results against them.

## 4. Execute negative cases

A negative test passes only when the prohibited operation is executed and rejected for the expected reason.

These are not negative tests:

- assigning the string `rejected`;
- checking that a rule name exists;
- checking that a trigger file exists;
- checking that a forbidden value is absent from prose.

## 5. Build real scenario proof

Scenario names are not scenarios. Each required scenario must contain its own relevant records, relationships, history, states, evidence, geometry, and projections.

Do not begin every scenario with one row for every entity and make only superficial changes. Test the defining behavior.

## 6. A green report may only claim executed assertions

The report must list each check actually performed. Do not say:

- “SQL validated” when only parentheses were balanced;
- “semantic mapping validated” when only target-name existence was checked;
- “authorization verified” when roles were inferred from path names;
- “no-loss proven” when a pseudo-`ASSERT` string was stored;
- “seven scenarios passed” when one generic fixture was reused.

## 7. Use real sources of truth

- Build the current schema and query `pg_catalog` rather than reconstructing it from regex where exact inventory matters.
- Generate and inspect the actual OpenAPI document rather than guessing contracts from routes.
- Build and boot the actual container image rather than testing only the host checkout.
- Restore real database dumps and compare source/restored invariants.
- Use browser/runtime evidence for workflow behavior.

## 8. Separate design from implementation

A design-only work order may change controlled design documents and explicitly authorized CI validation. It may not quietly change runtime tools, application code, executable migrations, or data.

When a real runtime defect is found:

1. record it;
2. preserve the fix;
3. create a separate maintenance branch/PR;
4. restore the active design branch to its authorized boundary.

## 9. Preserve reviewer authority

The agent may update only the resolution-log section assigned to it. It must not rewrite:

- SDA outcome;
- finding class;
- reviewer observation;
- required resolution;
- reviewer disposition;
- accepted conditions.

Resolution tooling must target a bounded section and fail if that section cannot be identified exactly.

## 10. Do not create circular evidence

A committed file cannot contain its own final commit SHA. Do not fake it.

Use:

```text
implementation SHA → CI run IDs → PR comment/metadata → SDA review record
```

## 11. Treat role and route identity precisely

- Key route policies by HTTP method plus path and operation/handler identity.
- Capture every permitted role, not only the first argument.
- Distinguish public, optional-auth, session-required, authenticated, role-required, service-client, and step-up actions.
- Validate the expected policy independently.
- Dynamic successful responses still need explicit field contracts.

## 12. Make data-model integrity enforceable

When the design claims a guarantee, represent it through one or more of:

- foreign key;
- unique/check/exclusion constraint;
- typed association;
- controlled vocabulary FK;
- reviewed trigger/function design;
- executable policy validator;
- positive and negative tests.

A comment saying “WO-002B will add a trigger” is not an implementation-ready design.

## 13. Distinguish technical validation from institutional authority

Technical checks cannot grant:

- official publication authority;
- legal administrative-boundary authority;
- land-title authority;
- final public-code grammar;
- personal-data processing authority;
- national-production approval.

Use RFIs and recorded conditions for these decisions.

## 14. Do not reduce raw values to hashes when no-loss preservation is required

A hash proves integrity of a value you still possess; it does not preserve that value.

Use a governed encrypted archive/object reference with classification, retention, access control, hash, source-row identity, and field path.

## 15. Keep transformations executable

A migration validation statement must be executable or backed by an executable test. Avoid pseudo-code presented as SQL, such as:

```text
ASSERT count(source) == count(target)
```

Use actual queries, fixture transformations, expected output rows, and comparison logic.

## 16. Validate lifecycle graphs, not just edges

For each lifecycle prove:

- every bound field uses the intended vocabulary and graph;
- all states are reachable or intentionally initial/terminal;
- terminality is correct;
- re-entry is explicit;
- forbidden transitions fail;
- actor, permission, scope, evidence, audit, public effect, reversal, and denial are defined;
- an executable validator or implementation-ready policy source exists.

## 17. Validate temporal chains completely

For version, alias, geometry, and supersession chains test:

- no self-link;
- same owner/subject/role where required;
- reciprocal pointers;
- no two-node or multi-node cycles;
- non-overlapping intervals;
- backdated correction behavior;
- containment of dependent intervals;
- historical reconstruction.

## 18. Treat fixtures as controlled data products

Fixtures need:

- deterministic IDs;
- environment allowlisting;
- ownership metadata;
- collision behavior;
- repeatable load and cleanup;
- explicit non-official classification;
- positive and negative scenario coverage.

## 19. Keep claims narrower than evidence

Prefer:

- “CI confirms these 24 named checks”

over:

- “semantic model validated.”

Prefer:

- “representative fixture inserted”

over:

- “national scenario supported.”

## 20. Stop before compounding an uncertain decision

Raise an RFI when:

- two tables could both be canonical;
- a field has multiple plausible meanings;
- an identifier might encode mutable geography;
- authority is missing;
- data loss is possible;
- a public projection is unclear;
- a future implementer would otherwise need to invent architecture.
