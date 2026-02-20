# AI Integration Notes

Working notes for model/provider integration details.

## To Capture

- Provider interface shape used by `cmdstash`
- Prompt contract for tags/description/examples
- Validation rules and failure handling
- Environment variable names and local setup

## Testing Reminders

- Keep tests deterministic (mock provider by default).
- Avoid network calls in default test runs.

## Future Checklist

- Provider swap strategy
- Retry/timeouts policy
- Cost and latency guardrails
