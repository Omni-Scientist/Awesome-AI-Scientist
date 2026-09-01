# Contributing to Awesome AI Scientist

Thanks for helping keep this list useful. The goal is a compact, high-signal map of AI systems that conduct or accelerate scientific discovery.

## Before opening a pull request

- Check whether the paper, project, benchmark, or dataset is already listed.
- Use the primary paper or preprint URL, the official code repository, and the official project page.
- Write a description that says what the resource does, not only what it is called.
- Verify every link actually resolves. Run `python3 scripts/check_links.py README.md`.
- Avoid claims stronger than the paper or project documentation supports.

## Selection criteria

We prioritize resources with one or more of the following.

1. Peer-reviewed publication or a technically substantive preprint.
2. A public implementation, benchmark, dataset, environment, or reproducible artifact.
3. Evaluation against meaningful scientific, coding, experimental, or reproducibility criteria.
4. Evidence traceability, so sources, code, data, protocols, or generated artifacts can be inspected.
5. A clear contribution to literature review, ideation, experiment design, experimentation, analysis, or scientific writing.

The list is intentionally selective. Generic LLM wrappers, unvalidated demos, duplicate collections, and ordinary productivity tools are usually out of scope.

## Where should an entry go?

Give each resource one canonical home. Link to that entry when it is relevant elsewhere; do not duplicate it across sections.

| Section | What belongs there |
|:--|:--|
| 🧭 Surveys & Position Papers | surveys, taxonomies, perspectives, critical pieces |
| 🤖 End-to-End AI Scientists | connected workflows spanning several research stages |
| 🔬 Co-Scientists & Research Agents | systems assisting a scientist or automating part of the loop |
| 🧰 Open-Source Workbenches | platforms you can clone and run, with a verified license |
| 📊 Benchmarks & Evaluation | tasks or environments measuring scientific-agent ability |
| 📦 Datasets, Corpora & Environments | corpora, APIs, simulated worlds, lab environments, domain data |
| 🎓 Tutorials, Blogs & Talks | learning material and technical reports |

### Two extra rules

**Blogs and technical reports** are limited to major labs, currently DeepMind, Google, Anthropic, Meta, Microsoft, and journal news desks such as Nature. Personal blogs, startup announcements, and newsletters are out of scope, however good they are. An official project page for a system already listed is not a blog entry; it belongs on that system's own line as a `Site` badge.

**Open-Source Workbenches requires a real license.** Read the actual `LICENSE` file before submitting. Do not trust the GitHub API's SPDX guess, which is wrong in both directions: it reports `NOASSERTION` for repositories whose license text carries extra wording, and it reports nothing at all when the license sits in a `licenses/` subdirectory. A repository with no license file is not open source, no matter how much code it has.

## Entry format

One line per entry. Bold name, a middle dot, one sentence, then badges.

~~~markdown
- ⭐ **Project name** · One sentence saying what it does. [![arXiv](https://img.shields.io/badge/arXiv-2408.06292-B31B1B?style=flat-square)](https://arxiv.org/abs/2408.06292) [![Code](https://img.shields.io/github/stars/OWNER/REPO?style=flat-square&logo=github&label=Code&color=181717)](https://github.com/OWNER/REPO) [![Daily Papers](https://img.shields.io/badge/%F0%9F%A4%97-FFD21E?style=flat-square)](https://huggingface.co/papers/2408.06292) [![Site](https://img.shields.io/badge/Site-2EA44F?style=flat-square)](https://example.org)
~~~

The `⭐` prefix marks an editor's pick. Use it sparingly.

### Badge conventions

| Badge | Pattern | Notes |
|:--|:--|:--|
| arXiv | `badge/arXiv-<ID>-B31B1B` | put the **real** arXiv ID in the label, never the word "Paper" |
| Journal | `badge/<Venue>-<Year>-006633` | Nature, Science, NEJM_AI, Nat_Mach_Intell, bioRxiv |
| OpenReview | `badge/OpenReview-Paper-8E44AD` | |
| Code | `github/stars/OWNER/REPO?...&label=Code&color=181717` | one badge carries both the repo link and the live star count |
| License | `badge/<SPDX>-6E7681` | static, from the actual license file |
| Daily Papers | `badge/%F0%9F%A4%97-FFD21E` | only if `https://huggingface.co/papers/<ID>` really resolves |
| Dataset | `badge/%F0%9F%A4%97%20Dataset-FFD21E` | Hugging Face dataset |
| Site | `badge/Site-2EA44F` | official project page |
| Leaderboard | `badge/Leaderboard-F59E0B` | |

Omit a badge rather than pointing it at a third-party mirror. Do not add a stars badge when there is no public repository.

### Checking a Hugging Face Daily Papers link

`https://huggingface.co/papers/<ARXIV_ID>` returns 404 for an ID that is not indexed, so an invented link fails loudly. The link checker paces requests to that host, since it answers bursts with HTTP 429.

## Pull request checklist

- [ ] The resource is directly relevant to AI-assisted or AI-driven scientific work.
- [ ] The paper or primary project page is linked, and the arXiv ID in the badge matches it.
- [ ] The description is one sentence, concrete, and evidence-based.
- [ ] Official code, dataset, environment, or website links are included when they exist.
- [ ] For a workbench, the license was read from the `LICENSE` file.
- [ ] `python3 scripts/check_links.py README.md` passes.
- [ ] Section placement is appropriate and the entry is not duplicated elsewhere.
- [ ] No unrelated formatting or generated files were added.

## Responsible use

Scientific agents generate executable code, laboratory instructions, and claims that look plausible but are wrong. Do not describe a system as reliable, autonomous, or scientifically validated unless the linked work provides evidence. Keep safety limitations visible, especially for tools that can reach a filesystem, a network, instruments, or wet-lab equipment.

By contributing, you agree that your contribution can be distributed under the repository's [CC BY 4.0 license](LICENSE).
