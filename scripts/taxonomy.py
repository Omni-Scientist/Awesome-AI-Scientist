#!/usr/bin/env python3
"""Maps the README's 13 sections onto the site's 6 browse categories.

Every mapping key is a literal README heading. build_site asserts that the
mapping consumes all 497 entries, so a renamed heading upstream fails the
build instead of silently dropping a section from the site.
"""

# category slug -> (nav label, page title, one-line intro, [(sub slug, sub label, README source)])
# A README source is either "Section" or "Section > Subsection".
CATEGORIES = [
    (
        "ai-scientists",
        "AI Scientists",
        "AI Scientists",
        "Systems that run several research stages as one loop, and the agents "
        "that work alongside a human researcher.",
        [
            ("end-to-end", "End-to-End", "End-to-End AI Scientists",
             "Systems that connect ideation, experimentation, analysis and writing into a single loop."),
            ("co-scientists", "Co-Scientists", "Co-Scientists & Research Agents",
             "Agents that assist a human researcher rather than replace the loop."),
        ],
    ),
    (
        "research",
        "Research",
        "Research Stages",
        "Work aimed at one stage of the research process: forming an idea, "
        "reading the literature, running the experiment, writing it up, checking it.",
        [
            ("ideation", "Ideation", "Research Stages > Ideation & hypothesis generation",
             "Generating and ranking research hypotheses."),
            ("literature", "Literature", "Research Stages > Literature review & retrieval",
             "Finding, reading and synthesising the existing literature."),
            ("experiments", "Experiments", "Research Stages > Experimentation & code execution",
             "Designing experiments, writing code and running them."),
            ("writing", "Writing", "Research Stages > Scientific writing",
             "Turning results into papers, figures and posters."),
            ("review", "Review", "Research Stages > Peer review & verification",
             "Reviewing, verifying and checking scientific claims."),
            ("knowledge", "Knowledge & Tools", "Research Stages > Knowledge, tools & environments",
             "Knowledge bases, tool interfaces and the environments agents act in."),
        ],
    ),
    (
        "domains",
        "Domains",
        "Scientific Domains",
        "Systems built for one science rather than for research in general.",
        [
            ("chemistry", "Chemistry & Materials", "Domains > Chemistry & materials",
             "Synthesis planning, materials discovery and self-driving chemistry labs."),
            ("biology", "Biology & Medicine", "Domains > Biology & medicine",
             "Biomedical discovery, therapeutic reasoning and clinical research."),
            ("physics", "Physics & Earth", "Domains > Physics, astronomy & earth",
             "Physics, astronomy, climate and earth-system research."),
            ("mathematics", "Mathematics", "Domains > Mathematics",
             "Theorem proving, conjecture generation and mathematical discovery."),
            ("social", "Social Science", "Domains > Social science & humanities",
             "Computational social science, economics and the humanities."),
        ],
    ),
    (
        "resources",
        "Resources",
        "Resources",
        "The things you can actually download and run: platforms, models, "
        "corpora and environments.",
        [
            ("workbenches", "Workbenches", "Open-Source Workbenches",
             "Platforms you can clone, install and drive today."),
            ("models", "Foundation Models", "Scientific Foundation Models",
             "Open or landmark models that scientific agents build on."),
            ("datasets", "Datasets", "Datasets, Corpora & Environments",
             "Corpora, tools, simulated worlds and domain data that agents feed on."),
        ],
    ),
    (
        "benchmarks",
        "Benchmarks",
        "Benchmarks & Leaderboards",
        "How the field measures itself, and where the current ceiling actually sits.",
        [
            ("benchmarks", "Benchmarks", "Benchmarks & Evaluation",
             "Tests of scientific knowledge, coding, reproducibility and whole research workflows."),
            ("leaderboards", "Leaderboards", "Leaderboards & Live Trackers",
             "Live scoreboards that track the current state of the art."),
        ],
    ),
    (
        "learn",
        "Learn",
        "Learn",
        "Surveys, safety work, talks and other reading to get oriented in the field.",
        [
            ("surveys", "Surveys", "Surveys & Position Papers",
             "Surveys and position papers mapping the field."),
            ("safety", "Safety & Policy", "Safety, Ethics & Policy",
             "Dual-use risk, research integrity, authorship and policy."),
            ("tutorials", "Tutorials & Talks", "Tutorials, Blogs & Talks",
             "Technical reports, lab blogs and journal commentary."),
            ("lists", "Related Lists", "Related Awesome Lists",
             "Neighbouring reading lists worth knowing about."),
        ],
    ),
]

