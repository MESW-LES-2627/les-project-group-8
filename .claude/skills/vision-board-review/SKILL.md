---
name: vision-board-review
description: Rate a Product Vision Board against Roman Pichler's Product Vision Board checklist, criterion by criterion, and report only. Use when asked to review, rate or check a product vision board, such as docs/iterations/NN/iNN.d001-vision.md.
---

# Vision board review

Rate a Product Vision Board against Roman Pichler's checklist below, and only
that checklist. This is a report: edit, create or delete no files.

## Steps

1. Read the board the user names. If none is named, use the vision file in
   the highest-numbered iteration folder, such as
   `docs/iterations/2/i02.d001-vision.md`.
2. Rate every criterion in the checklist, block by block, then the overall
   criteria. Skip none and add none.
3. For each criterion give:
   - **Verdict:** Met, Partly or Not met, or Unverifiable for the cases in
     step 4.
   - **Evidence:** the board sentence the verdict rests on, quoted word for
     word. If the board says nothing on it, write "None" and rate Not met.
   - **Fix:** one line saying what to change. Write "None" when Met.
4. Judge these overall criteria from the repo, not from the board's wording:
   - **Connected:** Met if the board links to the MVP, such as
     `docs/iterations/2/i02.d002-mvp.md`. No link is Not met.
   - **Adaptive:** run `git log --follow --format='%ad %h %s' --date=short --
     <board file>`. Met if a commit changed the board within the last three
     months of today, Not met otherwise. Quote the newest commit as evidence.
   - **Validated**, overall **Shared** (not the Vision block's Shared) and
     **Needs-first:** the repo cannot show these. Rate them Unverifiable
     unless the board links evidence (interview notes, prototype results, a
     review record); then rate them from that evidence.
5. Give no overall or 0–10 score.

## Report format

One table per block, in checklist order:

| Criterion | Verdict | Evidence | Fix |
| :- | :- | :- | :- |
| Inspiring | Partly | "…" | … |

## Checklist

Copied word for word from the
[Product Vision Board with Checklist](https://www.romanpichler.com/downloads/tools/Product-Vision-Board-with-Checklist.pdf).

> **PRODUCT VISION BOARD CHECKLIST**
>
> Use the following criteria to effectively apply the Product Vision Board.
>
> **VISION**
>
> - **Inspiring:** Describes the positive change the product should create.
> - **Shared:** Unites people and creates alignment.
> - **Ethical:** Gives rise to a product that does not cause any harm to people and the planet.
> - **Concise:** Easy to understand and remember.
> - **Ambitious:** Describes a big, audacious goal that might never be fully reached.
> - **Enduring:** Provides guidance for the next five to ten years.
>
> **TARGET GROUP**
>
> - **Clear:** The target group is clearly characterised, for example, by using demographics and behavioural attributes.
> - **Specific:** You can tell if somebody is included in the target group or not.
> - **Cohesive:** The members of a target group share similar attributes, e.g., age, lifestyle, disposable income. If that’s not the case, then break up the target group and form several subgroups.
>
> **NEEDS**
>
> - **Outcome-based:** Capture the reason why people would want to use the product. Describe what success looks like from the perspectives of the users and customers.
> - **Specific:** The needs are detailed enough so that you can validate them.
> - **Focused:** Concentrate on the main problem/benefit, the main reason for people to use the product.
> - **Prioritised:** If you do identify several needs, prioritise them according to their importance for the target group.
>
> **PRODUCT**
>
> - **Type:** It’s clear what kind of product you want to offer, for example, mobile app on Android and iOS
> - **Differentiated:** The aspects of your product that make it stand out, set it apart from alternative offerings are stated.
> - **Focused:** There are no more than five features.
> - **Big:** The features are big, coarse-grained product capabilities.
>
> **BUSINESS GOALS**
>
> - **Outcome-based:** The desired business benefits, the company’s reason for investing in the product, are clearly described, for example, generating revenue, increasing brand equity, reducing cost.
> - **Specific:** The business goals are detailed; state rough targets if possible.
> - **Prioritised:** If more than one business goal is identified, order them according to their business impact.
>
> **OVERALL CRITERIA**
>
> - **Needs-first:** Start with the needs after you’ve captured the vision especially when you create a new strategy—be it for a brand-new product or for an existing one.
> - **Validated:** The statements in the Target Group, Needs, Product, and Business Goal sections does not contain any major hypotheses and risks. They have been successfully validated, for instance, by interviewing and observing target users, building throwaway prototypes, and carrying out competitive analysis.
> - **Adaptive:** The Product Vision Board is regularly reviewed and adjusted, at least once every three months as a rule of thumb.
> - **Shared:** The key stakeholders and development team members have a shared understanding of the contents.
> - **Connected:** The strategy captured on the board is systematically connected to more specific outcomes, preferably to an outcome-based, goal-oriented product roadmap like my GO Product Roadmap.
>
> © 2024 Roman Pichler
