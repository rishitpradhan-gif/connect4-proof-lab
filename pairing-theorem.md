# Why an always-playable fixed response pairing cannot solve the opening

This is a limited negative result, not a solution of 9×9 Connect Four. It is a deduction made in this project; no claim of literature novelty is made.

## Precisely defined strategy family

P1 chooses an opening bottom cell q. P1 then fixes a perfect matching M of the 80 remaining cells. Whenever P2 plays x, P1 plays its mate M(x), unless the game has already ended. We impose the stronger, unconditional legality property: the prescribed response must be immediately playable after every P2 move from every pair-completed gravity position, even if wins are ignored. This excludes matchings whose illegal responses are unreachable only because P1 has already won. It also excludes adaptive pairings, threat-specific replies, and switching plans.

The result is that **every strategy in this specified family can be beaten by P2**, within at most 16 game plies. This does not establish that P2 can beat arbitrary P1 play.

## Structural classification

Contract each matched pair to one node. A pair containing a lower cell in a column is a prerequisite of pairs containing higher cells in that column. A dependency cycle is incompatible with unconditional legality: in the first unfinished cycle, some bottommost available cell has an unavailable mate. A same-column pair must consist of consecutive cells.

For a cross-column pair {u,v}, let A(u) and A(v) be the transitively closed sets of prerequisite pairs beneath its endpoints. Unconditional legality requires A(u)=A(v). Otherwise the smaller endpoint prerequisite ideal can be completed and one endpoint played while the mate remains unsupported. Conversely, equality makes the response legal once either endpoint is available.

These facts force the following form. A column can either consist entirely of vertical domino pairs, or it can be partnered with one other column. Two previously disjoint column components can first be joined only at their lowest remaining cells: their prerequisite sets are disjoint and can be equal only when both are empty. Once joined, their cross-column pairs must form a consecutive prefix. As soon as either column takes a vertical domino, it introduces a prerequisite unique to that column, so the columns cannot be joined again above it. No third column can join an existing component, because its previously disjoint prerequisite set cannot equal the existing nonempty one.

Thus partnered columns have k cross-column pairs at their lowest k available levels, followed by independent vertical dominoes above. P1's opening column has eight empty cells; every other column has nine. Different remaining parities cannot share a cross-pair prefix and then both finish with vertical dominoes. The opening column therefore consists of four vertical dominoes. The other eight columns form four column pairs. Each pair has an odd prefix length k ∈ {1,3,5,7,9}.

There are 7×5×3×1=105 matchings of those eight columns, and 5^4 prefix choices per column matching. Five opening reflection classes give 5×105×5^4 = **328,125 structural strategies**.

## Counterattack when a cross prefix has length at least three

P2 plays four consecutive moves in one column of that pair. P1's first three prescribed responses lie in the other column. P2 connects vertically on its fourth move. P1 cannot already have won: its discs consist only of the opening disc in a distinct column and up to three discs in the reply column. The game ends by ply 8.

This covers 327,600 structural strategies.

## Counterattack when every prefix has length one

Only the bottom cells are cross-paired. Above the bottom row, each column is vertically paired as (row 2,row 3), (row 4,row 5), (row 6,row 7), (row 8,row 9).

P2 first fills the four bottom pairs, choosing one endpoint of each as its own move. P1 receives the other endpoint, in addition to q. An orientation avoiding a P1 bottom-row four always exists. Choose each orientation uniformly and independently. A bottom four-cell interval containing q can be wholly P1 only if its other three cells belong to distinct pairs, and then has probability 1/8. An interval excluding q has probability at most 1/16. There are six intervals, at most four containing q. By the union bound, the probability of *any* P1 bottom-row four is at most

    4/8 + 2/16 = 5/8 < 1.

Intervals containing both endpoints of a pair have probability zero, so this upper bound is conservative. Thus an orientation without a P1 bottom four exists; the program explicitly finds one for every matching.

If P2 wins while filling the bottom row, the counterattack is already complete. Otherwise P2 plays row 2 in columns A, B, C, D. P1's replies are row 3 in those columns. P2 connects horizontally on the fourth row-2 move. P1 cannot win earlier: its bottom row has no four, it owns no row-2 cells, and it has at most three row-3 cells before the winning P2 move. It has no row-4 discs. The game ends by ply 16.

There are 525 such cases across the five opening classes. Their full response matchings and legal counterattack histories are saved in `continuation/pairing-refutation-certificates.json`.

## What was checked

`python3 pairing-refutations.py` constructs every one of the 328,125 structural matchings and replays the prescribed counterattack, checking gravity, both players' wins, and actual partner replies. The structural classification above is a mathematical argument; the enumeration is exhaustive over that classification, not over all abstract matchings of 80 cells.

The mixed-integer CEGIS experiment in `pairing.py` searched a larger matching formulation and rejected 349 illegal candidates before timing out. That timeout is not an infeasibility proof. The classification and explicit counterattacks provide the restricted negative result instead.

An independent explicit paired-state legality checker also exhausts all 105 cell matchings on each of two 3×3 cases and all 135,135 cell matchings on each of a 3×5 and 5×3 case. Its accepted matchings exactly match the structural classification. This is a useful check on the argument, not a replacement for its general proof. See `continuation/check-pairing-classification.py`.