# Groups listed here are ordered newest first instead of in README order.
SORT = {"ai-scientists/end-to-end"}


def sources():
    """Every README source string the mapping claims, for coverage checks."""
    out = []
    for _, _, _, _, subs in CATEGORIES:
        out += [src for _, _, src, _ in subs]
    return out


def find(sections, source):
    """Resolve 'Section' or 'Section > Subsection' to its parsed node."""
    if " > " in source:
        top, sub = source.split(" > ", 1)
        for s in sections:
            if s["title"] == top:
                for x in s["subs"]:
                    if x["title"] == sub:
                        return x
        raise KeyError(f"README subsection not found: {source}")
    for s in sections:
        if s["title"] == source:
            return s
    raise KeyError(f"README section not found: {source}")


def entries_of(node):
    """All entries under a node, including any subsections it owns."""
    out = list(node.get("entries", []))
    for sub in node.get("subs", []):
        out += sub["entries"]
    return out

# Per-category colour and icon. Mid-luminance hues chosen to stay legible on
# both the white and the near-black ground, so one value serves both themes.
STYLE = {
    "ai-scientists": ("#12B5A5", "flask"),
    "research":      ("#4C82F7", "loop"),
    "domains":       ("#9268F7", "globe"),
    "resources":     ("#F5892B", "stack"),
    "benchmarks":    ("#F0509A", "chart"),
    "learn":         ("#22B455", "book"),
}



# Twemoji codepoints for every category and sub-category. Each is the emoji the
# matching README heading already carries, except the four noted, where the
# README's choice would repeat an icon already used on the same page.
EMOJI = {
    "ai-scientists":               "1f916",   # README: 🤖 End-to-End AI Scientists
    "ai-scientists/end-to-end":    "1f501",   # loop; README's 🤖 is the category icon
    "ai-scientists/co-scientists": "1f52c",   # README: 🔬 Co-Scientists & Research Agents
    "research":                    "1f52d",   # README: 🔭 Research Stages
    "research/ideation":           "1f4a1",   # README: 💡 Ideation & hypothesis generation
    "research/literature":         "1f4d6",   # README: 📖 Literature review & retrieval
    "research/experiments":        "1f9ea",   # README: 🧪 Experimentation & code execution
    "research/writing":            "270d",    # README: ✍️ Scientific writing
    "research/review":             "1f9fe",   # README: 🧾 Peer review & verification
    "research/knowledge":          "1f9e0",   # README: 🧠 Knowledge, tools & environments
    "domains":                     "1f30d",   # README: 🌍 Domains
    "domains/chemistry":           "2697",    # README: ⚗️ Chemistry & materials
    "domains/biology":             "1f9ec",   # README: 🧬 Biology & medicine
    "domains/physics":             "1fa90",   # planet; README's 🔭 is the Research icon
    "domains/mathematics":         "2797",    # README: ➗ Mathematics
    "domains/social":              "1f3db",   # README: 🏛️ Social science & humanities
    "resources":                   "1f9f0",   # README: 🧰 Open-Source Workbenches
    "resources/workbenches":       "1f5a5",   # README: 🖥️ End-to-end research platforms
    "resources/models":            "1f9e0",   # README: 🧠 Scientific Foundation Models
    "resources/datasets":          "1f4e6",   # README: 📦 Datasets, Corpora & Environments
    "benchmarks":                  "1f4ca",   # README: 📊 Benchmarks & Evaluation
    "benchmarks/benchmarks":       "1f3af",   # target; README's 📊 is the category icon
    "benchmarks/leaderboards":     "1f3c6",   # README: 🏆 Leaderboards & Live Trackers
    "learn":                       "1f393",   # README: 🎓 Tutorials, Blogs & Talks
    "learn/surveys":               "1f9ed",   # README: 🧭 Surveys & Position Papers
    "learn/safety":                "1f6e1",   # README: 🛡️ Safety, Ethics & Policy
    "learn/tutorials":             "1f4f0",   # README: 📰 Blogs & technical reports
    "learn/lists":                 "1f517",   # README: 🔗 Related Awesome Lists
}

def icon(key, size=20, base=""):
    """The category's own emoji, as published artwork rather than a drawn glyph."""
    assert key in EMOJI, f"no icon assigned to {key}"
    return ('<img class="cat-ico" src="%sassets/icons/%s.svg" alt="" '
            'width="%d" height="%d" loading="lazy">'
            % (base, key.replace("/", "--"), size, size))
