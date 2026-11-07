# 9×9 Connect Four: exact weak-solution attempt

The empty board is **not proved solved by this experiment**. This folder contains actual executed searches, reproducible engines, independent tests, reusable subtree bounds, and an independently verified forced-win certificate for one endgame. Self-play win rates are not treated as a proof.

## Latest continuation

The follow-up extended the exact horizon to **27 plies**, added depth-first proof-number search, produced **21 independently checked midgame pairing certificates**, and exhaustively refuted **328,125 strategies in a precisely restricted fixed-pairing family**. The empty board is still unresolved. See [the continuation report](continuation/REPORT.md) and [machine-readable results](continuation/results.json).

## Initial executed result

All five symmetry-distinct first moves remained UNKNOWN after 600 seconds each. The full-game engine made 7,743,306,496 node visits and saved 13,334 significant bound records. The independent horizon engine completed depth 24 with value zero and stopped at its 480-second budget after 7,483,424,768 cumulative node visits, including its unfinished next iteration. Counts include repeated states; there is no meaningful “percent solved” estimate.

No opening move is certified winning, drawing, or losing. These outcomes are unknown, not draws. All compute processes from this attempt have stopped.

## Rules and mathematical labels

Two players alternate dropping one disc into one of nine columns. Gravity applies. The first horizontal, vertical, or diagonal line of four wins; a full board without a win is a draw. No PopOut, wrapping, or misère rules. The original chat exposed the request “9x9 c4” but its generated answers were content references, so these standard rules are an explicit assumption.

Label columns A…I (CLI digits 1…9), and rows 1…9 from bottom to top. A cell is `(c,r)`. There are exactly 180 winning four-cell sets: 54 horizontal, 54 vertical, and 36 in each diagonal direction.

For a legal state S, let V(S) ∈ {−1,0,+1} denote the result for the player about to move. If the previous player just made four, V(S)=−1. A full, unwon board has V(S)=0. Otherwise:

    V(S) = max over legal columns c of −V(play(S,c)).

A weak solution needs the empty-board value and a strategy attaining it against **every** legal reply. A favorable principal variation, neural score, or unbeaten tournament is insufficient.

Horizontal reflection maps c to 10−c. The nine openings have five equivalence classes: {1,9}, {2,8}, {3,7}, {4,6}, {5}. The five independent full-game searches cover these classes. After an opening, their reported score is from **the second player's** perspective. A proved −1 in any opening would establish a first-player win. Timeouts establish no opening value.

The main engine uses a 90-bit column representation, stored in a 128-bit integer. Each column occupies ten bits including a header. Comparing the complete normalized position key avoids probabilistic transposition hits. Normalization includes the upstream engine's dead-stone reduction, which is separately checked during validation.

A loose gravity-only configuration count, including unreachable color counts and already-won boards, is (1+2+…+2^9)^9 = 1023^9 = 1,227,102,111,503,512,992,112,190,463. This is an upper bound, not an estimate of reachable states or required search work. Larger boards cannot be assumed to inherit a smaller board's winning strategy: additional moves change timing and threats.

## Implementations

- `engine/`: research copy of Christophe Steininger's exact generalized solver, upstream commit `fa27f186d2f1bf8e8fd61bfad63454c6e4b0431c`. AGPL-3.0; original license and attribution retained. Uses bitboards, tactical and forced-move pruning, alpha-beta/null-window search, threat-based move ordering, reflection, dead-stone reduction, and transposition bounds. Even-height strategic pruning is guarded upstream and does not apply to this odd-height board.
- Main modifications: 9×9 WDL settings; full position-key identity instead of compressed CRT identity; one worker per process; persisted significant subtree bounds; a timed driver that explicitly returns `UNKNOWN_TIMEOUT` on cancellation.
- `horizon.cpp`: independently implemented iterative-deepening, finite-horizon minimax with full-key transpositions, reflection, immediate wins, compulsory blocks, double threats, and move ordering. A horizon score of zero means unresolved for the full game. A completed nonzero score would establish a forced win/loss; no heuristic evaluation is used.
- `certificate.py`: independent 81-cell rules implementation, exact endgame minimax, and a separate strategy-tree verifier. Verification checks legal play, actual winning leaves, one prescribed move on the winner's turns, and **every legal move** on the opponent's turns. Verification mode does not call minimax.

