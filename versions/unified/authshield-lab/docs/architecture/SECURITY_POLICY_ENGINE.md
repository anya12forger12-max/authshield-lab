# Security Policy Engine Architecture

## Policy Architecture

The Security Policy Engine provides a dynamic, configurable framework for evaluating security decisions at runtime. Policies are evaluated against incoming requests and user context to produce allow/deny/challenge decisions.

### Core Components

| Component | Purpose |
|-----------|---------|
| **SecurityPolicy** | Defines a named policy with rules and a decision |
| **RuleEngine** | Evaluates individual rules against context |
| **PolicyRegistry** | Stores and manages active policies |
| **PolicyConfiguration** | System-wide policy settings |

### Policy Lifecycle

```
    ┌───────┐
    │ DRAFT  │
    └───┬───┘
        │ (review & test)
    ┌───▼───┐
    │ ACTIVE │◄──┐
    └───┬───┘   │ (re-enable)
        │       │
    ┌───▼───┐   │
    │DISABLED│───┘
    └───┬───┘
        │ (archive)
    ┌───▼───┐
    │ARCHIVED│ (terminal)
    └───────┘
```

### Policy Data Model

```python
@dataclass
class SecurityPolicy:
    policy_id: str          # Unique identifier
    name: str               # Human-readable name
    description: str        # Policy description
    status: PolicyStatus    # draft, active, disabled, archived
    decision: PolicyDecision # allow, deny, challenge, log_only
    priority: int           # Evaluation order (higher = earlier)
    rules: list             # Associated rule set
    enabled: bool           # Master switch
    created_at: datetime    # Creation timestamp
```

## Rule Engine

The Rule Engine evaluates individual security rules against a context dictionary. Rules are composed of condition clauses that are combined with AND logic.

### RuleConditionClause

Each clause evaluates a single condition:

```python
@dataclass
class RuleConditionClause:
    field_name: str    # Context key to evaluate
    operator: str      # Comparison operator
    value: Any         # Expected value
```

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `status == "active"` |
| `neq` | Not equals | `status != "locked"` |
| `gt` | Greater than | `failed_attempts > 5` |
| `gte` | Greater than or equal | `login_count >= 10` |
| `lt` | Less than | `session_count < 3` |
| `lte` | Less than or equal | `risk_score <= 2` |
| `contains` | Contains element | `"admin" in roles` |
| `in` | Value in set | `role in ["admin", "superadmin"]` |

### Rule Evaluation

Rules evaluate all conditions with AND logic:

```python
def evaluate(self, context: dict) -> bool:
    return all(c.evaluate(context) for c in self.conditions)
```

A rule with no conditions always matches. Disabled rules always match (pass-through).

### SecurityRule Data Model

```python
@dataclass
class SecurityRule:
    rule_id: str
    name: str
    description: str
    conditions: list[RuleConditionClause]
    action: str        # deny, allow, log_only
    priority: int
    enabled: bool
```

## Policy Registry

The PolicyRegistry manages the lifecycle and retrieval of security policies:

### Operations

| Operation | Description |
|-----------|-------------|
| `register(policy)` | Add a policy to the registry |
| `unregister(policy_id)` | Remove a policy |
| `get(policy_id)` | Retrieve a policy by ID |
| `search(query, enabled_only)` | Find policies by name/tag |
| `enable(policy_id)` | Enable a disabled policy |
| `disable(policy_id)` | Disable an active policy |
| `count(enabled_only)` | Count policies |
| `list_all()` | Return all policies |

### Search Capabilities

The registry supports:

- **Text search**: Case-insensitive substring match on policy names
- **Enabled filtering**: Return only enabled policies
- **Combined queries**: Search by name with enabled filter

## Decision Model

Policy decisions determine the outcome of a security evaluation:

| Decision | Behavior |
|----------|----------|
| `allow` | Permit the operation |
| `deny` | Block the operation (403 response) |
| `challenge` | Require additional verification (MFA) |
| `log_only` | Allow but record in audit trail |

### Decision Priority

When multiple policies match, decisions are resolved by:

1. **Policy priority**: Higher priority policies are evaluated first
2. **Decision precedence**: `deny` > `challenge` > `log_only` > `allow`
3. **First match**: The first policy to produce a non-`allow` decision wins

## Evaluation Pipeline

```
Incoming Request
    │
    ▼
┌─────────────────┐
│ Build Context    │ (user, request, session, IP, device)
└────────┬────────┘
         │
┌────────▼────────┐
│ Get Active      │
│ Policies        │ (sorted by priority, descending)
└────────┬────────┘
         │
┌────────▼────────┐
│ For Each Policy │
│ └─► Evaluate    │
│    Rules        │
└────────┬────────┘
         │
┌────────▼────────┐
│ Resolve         │
│ Decision        │ (deny wins, then challenge, then allow)
└────────┬────────┘
         │
┌────────▼────────┐
│ Log Decision    │
│ (if configured) │
└────────┬────────┘
         │
┌────────▼────────┐
│ Return Policy   │
│ Decision        │
└─────────────────┘
```

## Extension Points

### Adding Custom Rules

New rule types can be created by implementing the `RuleConditionClause.evaluate()` method with custom operators:

```python
class CustomClause(RuleConditionClause):
    def evaluate(self, context):
        if self.operator == "regex":
            import re
            return bool(re.match(self.value, context.get(self.field_name, "")))
        return super().evaluate(context)
```

### Policy Hooks

Policies can be extended with pre/post evaluation hooks:

- **Pre-evaluation**: Modify context before rule evaluation
- **Post-evaluation**: Audit, alert, or transform decisions

### Event Integration

The policy engine publishes events for every evaluation:

- `policy.evaluated`: A policy was evaluated against a context
- `policy.decision`: A final decision was reached
- `policy.registered`: A new policy was registered
- `policy.enabled` / `policy.disabled`: Policy state changes

## Configuration

### PolicyConfiguration

```python
@dataclass
class PolicyConfiguration:
    max_policies: int = 100
    evaluation_timeout_ms: int = 50
    log_decisions: bool = True
    default_decision: PolicyDecision = PolicyDecision.ALLOW
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
```

### Environment Profiles

| Setting | Development | Testing | Production |
|---------|-------------|---------|------------|
| `max_policies` | 50 | 20 | 100 |
| `evaluation_timeout_ms` | 100 | 200 | 50 |
| `log_decisions` | true | true | true |
| `enable_caching` | false | false | true |

### Runtime Configuration

Policies can be modified at runtime through the PolicyRegistry:

```python
# Register a new policy
policy = SecurityPolicy(
    policy_id="rate-limit-login",
    name="Login Rate Limit",
    decision=PolicyDecision.DENY,
    rules=[
        SecurityRule(
            conditions=[
                RuleConditionClause("failed_attempts", "gt", 5)
            ]
        )
    ]
)
registry.register(policy)

# Disable temporarily
registry.disable("rate-limit-login")

# Re-enable
registry.enable("rate-limit-login")
```
