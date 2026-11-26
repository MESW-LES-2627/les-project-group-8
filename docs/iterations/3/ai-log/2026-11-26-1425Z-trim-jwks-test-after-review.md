# Trim the JWKS test to our own wiring, after review

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` skill.
- **Outcome:** Answered the review on [#206](https://github.com/MESW-LES-2627/les-project-group-8/pull/206): [`test_jwks_verifier.py`](../../../../backend/tests/integration/test_jwks_verifier.py) no longer tests PyJWT's refetch and cooldown, and [i03.d004](../i03.d004-testing.md) gains the rule that a configured library's behaviour is not tested.
- **Delegated:** Removed the cooldown and new-`kid` refetch checks, the `clock` fixture and the patch on PyJWT's private `jwt.jwks_client.time`; renamed the test. Updated d004 and added an amendment note to the [grilling record](../../../assets/iterations/3/grilling-testing-policy-and-coverage.md).
- **What we decided ourselves, and why:** The reviewer was right that most of the first test checked PyJWT, not our code. We kept "3 tokens, 1 fetch", because it is the one part that checks our wiring (one `PyJWKClient`, cache on), and made the rule explicit in the testing policy.
- **Where it was wrong:** The [earlier session](2026-11-25-1045Z-backend-coverage-and-jwks-test.md) tested a dependency's behaviour, which needed a patch on a private PyJWT import. Fixed in this change.
- **How we checked:** Full backend suite passes locally (166 passed, 2 skipped); `shared/auth.py` stays at 100% line and branch. With `cache_jwk_set=False` in `for_jwks`, the trimmed test fails with `assert 3 == 1`.
