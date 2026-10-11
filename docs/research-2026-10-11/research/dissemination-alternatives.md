# Dissemination of the two polyhedral-packing papers

**Alejandro Zarzuelo — publication routes checked 11 October 2026.**

The recommended route is a frozen GitHub release and **Zenodo archival record**, followed by a **recognized preprint repository when author eligibility is settled**, with **Experimental Mathematics** as the principal peer-review target for Paper 2. Rapid public availability, a permanent citation, and journal recognition serve different purposes. A repository DOI gives a stable citation; it does not constitute acceptance by a mathematics journal.

This document prepares the decision. No repository outside GitHub has received a deposit, no journal has received a submission, and no endorsement or catalogue request has been sent.

## arXiv: the reported obstacles are real

arXiv's own announcement confirms that, from **1 October 2026, each submitter is limited to two submissions per calendar month across all categories**. This is a general policy, not merely a restriction specific to this author. The official announcement is readable on [arXiv's LinkedIn account](https://www.linkedin.com/posts/arxiv_as-of-october-1-arxiv-is-updating-our-submission-activity-7511500706516836352-Of8s); its [support portal](https://arxiv-org.atlassian.net/servicedesk/customer/portal/2) points to the [1 October policy announcement](https://blog.arxiv.org/2026/10/01/updated-rate-limit-policy/). The blog itself presented an automated browser challenge during this check, so finer counting rules were not inferred from it.

The two current papers could occupy two available monthly submission slots, but that does not solve the endorsement obstacle or accommodate other papers in the same month. [The current endorsement page](https://info.arxiv.org/help/endorsement.html) requires endorsement before a first submission or entry into a new category. Its institutional route combines a qualifying institutional email with claimed authorship of existing work; institutional email alone is not a guaranteed exemption. One personal endorsement from a qualified author is an alternative. An endorser establishes subject suitability, not scientific correctness.

HAL's optional transfer to arXiv should not be treated as a way to bypass arXiv's rules. A later arXiv version remains useful for visibility, but it should not delay an approved release elsewhere.

## The three priority routes

| Route | What it contributes | Speed supported by the official source | Suitability and unresolved conditions |
|---|---|---|---|
| **Zenodo, first for a frozen archive** | A citable record for the papers, data, exact certificates, figures, and software; versioned DOI | The documented workflow publishes when the author confirms publication and assigns a DOI. There is no advertised referee queue for a direct deposit outside a curated community. | [Policy](https://about.zenodo.org/policies/) accepts all research fields and permits anyone to register and deposit material they have rights to. No endorsement or two-per-month manuscript limit is specified in the checked policy; that is not a promise of unlimited use. |
| **HAL, preferred academic preprint alternative if affiliation metadata can be completed honestly** | Research manuscripts in established scholarly infrastructure with permanent HAL identifiers | [Moderation guidance](https://doc.hal.science/en/check-of-deposits/) says manual checks may take a few days, depending on workload. | HAL covers French and international, public and private research. It does not peer-review the science. The [deposit form](https://doc.hal.science/en/deposit_new/) requires at least one affiliation. Independent-author handling needs confirmation before making this the critical path; no affiliation should be invented. |
| **Experimental Mathematics, principal journal target for Paper 2** | Independent mathematical peer review and an accepted journal article | [Publisher metrics](https://www.tandfonline.com/action/journalInformation?journalCode=uexm20&show=aimsScope) report 13 days to first decision, 133 days to first post-review decision, and 85 days from acceptance to online publication. | The scope explicitly includes experiment-led conjectures and evidence for significant hypotheses. The first decision can be a desk rejection. These are averages, not a promise. The subscription route has no APC; optional open access may carry an APC. |

These routes complement one another. Zenodo is the strongest verified option for obtaining a durable citation without waiting for sponsorship. HAL offers a more focused scholarly-manuscript setting, subject to the unresolved independent-author metadata issue. Experimental Mathematics is the best apparent fit for the mathematical pattern paper; that assessment is editorial judgment rather than a prediction of acceptance.

### What to deposit and how to identify it

For Zenodo, use a tagged release containing the exact data freeze, source commit, verifier, scripts, and viewer. Give the release its own software/data citation. Each paper may have a separate preprint record if Zenodo is chosen as the primary manuscript host, linked to that archive and to its companion paper. If HAL or another preprint server hosts the manuscripts, Zenodo can instead archive the reproducibility package while linking to the manuscript identifiers. Avoid creating several independent copies of the same manuscript simply to accumulate identifiers.

[Zenodo's quick-start guide](https://help.zenodo.org/docs/get-started/quickstart/) documents direct publication and automatic DOI assignment. [Versioning guidance](https://zenodo.org/help/versioning) distinguishes the DOI of a particular release from a concept DOI covering all versions: cite the version DOI for the dataset actually analyzed. Published files require a new version for subsequent changes. [The platform's institutional description](https://about.zenodo.org/) places it within CERN/OpenAIRE research infrastructure; this is archival credibility, not an endorsement of the paper's conclusions. A [community submission](https://help.zenodo.org/docs/share/submit-for-review/) adds curator review and can delay publication; direct publication is available without selecting a community.

[HAL's principles](https://static.ccsd.cnrs.fr/principles/) establish international and public/private scope, timestamps, stable identifiers, and long-term preservation. HAL identifiers provide citations even where no new DOI is minted. Link any existing archive DOI in the metadata. [HAL's preprint workflow](https://doc.hal.science/en/deposit/submitting-preprint-to-publishing-service/) can forward a manuscript to participating Episciences journals, but selecting that option is a separate journal submission, not merely archiving it.

## Other established preprint options

| Service | Verified practical position | Recommendation for these papers |
|---|---|---|
| **Preprints.org** | Its [author instructions](https://www.preprints.org/instructions-for-authors) cover Computer Science and Mathematics, technical notes, data descriptors, and hypotheses. Screening typically takes 24 hours during working days. It requires an account and scientific/identity checks, rather than an arXiv endorser. Excessive submissions or similar manuscripts can be declined. | A plausible fast fallback if HAL's affiliation requirement proves inconvenient. Screening is not peer review. It should be selected for accessibility and workflow, without describing its posting as prestigious journal acceptance. |
| **SSRN Mathematics Research Network** | [SSRN lists MathRN](https://www.ssrn.com/index.cfm/en/prn/prn-research-paper-series/). [Current submission rules](https://www.elsevier.support/ssrn/answer/get-started) require scholarly research with original findings and rigorous methodology. [Processing guidance](https://www.elsevier.support/ssrn/answer/ssrn-review-process), updated July 2026, allows up to 10 business days. | A recognizable Elsevier-operated option; less attractive when immediate availability is paramount. No two-per-month cap was found in the checked instructions, but acceptance and speed are not guaranteed. |
| **Research Square** | Its [submission guide](https://support.researchsquare.com/support/solutions/articles/6000271843-how-do-i-submit-a-preprint-) describes prescreening, DOI assignment, and typical posting within 24–48 hours. It asks for primary institution information. | An additional candidate; independent-author handling and exact mathematical eligibility were not established by the checked guide, so it should not be the first recommendation. |
| **OSF generalist preprints** | [COS continued the suspension indefinitely](https://www.cos.io/blog/update-on-future-of-osf-preprints?hs_amp=true) after suspending new generalist submissions in August 2025. Community servers remain active. | Do not recommend the generalist server. A disciplinary service would require a genuine match to its own scope. |

No fixed two-per-month cap or personal-endorsement mechanism was identified in the checked HAL/Zenodo instructions. This statement describes the public documentation inspected; it cannot certify the absence of every anti-abuse limit or account-specific restriction.

## Peer-review alternatives and the scientific contribution they need

**Paper 2: Experimental Mathematics is the leading choice.** Present the hypotheses with a precise domain, mechanism, possible falsifier, and consequence. Explain what is proved by the feasibility certificates, what is observed in the archive, and what is predicted beyond it. The venue's scope rewards this kind of experimental mathematics and asks for repeatable computational evidence. Its fit is stronger than an argument based only on the number of records or a proposed crystallization application.

**Paper 1: Journal of Computational Geometry is a serious alternative.** [JoCG](https://jocg.org/index.php/jocg/about) is a diamond open-access journal: peer-reviewed articles and supplements are freely available, and it charges no publishing fees. Its [review criteria](https://jocg.org/index.php/jocg/about/review-criteria) expressly consider experimental and applied papers alongside theoretical work. Its [submission policy](https://jocg.org/index.php/jocg/about/submissions) permits prior online posting. A strong submission should center on the geometric generalization, exact certificate design, and evidence that the method offers a substantial computational-geometric contribution. No official fast-turnaround promise was found.

**Discrete & Computational Geometry is a more demanding geometric target.** Its [scope](https://link.springer.com/journal/454/aims-and-scope) explicitly covers polytopes, packing, configurations, geometric algorithms, and crystallography, and welcomes animated supplements. It is a natural destination if the program develops substantial structural theorems or optimality proofs. It should not be chosen on an assumed speed advantage.

**Mathematical Programming Computation is relevant if the methods contribution becomes a comparative optimization study.** Its [scope](https://link.springer.com/journal/12532/aims-and-scope) requires source code and data and substantial computational testing for new techniques/applications. The present method could fit after controlled comparisons, ablations, and reproducible performance benchmarks establish an optimization contribution. That extra work makes it a lower priority for immediate dissemination.

Journal submission should be sequential for each manuscript. Public preprinting can occur while a compatible journal reviews the work; it does not permit simultaneous consideration of the same manuscript by multiple journals. The two papers should cross-cite and make their distinct contributions explicit.

## The OEIS analogy and an appropriate packing catalogue

The current container-scale tables consist of real or algebraic values, so an arbitrary conversion of decimals to integers would not produce a canonical integer sequence. [OEIS's contribution guidance](https://oeis.org/wiki/Welcome) asks for well-defined sequences of general interest, ideally infinite. A future exact family might yield a natural integer sequence—such as a proven capacity at integer scale—but that would be a separate mathematical result.

[Erich Friedman's Packing Center](https://erich-friedman.github.io/packing/) is a more directly relevant record catalogue. It already includes cubes, tetrahedra, and octahedra in cubes. Its [contributor instructions](https://erich-friedman.github.io/packing/submit.html) ask for attribution, a configuration image, its size, and a description of the generating program. After the papers and comparisons are settled, a separately authorized request could offer certified improvements and propose additional solid/container families. Inclusion is at the curator's discretion; it is not peer review or a guaranteed publication route.

For Alejandro Zarzuelo's wider all-pairs programme, the repository's linked coordinates, exact certificates, attribution, and rotating constructions already provide the right foundation for a scientific catalogue. A frozen DOI archive plus an independently reviewed pattern paper would make that resource substantially easier to cite and build upon.

## Proposed order after author review

1. Approve the two papers and their attribution, precise hypotheses, and external-record comparisons.
2. Tag the reproducibility release on GitHub; prepare a Zenodo archive with exact version citation and links to both manuscripts.
3. Choose one primary manuscript host: HAL if honest affiliation metadata is supported; otherwise Zenodo or Preprints.org. Do not wait for an arXiv sponsor to establish an accessible scientific record.
4. Submit Paper 2 to Experimental Mathematics, with Paper 1 linked as its method reference. Consider JoCG for Paper 1 if the geometric-method contribution meets its criteria; otherwise assess Experimental Mathematics for it as a complementary methods paper.
5. Add arXiv versions later if endorsement becomes available and the relevant monthly slots are free. Consider a packing-catalogue request only when separately authorized.

The present authorization remains **local files and the existing GitHub repository only**. The preceding sequence is a publication recommendation, not an instruction executed against an external service.
