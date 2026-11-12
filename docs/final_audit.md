# Final objective audit
This is a heuristic evidence review, not the instructor's grade. Maxima follow the supplied rubric; ranges acknowledge unresolved academic/external conditions. No 100/100 claim.

|Criterion|max|Supported range|Evidence / status|Impact / correction|
|---|---:|---:|---|---|
|Python software|20|18-20|app.py, nk_oil modules, 7 UI tabs, review/report; AppTest passes|Local single-user only; no unsupported production promise|
|Data / preprocessing|15|11-14|Real full 258,387 rows, chunking, exact pivot reconciliation, quality exports|Source below recommended size; instructor exception external|
|DB / SQL|10|9-10|Normalized dimensions/flags, ER, 8 individual executed queries; fixture/full integration|LAG absent hours distinct from NULL; ROWS vs clock hours explicit|
|EDA / visuals|15|12-14|5 offline HTML figures, grouped stats/patterns, paired coverage correlations|Different type sensors; no causal comparison or unlike-unit average|
|Methods / comparison|15|11-14|No-change, causal rolling and CUSUM; same test scope, threshold sensitivity, measured costs|No verified ground truth; counts cannot rank accuracy; repeated CUSUM alerts disclosed|
|Reproducibility / quality|10|8-10|Pinned requirements; clean venv 21 tests, pip check, Ruff, offline sample test, hashes|No-Git archive startup fixed; code hashes added for future runs|
|Report|5|4-5|9-page real PDF + complete Markdown, producing script and evidence|Real authors/contributions not provided; explicit placeholder|
|Presentation / defense|10|8-10|12 editable slides, native charts/table, notes, defense guide; PowerPoint render/edit-copy test|Instructor timing/required institutional template unknown|

Combined heuristic 81-97/100; this does not predict the instructor's score. Extensions add no guaranteed points beyond maxima.

## Repairs in final review
- Corrected Git-free source archive handling in run manifest and integer validation of n_obs.
- Added verified offline sample fallback test and clean-environment installation/test evidence.
- Corrected Russian wording from nonzero to nonmissing: zero sensor readings remain valid source observations.
- Native slide chart values round to six decimal places for Excel's precision limit; exact research values remain CSV/JSON. Line chart uses straight segments, no smoothing.
- PowerPoint render detected text-fit issues; revised footer, caveat boxes and closing line. Final render/QA record saved separately.

## Pass / external status
PASS: implementation, full source execution, 8 SQL, pivot, sample/full app smoke, temporal invariants, product review→report, tests and clean install. PASS artifacts after visual final QA: academic PDF and editable PPTX.

EXTERNAL: dataset size exception; SCADA year/timezone validation; instructor topic approval; actual team names/contributions; exam/Moodle date and submission. GitHub authorized owner qtj4 only; connector and existing credential identities verified. Private qtj4/nk-oil-well-monitoring contains all phase commits and deliverables, pushed without force. No repository was published to a different account.
