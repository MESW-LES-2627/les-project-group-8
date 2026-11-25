# Decide the testing policy and coverage report

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `grill-with-docs` skill (`grilling` + `domain-modeling`).
- **Outcome:** The [grilling record](../../../assets/iterations/3/grilling-testing-policy-and-coverage.md) for closing the Unit Tests gap; issues [#195](https://github.com/MESW-LES-2627/les-project-group-8/issues/195)–[#198](https://github.com/MESW-LES-2627/les-project-group-8/issues/198) filed to decide later; [#179](https://github.com/MESW-LES-2627/les-project-group-8/issues/179)–[#182](https://github.com/MESW-LES-2627/les-project-group-8/issues/182) assigned.
- **Delegated:** Read the rubric, CI workflows and `i03.d004-testing.md`; asked the questions with recommended answers; filed the issues and wrote the record.
- **What we decided ourselves, and why:** Coverage measures what each layer is responsible for, instead of the AI's "measure everything", with exclusions matching the policy so the number isn't circular. Hand checks don't count as coverage: the JWKS caching gets an automated test, and migration data preservation becomes an issue. Codecov, mutation testing and branch protection are deferred to issues.
- **Where it was wrong:** The handoff said there was no testing policy; d004 already named several untested parts, just without a rule. The AI also first proposed leaving the JWKS methods as known misses "checked by hand", which Alef rejected (Q13–Q14 in the record).
- **How we checked:** Checked the record's links and the issue numbers after filing.
