# LaTeX developmental research note

Open `main.tex` in the Codex LaTeX editor or any standard LaTeX editor.
The source is self-contained: bibliography, exact board witnesses, theorem
statements, and proofs are embedded in that file.

The empty 9×9 game's value is not established. The principal mathematical
result is a classification of universally legal fixed response matchings,
followed by an obstruction theorem for nine columns and every odd height
at least five. These are restricted-strategy results, not a game solution.

## Build

With Tectonic:

    tectonic --keep-logs --outdir output/pdf main.tex

With a standard TeX distribution:

    pdflatex main.tex
    pdflatex main.tex

The shipped PDF is `output/pdf/main.pdf`.

## Check exact finite witnesses

From this directory:

    python3 audit_note.py

This uses only the standard library. It verifies the arithmetic draw
certificate and explicit endgame, and checks all classified counterattacks
at heights five and seven. It writes `audit_results.json` and prints the
same results. The infinite-family theorem is proved in the paper; finite
checks do not replace that proof.

Further project evidence is under `../continuation/`. This note does not
claim proof-assistant verification, peer review, or a priority result.
