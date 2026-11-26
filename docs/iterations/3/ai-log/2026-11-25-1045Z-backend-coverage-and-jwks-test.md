# Report backend coverage in CI, and test JWKS caching

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills.
- **Outcome:** Coverage in [`backend-ci.yml`](../../../../.github/workflows/backend-ci.yml) and [`backend/.coveragerc`](../../../../backend/.coveragerc), plus [`test_jwks_verifier.py`](../../../../backend/tests/integration/test_jwks_verifier.py), for [#201](https://github.com/MESW-LES-2627/les-project-group-8/issues/201).
- **Delegated:** Added `pytest-cov` and a per-file line and branch table (domain services first) to the job summary, uploaded the HTML report as an artifact, and wrote the JWKS integration test with a stdlib key-set server that counts fetches, following Q1, Q2, Q4, Q9 and Q13 of the [grilling record](../../../assets/iterations/3/grilling-testing-policy-and-coverage.md). Updated [i03.d004](../i03.d004-testing.md), which still called the JWKS fetch a hand check. Ran a two-axis review (standards, spec).
- **Where it was wrong:** It first expected a new `kid` to refetch straight away. PyJWT 2.15 waits 30 s after any fetch, so the test drives PyJWT's clock instead of waiting.
- **How we checked:** Full suite passes locally (166 passed, 2 skipped); `shared/auth.py` is at 100%. With caching turned off in `for_jwks`, the caching test fails (3 fetches instead of 1). The job summary and artifact were not seen in a real CI run before the commit.
- **Notes:** The test also covers two things the issue didn't ask for: an unknown `kid` inside the cooldown is refused without a fetch, and an unreachable key set raises a connection error rather than a 401. The clock patch depends on PyJWT's private `jwt.jwks_client.time` import.
