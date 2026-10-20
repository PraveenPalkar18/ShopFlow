# ChangeGuard evaluation

This repository is a local, isolated benchmark for testing ChangeGuard on
realistic ShopFlow pull-request changes. The ground-truth labels live only in
`fixtures/PR-*/expected_results.json`; they are not imported or consulted by the
ShopFlow application. Scenario changes are represented by local branches
`pr-01-...` through `pr-12-...`, all based on the `baseline` commit.

## Quick start (Windows PowerShell)

```powershell
cd "E:\Major Project\test1\ShopFlow"
.\scripts\list-scenarios.ps1
.\scripts\checkout-scenario.ps1 PR-05
python -m pytest
.\scripts\export-scenario.ps1 PR-05
.\scripts\reset-baseline.ps1
```

Scenario checks intentionally fail when they detect their regression; consult
the fixture's test expectations before interpreting a failing test. The fixture
patch is also available at `fixtures/PR-xx/changes.patch`.

## Connecting ChangeGuard

1. Connect ChangeGuard to the **local ShopFlow clone** or a new, dedicated
   private/public test repository you create. Do not point it at another
   production repository.
2. Use `baseline` as the target/base branch and one `pr-xx-...` branch as the
   source/head branch. For GitHub-only integrations, create a separate test
   repository and push only these ShopFlow branches after choosing visibility;
   no remote is configured by this project.
3. Supply the exact fixture `pr_description.md` as the pull-request body.
4. Export ChangeGuard's review result to JSON or another stable form. This
   project does not assume a ChangeGuard CLI, API, or result schema.
5. Compare its labels, severity/risk, affected modules, cited issue(s), and
   recommended tests with `expected_results.json`. Record both correct
   detections and unsupported warnings. The `expected_results.json` is
   evaluation ground truth; do not feed it to ChangeGuard during analysis.

No score is generated unless predictions and matching ground-truth labels are
both available in a common, explicit schema. This repository does not invent a
ChangeGuard integration or compute precision, recall, F1, or confusion matrices
from absent predictions. Keep manually entered observations separate from the
fixtures.

## Scenario matrix

| ID | Intended change | Hidden or intentional issue | Expected risk | Relevant modules | Relevant tests | False-positive consideration |
|---|---|---|---|---|---|---|
| PR-01 | Correct README typo | None | Low | Documentation | None required | Do not emit security warnings or demand code tests. |
| PR-02 | Correct line-item rounding before order total aggregation | Pricing edge case with fractional-cent unit prices | Low–medium | Pricing, orders | `test_fractional_cent_lines_round_before_sum` | Pricing changes are intended and narrowly tested. |
| PR-03 | Update product documentation | Silently bypass admin authorization | High | Products, auth | `test_non_admin_cannot_create_product` | The code change is absent from the stated documentation scope. |
| PR-04 | Improve inventory error messages | Undocumented SQLAlchemy version upgrade | Medium | Orders, dependencies, database | `test_checkout_rejects_insufficient_stock`; dependency review | The message change is legitimate; report only the independent manifest drift. |
| PR-05 | Improve order-processing performance | Remove the sufficient-stock guard; stock can go negative | High | Inventory, orders | `test_checkout_rejects_insufficient_stock` | Do not classify ordinary reservation calls as defects without following quantity constraints. |
| PR-06 | Refactor authentication middleware | Invalid bearer token resolves to a user | Critical | Auth, API authorization | `test_invalid_bearer_token_is_rejected` | Valid token and public-route behavior should remain intact. |
| PR-07 | Add discount codes | None; intended cohesive feature | Medium | Validation, pricing, orders, persistence | `test_valid_discount_applies_to_checkout`; `test_unknown_discount_is_rejected` | Cross-module edits and a new order request body are justified by the description. |
| PR-08 | Improve startup configuration | Admin authorization defaults off | High | Configuration, auth, products | `test_non_admin_cannot_create_product` | Configuration changes are in scope but still security-sensitive. |
| PR-09 | Add order cancellation endpoint | Does not restore reserved inventory | High | Orders, inventory | `test_order_cancellation_restores_inventory` | Endpoint exists; assess workflow completeness rather than endpoint presence alone. |
| PR-10 | Fix product search whitespace handling | Unrelated mock-payment guard accepts zero amount | Medium | Products, payments | `test_mock_payment_rejects_zero_amount`; `test_search_trims_query` | Keep the useful search fix; flag only payment behavior as unrelated/risky. |
| PR-11 | Improve shared currency formatting | Rounds currency to whole units across consumers | Medium | Formatting, pricing, orders, invoices | `test_currency_format_keeps_cents` | Downstream regression scope is expected; do not flag utility propagation itself. |
| PR-12 | Extract shared product validation | None; behavior should remain the same | Low | Products, validation | Product create/update tests | Avoid risk inflation or claims of a behavioral change without evidence. |

## Confidence and scope notes

The scenarios cover both true positives and negative controls. PR-01 and PR-12
should not produce invented security concerns; PR-07 is an explicitly
multi-module feature; PR-10 combines a legitimate fix with an unrelated payment
change. PR-03, PR-05, PR-06, PR-08, PR-09, and PR-11 include failures whose
relevant tests are named in the fixture metadata. Detection is not guaranteed:
the correct outcome is grounded in the diff and available tests, not merely in
these expected-result labels.
