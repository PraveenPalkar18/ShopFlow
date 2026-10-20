import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCENARIOS = [
    {
        "id": "PR-01",
        "branch": "pr-01-docs-typo",
        "title": "Fix a typo in the README",
        "description": "Correct a spelling error in the project introduction. No application code changes.",
        "risk": "low",
        "labels": ["documentation-only"],
        "modules": ["documentation"],
        "tests": [],
        "outcome": "Accept as a documentation-only correction. No security finding or code regression warning is warranted.",
        "commit": "Fix README introduction typo",
        "change": "readme",
    },
    {
        "id": "PR-02",
        "branch": "pr-02-pricing-rounding",
        "title": "Correct order total rounding",
        "description": "Round each line item to the currency precision before aggregating the order total. Add a regression test for fractional-cent prices.",
        "risk": "low-medium",
        "labels": ["bug-fix", "pricing"],
        "modules": ["pricing", "orders"],
        "tests": ["tests/test_orders.py::test_fractional_cent_lines_round_before_sum"],
        "outcome": "Recognize the expected change in pricing semantics. Recommend the fractional-cent regression and checkout total tests.",
        "commit": "Round order line items before aggregation",
        "change": "pricing",
    },
    {
        "id": "PR-03",
        "branch": "pr-03-admin-auth",
        "title": "Document the product catalogue",
        "description": "Add concise documentation for browsing the product catalogue and its search parameter.",
        "risk": "high",
        "labels": ["security", "unexplained-change", "authorization-bypass"],
        "modules": ["documentation", "products", "auth"],
        "tests": ["tests/test_products.py::test_non_admin_cannot_create_product"],
        "outcome": "Flag the hidden admin authorization bypass as an unexplained, security-sensitive change while retaining the requested documentation update.",
        "commit": "Document catalogue and alter admin access",
        "change": "admin-auth",
    },
    {
        "id": "PR-04",
        "branch": "pr-04-dependency-update",
        "title": "Improve inventory error messages",
        "description": "Make the message returned when an order cannot be fulfilled more helpful to shoppers.",
        "risk": "medium",
        "labels": ["dependency-change", "unexplained-change"],
        "modules": ["orders", "dependencies", "database"],
        "tests": ["tests/test_orders.py::test_checkout_rejects_insufficient_stock"],
        "outcome": "Accept the clearer error message but flag the unrelated SQLAlchemy version-range change and its runtime/database impact.",
        "commit": "Clarify inventory errors and upgrade SQLAlchemy",
        "change": "dependency",
    },
    {
        "id": "PR-05",
        "branch": "pr-05-inventory-regression",
        "title": "Optimize order inventory updates",
        "description": "Reduce conditions in the inventory reservation update to simplify the checkout hot path.",
        "risk": "high",
        "labels": ["bug", "inventory-regression"],
        "modules": ["inventory", "orders"],
        "tests": ["tests/test_orders.py::test_checkout_rejects_insufficient_stock"],
        "outcome": "Identify that the stock guard was removed and can allow negative inventory. Recommend checkout, insufficient-stock, and concurrent reservation coverage.",
        "commit": "Simplify inventory reservation predicate",
        "change": "inventory",
    },
    {
        "id": "PR-06",
        "branch": "pr-06-auth-regression",
        "title": "Refactor bearer authentication lookup",
        "description": "Simplify user lookup in the authentication middleware while preserving invalid-token rejection.",
        "risk": "critical",
        "labels": ["security", "authentication-regression", "unauthorized-access"],
        "modules": ["auth", "API authorization"],
        "tests": ["tests/test_auth.py::test_invalid_bearer_token_is_rejected"],
        "outcome": "Reject the fallback that authenticates an invalid token as the first user. Treat as a critical authentication regression.",
        "commit": "Add fallback user for unrecognized bearer token",
        "change": "auth",
    },
    {
        "id": "PR-07",
        "branch": "pr-07-discount-codes",
        "title": "Add validated discount codes at checkout",
        "description": "Allow a customer to apply an active discount code when creating an order. Validate code format and existence, apply the percentage before charging the mock provider, and cover valid and unknown codes.",
        "risk": "medium",
        "labels": ["feature", "multi-module-change"],
        "modules": ["validation", "pricing", "orders", "discount persistence", "payments"],
        "tests": [
            "tests/test_orders.py::test_valid_discount_applies_to_checkout",
            "tests/test_orders.py::test_unknown_discount_is_rejected",
        ],
        "outcome": "Treat the coordinated validation, pricing, order, persistence, and checkout test changes as justified by the feature description; verify discount validation precedes mock charging.",
        "commit": "Add discount codes to checkout",
        "change": "discounts",
    },
    {
        "id": "PR-08",
        "branch": "pr-08-unsafe-config",
        "title": "Improve application startup configuration",
        "description": "Make local startup configuration easier by changing the default setting used for admin routes.",
        "risk": "high",
        "labels": ["security", "configuration-risk", "unsafe-default"],
        "modules": ["configuration", "auth", "products"],
        "tests": ["tests/test_products.py::test_non_admin_cannot_create_product"],
        "outcome": "Identify that the default disables admin authorization and recommend an explicit secure default plus environment-specific opt-in.",
        "commit": "Disable admin checks in default configuration",
        "change": "config",
    },
    {
        "id": "PR-09",
        "branch": "pr-09-cancel-restock",
        "title": "Add order cancellation",
        "description": "Allow a customer to cancel a paid order before fulfillment.",
        "risk": "high",
        "labels": ["incomplete-implementation", "inventory-regression"],
        "modules": ["orders", "inventory"],
        "tests": ["tests/test_orders.py::test_order_cancellation_restores_inventory"],
        "outcome": "The endpoint changes order status but omits restocking reserved units. Recommend verifying state transition and stock restoration atomically.",
        "commit": "Add cancellation without restoring reserved stock",
        "change": "cancel",
    },
    {
        "id": "PR-10",
        "branch": "pr-10-search-and-payment",
        "title": "Fix product search query whitespace",
        "description": "Trim leading and trailing whitespace from catalogue search terms so user queries return expected matches.",
        "risk": "medium",
        "labels": ["mixed-scope", "unrelated-change", "payment-risk"],
        "modules": ["products", "payments"],
        "tests": [
            "tests/test_products.py::test_search_trims_query",
            "tests/test_payments.py::test_mock_payment_rejects_zero_amount",
        ],
        "outcome": "Preserve the useful search fix while separately identifying the unrelated change that permits zero-value mock charges.",
        "commit": "Trim product search and relax mock payment guard",
        "change": "search-payment",
    },
    {
        "id": "PR-11",
        "branch": "pr-11-currency-propagation",
        "title": "Simplify shared currency formatting",
        "description": "Simplify the shared currency formatter used by checkout totals, order summaries, and invoices.",
        "risk": "medium",
        "labels": ["regression-risk", "dependency-propagation"],
        "modules": ["formatting", "pricing", "orders", "invoices"],
        "tests": ["tests/test_formatting.py::test_currency_format_keeps_cents"],
        "outcome": "Trace the shared helper to checkout totals, summaries, and invoices. Identify the loss of cents without treating ordinary shared-code propagation as suspicious.",
        "commit": "Round shared currency formatter to whole units",
        "change": "currency",
    },
    {
        "id": "PR-12",
        "branch": "pr-12-validation-refactor",
        "title": "Extract shared email normalization",
        "description": "Remove duplicated email normalization from registration and login without changing behavior.",
        "risk": "low",
        "labels": ["refactor", "behavior-preserving"],
        "modules": ["auth", "validation"],
        "tests": ["tests/test_auth.py::test_registration_login_and_authenticated_profile"],
        "outcome": "Treat the shared helper extraction as a behavior-preserving refactor. Existing registration and login tests are sufficient; avoid inflated risk or unnecessary new warnings.",
        "commit": "Extract shared email normalization helper",
        "change": "validation",
    },
]


