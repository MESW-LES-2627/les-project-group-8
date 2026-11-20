# Open-ended Bet design scenario draft

- **Who:** João.
- **Tools:** Codex (GPT-6). Repository inspection and the teacher's three-part design-report template supplied in the chat.
- **Outcome:** Drafted an Iteration 2 future-change scenario for [US28](../i02.d003-user-stories.md#us28-create-and-answer-an-open-ended-bet--later), then added João’s edited text to [the design report](../../../design.md) in [PR #100](https://github.com/MESW-LES-2627/les-project-group-8/pull/100). No application code changed.
- **Delegated:** Read the glossary, ADR 0004, vision diagram, user story and Pool/Pick/Score implementation. Explained existing model and functional coupling, the single bounded context, affected interfaces, strength/distance/volatility, alternatives and a proposed design for distinct answer representations with shared submission rules.
- **What we decided ourselves, and why:** João requested a scenario grounded in existing user stories instead of post-MVP scoring variations, asked for an independent assessment of Strategy, and requested explicit requirements and coupling analysis.
- **How we checked:** Compared claims with the service/model code and US28 acceptance criteria, including the still-open text limit and correctness rules. No application tests were needed for the discussion draft.
- **Notes:** Proposed design choices remain subject to team review. Free-text correctness and sprint scheduling were not assumed to be agreed.

## Continuation: add the edited scenario to the DOO draft PR

- **Delegated:** Identified the existing draft PR, inserted the supplied attachment under Iteration 2, converted local file links to repository-relative links and updated the PR description.
- **What we decided ourselves, and why:** João refined the wording, chose explicit choice/text answer representations with one submission flow, and supplied the text to publish.
- **How we checked:** Verified that the inserted scenario matches the attachment apart from link conversion, that relative link targets exist, and that the diff is limited to documentation.
