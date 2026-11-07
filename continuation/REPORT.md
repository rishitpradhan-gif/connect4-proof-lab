# Continued 9×9 Connect Four research

**The empty board is still unresolved. No weak or ultra-weak solution is claimed.** All experiments in this continuation have stopped. Rules remain standard gravity, two players, four in a row, and no PopOut.

The main new mathematical result is a restricted obstruction: every unconditionally playable fixed response pairing after P1's opening has a counterattack. The main computational improvement is an exact empty-board search completed through 27 plies, up from 24.

## Mathematical progress

### A precisely limited pairing obstruction

[The argument](../pairing-theorem.md) classifies fixed perfect matchings that always prescribe an immediately legal partner reply, including when terminal wins are ignored. Across the five opening reflection classes, that family contains 328,125 structural strategies. Every one was replayed against a concrete counterattack:

- 327,600 fall to a four-disc vertical counterattack.
- The remaining 525 fall to a bottom-row preparation followed by a row-2 horizontal counterattack, by at most game ply 16.

The structural classification was also independently tested against **every abstract cell matching** on four small-board cases. The accepted matchings exactly matched the classification: two for each tested 3×3 opening, three for a 3×5 opening, and twelve for a 5×3 opening. See `pairing-classification-check.json` and its executable checker.

This rules out that fixed response shortcut. It does not rule out adaptive pairings, threat-based strategy changes, or arbitrary first-player winning strategies. No claim is made that this is a new theorem in the published literature.

### Certificate-producing midgame theorem

[A separate rule](../pairing-oracle.md) partitions the remaining cells into vertical dominoes and pairs of currently playable bottom cells. Completing the opponent's pair is always legal. If this blocks all 180 possible opposing winning lines, it proves a nonloss; if the responder's guaranteed cells also form four, it proves a win.

The independent Python constructor/verifier found **21 certificates**, including **nine forced-loss bounds for the player to move**, on the 100 saved exact endgames. All agree with exhaustive minimax. The verifier rejects missing pairs, reversed vertical replies, and unjustified forced-win claims. The certificates explicitly cover the entire remaining board, rather than just one sample continuation.

The optional C++ oracle passed the same comparisons. It did not show a speed improvement in the short opening benchmark, so the reproducible default build disables it. `ENABLE_PAIRING_ORACLE=1 sh build.sh` enables it. The DFPN solver uses the proved rule directly.

### A draw is legally possible

`full-board-draw.json` contains a legally replayed 81-move game ending with 41 P1 discs, 40 P2 discs, and no winning line. Therefore odd board area alone cannot show that draws are impossible. This is not a drawing strategy from the empty board.

## Further searches

### Improved finite-horizon minimax

The earlier table index accidentally ignored middle bits when selecting a bucket. Complete key comparisons prevented false hits, but many central-column positions collided. Full 90-bit key mixing fixes that performance problem. A diagnostic set of 20 middle-column color variations previously occupied one bucket; it now occupies twenty.

With the fix, the search completed **depth 27** with finite-horizon value zero, then timed out while attempting depth 28. Its total was 726,138,880 node visits, including the unfinished iteration. A zero at a depth cutoff means unresolved for the full game; it is not a draw proof. The completed computation does not establish a forced win within 27 plies for either player.

Regression checks include 1,000 comparisons against independent plain-array minimax at depths 1–4 and 100 independently solved endgames searched all the way to their terminal horizon. See `horizon-mixed.jsonl` and `validation-horizon-mixed.log`.

### Exact opening searches and memory behavior

All five opening classes were resumed with 2 GiB tables per process. They remained unknown. Heavy system memory pressure made these runs counterproductive; the five runs added 515,473,863 node visits, and their actual wall times exceeded the nominal twenty-minute budgets. No claim of a fair hardware benchmark is made.