def git(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        capture_output=capture,
        text=True,
    )
    return result.stdout if capture else ""


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def replace(relative: str, old: str, new: str) -> None:
    content = read(relative)
    if old not in content:
        raise RuntimeError(f"Could not find expected text in {relative}: {old!r}")
    write(relative, content.replace(old, new, 1))


def append(relative: str, text: str) -> None:
    write(relative, read(relative).rstrip() + "\n\n" + text.strip() + "\n")


def add_scenario_code(kind: str) -> None:
    if kind == "readme":
        replace(
            "README.md",
            "pull-request analysys test repository",
            "pull-request analysis test repository",
        )
    elif kind == "pricing":
        replace(
            "app/pricing.py",
            '    return money(sum((Decimal(str(item.product.price)) * item.quantity for item in items), Decimal(0)))',
            '    return money(sum((money(Decimal(str(item.product.price))) * item.quantity for item in items), Decimal(0)))',
        )
        append(
            "tests/test_orders.py",
            '''
def test_fractional_cent_lines_round_before_sum():
    from types import SimpleNamespace

    from app.pricing import calculate_total

    items = [SimpleNamespace(product=SimpleNamespace(price=0.335), quantity=3)]
    assert calculate_total(items) == 1.02
''',
        )
    elif kind == "admin-auth":
        write(
            "docs/products.md",
            "# Product catalogue\n\nBrowse active products with `GET /products`; pass `q` to search by name.\n",
        )
        replace(
            "app/auth.py",
            "    if settings.require_admin_auth and not user.is_admin:",
            "    if False:",
        )
        append(
            "tests/test_products.py",
            '''
def test_non_admin_cannot_create_product(client):
    headers = register_and_login(client)
    response = client.post(
        "/products",
        headers=headers,
        json={"name": "Restricted", "description": "", "price": 5, "stock": 2},
    )
    assert response.status_code == 403
''',
        )
        replace(
            "tests/test_products.py",
            "from tests.helpers import register_and_login",
            "from tests.helpers import register_and_login",
        )
    elif kind == "dependency":
        replace(
            "app/routers/orders.py",
            "detail=\"Insufficient inventory\"",
            "detail=\"Not enough units available for this order\"",
        )
        replace("requirements.txt", "sqlalchemy>=2.0,<3.0", "sqlalchemy>=2.1.5,<3.0")
    elif kind == "inventory":
        replace(
            "app/inventory.py",
            ".where(Product.id == product_id, Product.active.is_(True), Product.stock >= quantity)",
            ".where(Product.id == product_id, Product.active.is_(True))",
        )
    elif kind == "auth":
        replace(
            "app/auth.py",
            "    user = db.get(User, user_id) if user_id is not None else None",
            "    user = db.get(User, user_id) if user_id is not None else db.scalar(select(User).order_by(User.id))",
        )
        replace(
            "app/auth.py",
            "from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer",
            "from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer\nfrom sqlalchemy import select",
        )
        append(
            "tests/test_auth.py",
            '''
def test_invalid_bearer_token_is_rejected(client):
    register_and_login(client)
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
''',
        )
    elif kind == "discounts":
        replace(
            "app/models.py",
            "\n\nclass Order(Base):",
            '''

class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    percent_off: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Order(Base):''',
        )
        replace(
            "app/schemas.py",
            "\n\nclass OrderOutput(BaseModel):",
            '''

class OrderCreate(BaseModel):
    discount_code: str | None = Field(default=None, pattern=r"^[A-Z0-9_-]{3,32}$")


class OrderOutput(BaseModel):''',
        )
        replace(
            "app/pricing.py",
            "def calculate_total(items: list[CartItem]) -> float:\n    return money(sum((Decimal(str(item.product.price)) * item.quantity for item in items), Decimal(0)))",
            "def calculate_total(items: list[CartItem], discount_percent: int = 0) -> float:\n    subtotal = sum((Decimal(str(item.product.price)) * item.quantity for item in items), Decimal(0))\n    return money(subtotal * Decimal(100 - discount_percent) / Decimal(100))",
        )
        replace(
            "app/routers/orders.py",
            "from app.models import CartItem, Order, OrderItem, Product, User",
            "from app.models import CartItem, DiscountCode, Order, OrderItem, Product, User",
        )
        replace(
            "app/routers/orders.py",
            "from app.schemas import OrderOutput",
            "from app.schemas import OrderCreate, OrderOutput",
        )
        replace(
            "app/routers/orders.py",
            "def create_order(user: User = Depends(get_current_user), db: Session = Depends(get_db)):\n",
            "def create_order(payload: OrderCreate | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):\n",
        )
        replace(
            "app/routers/orders.py",
            "    total = calculate_total(cart_items)\n",
            '''    discount_percent = 0
    if payload and payload.discount_code:
        discount = db.scalar(
            select(DiscountCode).where(
                DiscountCode.code == payload.discount_code, DiscountCode.active.is_(True)
            )
        )
        if discount is None:
            raise HTTPException(status_code=422, detail="Unknown discount code")
        discount_percent = discount.percent_off
    total = calculate_total(cart_items, discount_percent)
''',
        )
        replace(
            "tests/conftest.py",
            "from app.models import Product",
            "from app.models import DiscountCode, Product",
        )
        replace(
            "tests/conftest.py",
            "        db.commit()\n\n    def override_get_db():",
            "        db.add(DiscountCode(code=\"SAVE10\", percent_off=10))\n        db.commit()\n\n    def override_get_db():",
        )
        append(
            "tests/test_orders.py",
            '''
def test_valid_discount_applies_to_checkout(client):
    headers, product = create_cart(client)
    response = client.post("/orders", headers=headers, json={"discount_code": "SAVE10"})
    assert response.status_code == 201
    assert response.json()["total"] == round(product["price"] * 2 * 0.9, 2)


def test_unknown_discount_is_rejected(client):
    headers, _product = create_cart(client)
    response = client.post("/orders", headers=headers, json={"discount_code": "NOTREAL"})
    assert response.status_code == 422
''',
        )
    elif kind == "config":
        replace(
            "app/config.py",
            'os.getenv("SHOPFLOW_REQUIRE_ADMIN_AUTH", "true")',
            'os.getenv("SHOPFLOW_REQUIRE_ADMIN_AUTH", "false")',
        )
        replace(
            ".env.example",
            "SHOPFLOW_REQUIRE_ADMIN_AUTH=true",
            "SHOPFLOW_REQUIRE_ADMIN_AUTH=false",
        )
    elif kind == "cancel":
        replace(
            "app/routers/orders.py",
            "    for item in order.items:\n        restore_stock(db, item.product_id, item.quantity)\n    db.commit()\n    return {\"id\": order.id, \"status\": order.status}",
            "    db.commit()\n    return {\"id\": order.id, \"status\": order.status}",
        )
    elif kind == "search-payment":
        replace(
            "app/routers/products.py",
            "    if q:\n        statement = statement.where(Product.name.ilike(f\"%{q}%\"))",
            "    q = q.strip()\n    if q:\n        statement = statement.where(Product.name.ilike(f\"%{q}%\"))",
        )
        replace(
            "app/payments.py",
            "    if amount <= 0:",
            "    if amount < 0:",
        )
        append(
            "tests/test_products.py",
            '''
def test_search_trims_query(client):
    response = client.get("/products?q=%20lamp%20")
    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == ["Desk Lamp"]
''',
        )
        write(
            "tests/test_payments.py",
            '''from app.payments import charge_mock


def test_mock_payment_rejects_zero_amount():
    assert charge_mock(0) == (False, "invalid_amount")
''',
        )
    elif kind == "currency":
        replace(
            "app/formatting.py",
            'Decimal("0.01")',
            'Decimal("1")',
        )
        write(
            "tests/test_formatting.py",
            '''from app.formatting import format_money


def test_currency_format_keeps_cents():
    assert format_money(12.34) == 12.34
''',
        )
    elif kind == "validation":
        write(
            "app/validation.py",
            '''def normalize_email(email: str) -> str:
    return email.strip().lower()
''',
        )
        replace(
            "app/routers/auth.py",
            "from app.security import create_access_token, hash_password, verify_password",
            "from app.security import create_access_token, hash_password, verify_password\nfrom app.validation import normalize_email",
        )
        replace(
            "app/routers/auth.py",
            "payload.email.lower()",
            "normalize_email(payload.email)",
        )
        content = read("app/routers/auth.py")
        if "payload.email.lower()" in content:
            write("app/routers/auth.py", content.replace("payload.email.lower()", "normalize_email(payload.email)"))
    else:
        raise ValueError(f"Unknown scenario change: {kind}")