The full-game engine uses one worker per process to avoid the upstream shared table's unsynchronized access, especially with enlarged multiword entries. The initial five concurrent opening processes used about 2.5 GiB for tables. The current default uses a 16 MiB table and one concurrent job; the continuation report explains the memory experiments. Memory is bounded; this run uses local CPUs, no paid cloud compute or GPU training.

## Evidence and its limits

- `validation-7x6.log`: original standard-board light suite passed after the full-key modification, before switching to 9×9: position/table tests plus 1,000 known endgames in weak, strong, and self-play modes.
- `validation.log`: final stronger 9×9 comparison: 169,887 independently checked positions, 1,493,136 immediate-threat checks, and 100 exhaustive endgame comparisons with no immediate winning move at entry. The endgames comprise 30 wins, 44 losses, and 26 draws. Fixtures are deterministic, sampled from generated games, and are not statistically independent evidence about the opening.
- `validation-horizon.log`: 1,000 horizon comparisons against plain-array exhaustive minimax, on 250 generated positions at depths 1…4.
- `fixtures-9x9.jsonl`: 100 legal endgame histories and independently checked exact values.
- `endgame-certificate.json`: a first-player win from a specified position after move 74. Its eight-node strategy tree covers three opponent replies and wins within three more plies. This is **not a certificate for the empty board**.
- `certificate-verification.json`: verification result for that strategy tree.
- `horizon.jsonl`: completed depths, exact finite-horizon scores, cumulative node calls, elapsed wall time, and timeout status. Node calls include repeated positions and separate iterations; they are not unique states.
- `runs/opening-*/search.log`: initial ten-minute full-game searches and their final statistics.
- `runs/opening-*/data/table-9x9.csv`: reusable significant subtree bounds. These are cached engine results, not standalone independently checked strategy certificates. Bound records and node-work fields cannot be summed to count unique work.
- `results.json`: final machine-readable summary of this attempt.

The published upstream results table leaves 9×9 blank. That observation is not a proof that nobody elsewhere has solved it. The standard 7×6 result is not used as evidence of the 9×9 outcome.

## Reproduce or continue

From this directory, on a machine with Python 3 and a C++20 compiler supporting `__uint128_t`:

    sh build.sh
    mkdir -p data
    ./validate
    ./validate-horizon
    python3 certificate.py endgame-certificate.json
    python3 run.py --seconds 600 --jobs 1 --openings 5
    ./horizon 480 > horizon-next.jsonl

`run.py` resumes saved subtree bounds and creates a new log for each attempt. For example, `--seconds 3600 --jobs 1 --openings 5` concentrates a one-hour budget on the center opening. An `UNKNOWN_TIMEOUT` result must never be relabelled a draw or loss. `horizon` restarts its iterative-deepening search; it has no persistent table. `build.sh` overwrites only local compiled executables.

The continuation added a reusable theorem oracle, proper full-key table mixing, and a proof-number solver. Further progress requires a stronger opening invariant or more effective theorem-guided exact search, followed by an opening strategy certificate if a result is reached. Additional self-play can help propose move orderings, but cannot replace the universal-reply proof obligation.

Sources: https://github.com/ChristopheSteininger/c4 and https://tromp.github.io/c4/c4.html . See `provenance.json` for configuration and upstream identity.

## Formal LaTeX research note

The audited proof manuscript is [main.tex](latex-development-note/main.tex), with a [compiled PDF](latex-development-note/output/pdf/main.pdf). It supplies a full inductive classification proof, corrects the distinction between representative-opening configurations and matching symmetry orbits, and extends the restricted obstruction to every nine-column board of odd height at least five. The opening value remains unresolved.
