# Structured Error

Published contract: `TLC-HC-STRUCTURED-ERROR@1.0.0`.

```json
{
  "code": "MASTER-INVALID",
  "category": "validation",
  "condition": "name missing",
  "recoverability": "non_retryable",
  "public_result": "error_only",
  "failure_atomicity": "no_observable_partial_result",
  "context": {"field": "name"},
  "transport": "implementation_defined"
}
```

The stable code and declared policy fields are structural data. Transport remains
implementation-defined by the published contract.
