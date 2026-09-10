# Contributing

Thank you for improving Functional Acceptance. Contributions should preserve
the project's central promise: verify a real user outcome without relabelling
missing evidence as success.

## Before changing code or instructions

Open an Issue first when a proposal changes user-visible acceptance semantics,
authority boundaries, supported environments, or reporting behavior. Small
documentation corrections can go directly to a pull request.

Use synthetic data and isolated targets. Never commit credentials, private
acceptance reports, customer data, generated virtual environments, or test
artifacts from another project.

## Local checks

Run the checks relevant to the change from the repository root:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B -m unittest discover -s examples/paginated_export -p 'test_export.py' -v
python3 -B -S -m unittest discover -s examples/sqlite_utils/acceptance -p test_lifecycle.py -v
python3 -B -S -m unittest discover -s examples/sqlite_utils/acceptance -p test_identity.py -v
```

For a Skill change, include the user promise, a counterexample or independent
observation it addresses, and evidence that the proposed instructions do not
turn a known gap into a false PASS. If an evaluation uses an old-versus-new
comparison, keep prompts, tools, budget, and grading symmetric.

## Pull requests

Keep pull requests focused. Explain the user-facing result, affected files,
tests run, limitations, and any follow-up that remains UNVERIFIED. Do not claim
release readiness from a green local suite alone. By contributing, you agree
that your contribution is available under the [MIT License](LICENSE).