A compact **16 MiB** table recovered much better throughput. A short center-opening run visited 291,002,009 nodes in 60.13 seconds. A focused continuation loaded the merged bounds and added **1,233,283,398** node visits in 701.47 seconds, again without determining the opening value. The default build now uses that smaller table and one worker per process; `run.py` defaults to one concurrent job. Actual elapsed times, rather than nominal budgets, are recorded in `results.json`.

The final cache merger checked 40,272 input records across nine files, retained **16,650 distinct normalized position keys**, and determined exact values for **11,051** of those keys from compatible bounds. It found **no contradictory bounds**. The earliest cached position is at ply 16. These are subtree facts, not opening results. Cached engine bounds are not standalone strategy certificates.

### Depth-first proof-number search

`dfpn.cpp` searches the Boolean proposition “P1 can force a win,” treating P1 moves as OR nodes and P2 moves as AND nodes. Terminal results and the proved pairing theorem close leaves; no heuristic score is accepted as a proof. Table entries compare full position keys. Move ordering affects search order only.

The corrected solver passed all 100 independently solved endgames. Every one of the 18 possible combinations of player parity, WDL bound type, and bound value was checked for sound conversion to the Boolean proposition. The final seeded regression also passed after loading the merged bounds.

The focused seeded run loaded the original 14,548-position merge and made **348,815,360 DFPN visits**, with 348,710,289 expansions and 806,790,489 table hits. It timed out after 745.872 seconds. Its root proof/disproof numbers were 23,461 and 28,870. Neither is zero, so the result is **unknown**. These numbers are search bookkeeping, not probabilities or a percentage complete.

`merged-bounds-seed.csv` preserves that run's exact input. `merged-bounds.csv` contains the later final merge. Raw DFPN calls and alpha-beta node visits are different metrics and are not added together as unique positions.

An early development regression caught a move-filter API mismatch; that failed build's opening output was discarded. A first validated timeout run also preceded proper exception-state restoration, so its proof-number metadata is superseded. The corrected and seeded logs above are the results used here.

## Files and continuation commands

The machine-readable summary is `results.json`. The mathematical arguments are `../pairing-theorem.md` and `../pairing-oracle.md`. Important independently checked artifacts are:

- `pairing-refutation-certificates.json`: 525 complete matchings and counterattack histories for the nontrivial bottom-pair cases.
- `midgame-pairing-certificates.json`: 21 explicit midgame proof certificates.
- `full-board-draw.json`: a fully replayable draw witness.
- `merged-bounds.csv`: all final reusable cached bounds.

From the research directory:

    sh build.sh
    ./dfpn --validate continuation/merged-bounds.csv
    ./validate-horizon
    python3 pairing-proof.py
    python3 pairing-refutations.py
    python3 continuation/check-pairing-classification.py
    ./dfpn 600 5 continuation/merged-bounds.csv
    ./horizon 600 > continuation/horizon-next.jsonl

For an exact-search continuation using the final merge, create a separate run directory with a `data/` subdirectory, copy `continuation/merged-bounds.csv` to `data/table-9x9.csv`, then run the absolute path to `attempt` from that directory, with seconds and a digit history as arguments. The driver also supports a local `stop.request` file for cooperative cancellation with statistics and checkpoints preserved.

The original published reference solvers are linked in the parent README. A newly reviewed [preliminary neural results matrix](https://hzyhhzy.github.io/boardgames/games.html) labels 9×9 a first-player win, but supplies no exact opening proof or certificate here. It is not used to establish the outcome. Allis's [thesis](https://tromp.github.io/c4/connect4_thesis.pdf) and [WeakC4](https://2swap.github.io/WeakC4/explanation/) were reviewed for strategic-rule and compact-proof approaches; their standard-board results do not determine this board.

## Remaining obligation

An ultra-weak solution still requires a proof that the empty board is won for a particular player or drawn. The computations and restricted theorems here do not establish that value. Further work needs either a stronger strategic invariant that applies near the opening, or substantially more effective theorem-guided exact search. No unbeaten-play or neural-confidence claim is substituted for that obligation.
