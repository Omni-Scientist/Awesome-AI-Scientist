# Contributing to Awesome AI Scientist

Thanks for helping keep this list useful. The goal is a compact, high-signal map of AI systems that conduct or accelerate scientific discovery.

## Before opening a pull request

- Check whether the paper, project, benchmark, or dataset is already listed.
- Use the primary paper or preprint URL, the official code repository, and the official project page.
- Add a short description that says what the resource does, not only what it is called.
- Explain why the resource belongs in the selected section.
- Check that every link works and points to the intended version.
- Avoid claims that are stronger than the paper or project documentation supports.

## Selection criteria

We prioritize resources with one or more of the following:

1. Peer-reviewed publication or a technically substantive preprint.
2. A public implementation, benchmark, dataset, environment, or reproducible artifact.
3. Evaluation against meaningful scientific, coding, experimental, or reproducibility criteria.
4. Evidence traceability: sources, code, data, protocols, or generated artifacts can be inspected.
5. A clear contribution to literature review, hypothesis generation, experiment design, experimentation, analysis, or scientific writing.

The list is intentionally selective. Generic LLM wrappers, unvalidated demos, duplicate collections, and ordinary productivity tools are usually out of scope.

## Where should an entry go?

- **AI Scientist Systems:** connected workflows spanning several research stages.
- **AI Co-Scientists / Research Agents:** systems that assist a scientist or automate only part of the loop.
- **By Research Stage:** the most important stage-specific capability.
- **By Domain:** strong domain-specific discovery or research systems.
- **Benchmarks & Evaluation:** datasets, tasks, or environments designed to measure scientific-agent ability.
- **Datasets & Environments:** corpora, APIs, simulated worlds, lab environments, and domain resources used by agents.

An entry may appear in multiple sections when the duplication improves discoverability.

## Preferred entry format

Use a compact bullet with direct links:

~~~markdown
- [**Project or paper title**](PAPER_OR_PREPRINT_URL) — One sentence describing the contribution.
  [Paper](PAPER_OR_PREPRINT_URL) · [Code](OFFICIAL_CODE_URL) · [Website](OFFICIAL_PROJECT_URL)
~~~

Use the badge style already present in the core systems section when adding a major entry. If an official code or website does not exist, omit that link rather than adding a third-party mirror without labeling it.

## Pull request checklist

- [ ] The resource is directly relevant to AI-assisted or AI-driven scientific work.
- [ ] The paper or primary project page is linked.
- [ ] The description is concise and evidence-based.
- [ ] Official code, dataset, environment, or website links are included when available.
- [ ] The section placement is appropriate.
- [ ] Links were checked after editing.
- [ ] No unrelated formatting or generated files were added.

## Responsible use

Scientific agents may generate executable code, laboratory instructions, or claims that look plausible but are wrong. Please do not describe a system as reliable, autonomous, or scientifically validated unless the linked work provides evidence. Keep safety limitations visible, especially for tools that can access a filesystem, network, instruments, or wet-lab equipment.

By contributing, you agree that your contribution can be distributed under the repository's [CC BY 4.0 license](LICENSE).