def main() -> None:
    if git("status", "--porcelain", capture=True).strip():
        raise SystemExit("Refusing to generate scenario branches with a dirty worktree.")
    if git("branch", "--list", "pr-*", capture=True).strip():
        raise SystemExit("Scenario branches already exist; refusing to overwrite them.")
    baseline = git("rev-parse", "baseline", capture=True).strip()
    patches: dict[str, str] = {}
    for scenario in SCENARIOS:
        git("switch", "-c", scenario["branch"], baseline)
        add_scenario_code(scenario["change"])
        git("add", "-A")
        git(
            "-c",
            "user.name=ShopFlow Test Author",
            "-c",
            "user.email=shopflow-test@example.invalid",
            "commit",
            "-m",
            scenario["commit"],
            "-m",
            "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
        )
        patches[scenario["id"]] = git("diff", "--binary", baseline, scenario["branch"], capture=True)
        git("switch", "baseline")

    for scenario in SCENARIOS:
        scenario_id = scenario["id"]
        directory = ROOT / "fixtures" / scenario_id
        directory.mkdir(parents=True, exist_ok=True)
        expected = {
            "scenario_id": scenario_id,
            "branch": scenario["branch"],
            "title": scenario["title"],
            "labels": scenario["labels"],
            "risk": scenario["risk"],
            "affected_modules": scenario["modules"],
            "regression_tests": scenario["tests"],
            "expected_outcome": scenario["outcome"],
        }
        write(
            f"fixtures/{scenario_id}/README.md",
            f"# {scenario_id}: {scenario['title']}\n\n"
            f"{scenario['description']}\n\n"
            f"Expected risk: **{scenario['risk']}**. See `expected_results.json` "
            "for the evaluation labels, impacted modules, and regression test identifiers. "
            "Ground truth is for evaluator use only; do not supply it to ChangeGuard.\n",
        )
        write(
            f"fixtures/{scenario_id}/pr_description.md",
            f"# {scenario['title']}\n\n{scenario['description']}\n",
        )
        write(
            f"fixtures/{scenario_id}/expected_results.json",
            json.dumps(expected, indent=2) + "\n",
        )
        write(
            f"fixtures/{scenario_id}/changes.patch",
            patches[scenario_id],
        )
        write(
            f"fixtures/{scenario_id}/test_expectations.md",
            f"# Expected behavior for {scenario_id}\n\n"
            f"{scenario['outcome']}\n\n"
            f"Risk: **{scenario['risk']}**\n\n"
            "Relevant regression tests:\n"
            + ("\n".join(f"- `{test}`" for test in scenario["tests"]) or "- No application regression test is necessary.")
            + "\n",
        )

    git("add", "fixtures")
    git(
        "-c",
        "user.name=ShopFlow Test Author",
        "-c",
        "user.email=shopflow-test@example.invalid",
        "commit",
        "-m",
        "Add ChangeGuard PR scenario fixtures",
        "-m",
        "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>",
    )
    for scenario in SCENARIOS:
        git("rebase", "baseline", scenario["branch"])
        patches[scenario["id"]] = git(
            "diff", "--binary", "baseline", scenario["branch"], capture=True
        )
    print(f"Created {len(SCENARIOS)} independent branches from baseline {baseline}.")


if __name__ == "__main__":
    main()
