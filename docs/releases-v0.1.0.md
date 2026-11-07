# Certified Structures: Proof-Oriented Connect Four Research

**Connect Four Proof Lab v0.1.0** brings structural combinatorics, exact adversarial search, and independently checkable certificates into one reproducible research release.

The project asks a sharper question than whether an agent plays well: **what can actually be proved against every legal response?** This release turns that distinction into inspectable mathematical objects, verification code, and a documented experimental record.

## The strongest results

- **A structural classification and counting formula.** Universally legal fixed response matchings reduce to vertical components and paired-column cross-prefixes. For odd width `2m + 1` and odd height `2n + 1`, the count after a fixed opening is `(2m − 1)!! · (n + 1)^m`.
- **An obstruction theorem that extends beyond 9×9.** On every nine-column board of odd height at least five, each first-player strategy in that precisely defined fixed-pairing family has a second-player counterattack by ply 16. This is a restricted-strategy result, not a full-game solution.
- **Exhaustive counterattack evidence.** The 9×9 checker replays 328,125 configurations across five representative openings. Additional manuscript audits cover 42,525 configurations at height five and 134,400 at height seven.
- **Certified midgame reasoning.** Twenty-one independent line-cover certificates, including nine forced losses, check every potential winning line. An eight-node endgame tree covers all legal opposing replies. A legal 81-move draw demonstrates why odd board area alone is insufficient.

## Research engineering

The release includes complementary WDL, finite-horizon minimax, and depth-first proof-number implementations; full normalized position-key comparisons in a 128-bit representation; compatible-bound reconciliation; cancellation and checkpointing; and memory-conscious experiments.

The recorded finite-horizon search completes 27 plies from the empty board. The final cache retains 16,650 distinct normalized positions, including 11,051 exact values derived from compatible bounds, with no detected contradictions.

Verification uses separate checking implementations, exact endgame references, exhaustive small-board matching tests, and all 18 WDL-bound/turn-parity conversion cases. The one-command release check builds the code and runs the evidence checks without launching expensive opening searches.

## Included artifacts

- The **13-page research note**, with complete proofs, explicit hypotheses, exact histories, and a reproduction manifest.
- Editable **LaTeX source** and a self-contained finite-witness audit.
- **C++20 and Python source**, independent certificate checkers, cached bounds, experiment logs, and a ready-to-enable CI verification workflow.
- A source-and-evidence archive and SHA-256 checksums for the attached release files.

Run:

```sh
python3 scripts/verify_release.py
```

## Scope and provenance

**The empty 9×9 opening remains unresolved.** No weak or ultra-weak solution, literature-first priority, external peer review, or proof-assistant formalization is claimed. “Independent” describes separate checking implementations.

A research project maintained by **Rishit Pradhan**, developed with AI-assisted implementation, mathematical exploration, and proof drafting. The generalized exact engine is adapted from **Christophe Steininger’s `c4`**, with its upstream attribution and AGPL-3.0 license retained. The repository separates that baseline from the project’s proof development, complementary search implementations, certificate tooling, and release infrastructure.
