# Review 08 F12 Semantic Mutation Test Report

Each mutation is applied in a copied temporary design workspace and verified by running the actual `design_consistency_check.py` gate.

Mutations: 11
Caught: 11
Failed: 0

| Mutation | Status | Expected reason |
|---|---|---|
| wrong-transformed-output | passed | named transform assertion must come from disposable DB execution |
| missing-archive-or-final-fk | passed | archive-created assertion must include governed archive row evidence |
| wrong-field-classification | passed | missing classification |
| removed-cardinality-constraint | passed | target schema actual trigger catalog missing required semantic triggers |
| temporal-cycle-or-overlap | passed | invalid-temporal-overlap was not produced by real SQL/policy execution |
| weakened-geometry-authority | passed | geometry promotion trigger does not bind actor permission |
| missing-lifecycle-transition | passed | every authored lifecycle transition |
| wrong-api-policy | passed | route policy must be independently reviewed |
| missing-api-response-field-projection | passed | every successful response must have exact reviewed response fields |
| broken-scenario-output | passed | F10 scenario must include persisted query evidence |
| negative-harness-false-pass-regression | passed | negative harness false-pass regression |
