"""Build the case-study presentation from the run artifacts.

Run:  .venv/bin/python build_slides.py
Out:  content/gaapo_outputs_v2/GAAPO_case_study_slides.pptx
"""
import json
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent
ART = ROOT / "content/gaapo_outputs_v2"
FIG = ART / "figures"

INK = RGBColor(0x1B, 0x27, 0x33)
MUTED = RGBColor(0x5A, 0x6B, 0x7B)
RED = RGBColor(0xC1, 0x55, 0x4F)
BLUE = RGBColor(0x2A, 0x6F, 0x97)
SAND = RGBColor(0xF6, 0xF3, 0xEE)
GREY = RGBColor(0xE6, 0xEA, 0xEF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Arial"
W, H = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]

S = json.loads((ART / "probe" / "probe_summary.json").read_text()) if (
    ART / "probe" / "probe_summary.json").exists() else None


# ---------------------------------------------------------------- helpers
def textbox(slide, text, left, top, width, height, size=18, bold=False,
            color=INK, align=PP_ALIGN.LEFT, italic=False, spacing=1.0,
            anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = FONT
    return box


def rule(slide, top, color=RED, width=Inches(0.9), left=Inches(0.85), thick=Pt(3)):
    bar = slide.shapes.add_shape(1, left, top, width, thick)
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    bar.shadow.inherit = False


def frame(title, kicker=None):
    slide = prs.slides.add_slide(BLANK)
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = WHITE
    if kicker:
        textbox(slide, kicker.upper(), Inches(0.85), Inches(0.62), Inches(11.6),
                Inches(0.3), size=11.5, bold=True, color=MUTED)
    textbox(slide, title, Inches(0.85), Inches(0.95), Inches(11.6), Inches(1.0),
            size=28, bold=True, color=INK, spacing=0.95)
    rule(slide, Inches(1.92))
    return slide


def bullets(slide, items, left=Inches(0.85), top=Inches(2.25), width=Inches(6.2),
            size=17, space=12, gap=0.0):
    box = slide.shapes.add_textbox(left, top + Inches(gap), width,
                                   H - top - Inches(1.0))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            head, body = item
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(space)
            p.line_spacing = 1.12
            r = p.add_run()
            r.text = head
            r.font.size = Pt(size)
            r.font.bold = True
            r.font.name = FONT
            r.font.color.rgb = INK
            r2 = p.add_run()
            r2.text = " " + body
            r2.font.size = Pt(size)
            r2.font.name = FONT
            r2.font.color.rgb = MUTED
        else:
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(space)
            p.line_spacing = 1.12
            r = p.add_run()
            r.text = item
            r.font.size = Pt(size)
            r.font.name = FONT
            r.font.color.rgb = MUTED
    return box


def picture(slide, name, left=None, top=None, width=None, height=None):
    path = FIG / name
    if not path.exists():
        return None
    kw = {}
    if width:
        kw["width"] = width
    if height:
        kw["height"] = height
    pic = slide.shapes.add_picture(str(path), left or Inches(0.9), top or Inches(2.3), **kw)
    return pic


def fact(slide, big, label, left, top, width=Inches(3.2), color=RED):
    textbox(slide, big, left, top, width, Inches(0.75), size=40, bold=True, color=color)
    textbox(slide, label, left, top + Inches(0.72), width, Inches(0.9), size=13,
            color=MUTED, spacing=1.1)


def table(slide, rows, left, top, width, height, col_widths=None, header=True,
          size=13):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), left, top, width, height)
    tbl = shape.table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Emu(int(width * cw / total))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.03)
            cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if header and r == 0:
                cell.fill.fore_color.rgb = INK
            else:
                cell.fill.fore_color.rgb = WHITE if r % 2 else SAND
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
            run = p.add_run()
            run.text = str(val)
            run.font.size = Pt(size)
            run.font.name = FONT
            run.font.bold = (header and r == 0)
            run.font.color.rgb = WHITE if (header and r == 0) else INK
    return tbl


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def footer(slide, n):
    textbox(slide, "GAAPO: replication audit and adaptive operator selection",
            Inches(0.85), H - Inches(0.5), Inches(8), Inches(0.3), size=9, color=MUTED)
    textbox(slide, str(n), Inches(12.1), H - Inches(0.5), Inches(0.4), Inches(0.3),
            size=9, color=MUTED, align=PP_ALIGN.RIGHT)


# ---------------------------------------------------------------- 1 title
s = prs.slides.add_slide(BLANK)
s.background.fill.solid()
s.background.fill.fore_color.rgb = SAND
textbox(s, "SOFT COMPUTING  ·  CASE STUDY", Inches(1.0), Inches(1.35), Inches(9),
        Inches(0.3), size=12, bold=True, color=RED)
textbox(s, "GAAPO: a replication audit\nand an adaptive operator-selection extension",
        Inches(1.0), Inches(1.80), Inches(11.2), Inches(2.3), size=35, bold=True,
        color=INK, spacing=0.95)
textbox(s, "Reproducing, correcting and stress-testing a genetic algorithm "
           "for automatic prompt optimisation",
        Inches(1.0), Inches(4.45), Inches(9.2), Inches(0.9), size=17, color=MUTED,
        spacing=1.15)
textbox(s, "Bhargav  ·  27 October 2026", Inches(1.0), Inches(5.75), Inches(6),
        Inches(0.35), size=13, color=INK)
textbox(s, "qwen2.5:7b optimiser  ·  qwen2.5:3b target  ·  ETHOS multilabel, 433 rows",
        Inches(1.0), Inches(6.2), Inches(10), Inches(0.35), size=12, color=MUTED)
notes(s, "One sentence to open: I reproduced a 2025 paper on evolving prompts with a "
         "genetic algorithm, found that its published notebook measures something "
         "different from what it claims, fixed it, and then tested the one part of the "
         "method the paper never justifies — how the search budget is split between "
         "its five operators.")

# ---------------------------------------------------------------- 2 the paper
s = frame("The paper evolves a prompt, not a model", "The algorithm")
bullets(s, [
    ("Population:", "a set of prompt strings, scored by the target model on a validation split."),
    ("Each generation:", "the best prompts become parents; five operators breed the next set."),
    ("Selection:", "highest validation accuracy survives."),
    ("The gap:", "budget split 40/20/20/10/10 across operators, with no derivation."),
], top=Inches(2.2), width=Inches(5.7), size=16)
table(s, [
    ["Operator", "Share", "What it does"],
    ["Random mutation", "40 %", "eight hand-written edits"],
    ["APO / ProTeGi", "20 %", "rewrite from the errors made"],
    ["OPRO", "20 %", "learn from best-prompt history"],
    ["Few-shot", "10 %", "append 1–3 labelled examples"],
    ["Crossover", "10 %", "splice two prompts at the midpoint"],
], Inches(6.75), Inches(2.3), Inches(5.85), Inches(2.75),
    col_widths=[1.95, 0.85, 3.9], size=12)
textbox(s, "Two claims to test: it works, and those five weights are the right ones.",
        Inches(6.9), Inches(5.25), Inches(5.5), Inches(0.8), size=14, italic=True,
        color=BLUE, spacing=1.1)
notes(s, "Framing: this is a search problem with five neighbourhood operators, so the "
         "natural questions for a soft-computing course are operator selection and "
         "fitness evaluation. Both turn out to matter.")

# ---------------------------------------------------------------- 3 what I did
s = frame("Three things: audit, ablate, extend", "What this study does")
cols = [
    ("1  Audit", "Re-implement the method from the paper and check it against the "
                 "published notebook. 24 defects corrected.",
     "6 of them change what is measured, not how fast it runs."),
    ("2  Ablate", "First leave-one-out test of the five operators: remove one at a "
                  "time, three paired repeats.",
     "Random mutation carries the method; OPRO is unresolved."),
    ("3  Extend", "Replace the fixed 40/20/20/10/10 weights with a controller that "
                  "learns the allocation from credit.",
     "Compared against the paper, uniform and random allocation."),
]
for i, (head, body, tail) in enumerate(cols):
    x = Inches(0.85 + i * 4.1)
    box = s.shapes.add_shape(1, x, Inches(2.35), Inches(3.7), Inches(2.9))
    box.fill.solid()
    box.fill.fore_color.rgb = SAND
    box.line.fill.background()
    box.shadow.inherit = False
    textbox(s, head, x + Inches(0.3), Inches(2.65), Inches(3.1), Inches(0.4),
            size=19, bold=True, color=RED)
    textbox(s, body, x + Inches(0.3), Inches(3.15), Inches(3.1), Inches(1.3),
            size=14, color=INK, spacing=1.15)
    textbox(s, tail, x + Inches(0.3), Inches(4.35), Inches(3.1), Inches(0.9),
            size=13, color=MUTED, italic=True, spacing=1.15)
textbox(s, "≈ 14 hours of local compute, no API cost, no cluster.",
        Inches(0.85), Inches(6.1), Inches(8), Inches(0.4), size=13, color=MUTED)
notes(s, "The structure of the talk follows these three blocks. The audit is what makes "
         "the numbers trustworthy; the ablation says which parts matter; the extension "
         "tests the one thing the paper leaves unjustified.")

# ---------------------------------------------------------------- 4 audit
s = frame("The published notebook does not measure what the paper describes",
          "1 · Audit")
bullets(s, [
    ("Duplicates merged, then double-counted.",
     "One row reached n = 300 on a 50-example validation set."),
    ("Baseline scored on 10 examples, candidates on 50.",
     "The published “0.00 → 0.32” compares two different test sets."),
    ("“Successive halving” ranked on a cumulative mean",
     "and returned that mean as the score."),
    ("The bandit rule was not UCB-E,", "and recycled examples as if they were new evidence."),
    ("Generated prompts were never validated.",
     "The stored “best prompt” had lost one of the eight labels."),
    ("The ablation leaked.", "APO, OPRO and crossover fell back to the mutation operator, "
     "so “without mutation” could still mutate."),
], top=Inches(2.2), width=Inches(7.4), size=15.5, space=9)
fact(s, "24", "defects corrected in the corrected notebook", Inches(9.35), Inches(2.35),
     width=Inches(3.2))
fact(s, "6", "of them change what is measured, not only speed", Inches(9.35),
     Inches(3.85), width=Inches(3.2), color=BLUE)
textbox(s, "Plus: no RNG control anywhere, one unseeded repeat per ablation arm, "
           "ablated arms never scored on test.",
        Inches(0.85), Inches(6.15), Inches(7.4), Inches(0.6), size=12, italic=True,
        color=MUTED, spacing=1.15)
notes(s, "Do not read out all 24. The point is that six of them change what is measured, "
         "so the published numbers cannot be compared with a corrected run — only the "
         "structure of the claims can. That is why the report never claims a reproduction "
         "of their tables.")

# ---------------------------------------------------------------- 5 corrected run
s = frame("Corrected, the method works — but the gap to test is large", "2 · The run")
table(s, [
    ["", "Validation (n = 50)", "Test (n = 200)"],
    ["Seed prompt", "0.100", "0.090"],
    ["Best evolved prompt", "0.460", "0.240"],
    ["Delta", "+0.360", "+0.150"],
], Inches(0.85), Inches(2.3), Inches(5.4), Inches(1.6), col_widths=[2.4, 1.7, 1.5],
    size=13)
bullets(s, [
    ("Qualitative claim survives:", "the evolved prompt nearly triples test accuracy."),
    ("Quantitative claim does not:", "validation overstates held-out by 22 points."),
    ("Why:", "the best of 102 candidates ranked on 50 examples is a biased maximum."),
], top=Inches(4.25), width=Inches(5.6), size=14, space=8)
picture(s, "score_by_generation.png", left=Inches(6.7), top=Inches(2.2),
        width=Inches(5.9))
notes(s, "This table is the honest version of the paper's headline. The method does "
         "improve the prompt — 0.09 to 0.24 on held-out data is real. What does not "
         "survive is the size of the improvement they report.")

# ---------------------------------------------------------------- 6 probe
s = frame("Where the choice is made, the signal carries no ordering", "2 · The measurement")
picture(s, "probe_validation_vs_test.png", left=Inches(0.7), top=Inches(2.2),
        width=Inches(8.9))
if S:
    textbox(s, f"ρ = {S['spearman_rho']:.2f}  (n = {S['n_prompts']}, not significant)",
            Inches(9.75), Inches(2.35), Inches(3.0), Inches(0.4), size=13, bold=True,
            color=RED)
    textbox(s, f"{S['n_within_noise_of_leader']} prompts tie with the leader on validation.",
            Inches(9.75), Inches(2.9), Inches(3.0), Inches(0.8), size=12.5, color=MUTED,
            spacing=1.15)
    textbox(s, f"Their true scores span "
               f"{S['within_noise_test_range'][0]:.2f}–{S['within_noise_test_range'][1]:.2f} — "
               f"eight points.",
            Inches(9.75), Inches(3.75), Inches(3.0), Inches(0.9), size=12.5, color=MUTED,
            spacing=1.15)
    textbox(s, f"The prompt validation picks is "
               f"{S['leader_by_validation']['n_prompts_with_higher_test'] + 1}th of "
               f"{S['n_prompts']} on test.",
            Inches(9.75), Inches(4.75), Inches(3.0), Inches(0.9), size=12.5, bold=True,
            color=INK, spacing=1.15)
textbox(s, "Post-hoc: nine prompts already generated were re-scored on the held-out set.",
        Inches(0.7), Inches(6.55), Inches(8.5), Inches(0.35), size=11, italic=True,
        color=MUTED)
notes(s, "This is the slide I would spend the most time on. It is post-hoc and labelled as "
         "such. At the coarse scale the signal works — the worst prompt on validation is "
         "the worst on test. But among the seven prompts that are statistically tied at the "
         "top, the true score ranges from 0.24 to 0.33, and the one validation picks is "
         "seventh of nine. So the search is not blind; the ranking it uses to choose is.")

# ---------------------------------------------------------------- 7 ablation
s = frame("Which operators actually carry the method?", "3 · Ablation")
table(s, [
    ["Configuration", "Best validation", "Held-out test", "Δ test"],
    ["full hybrid", "0.247 ± 0.058", "0.232 ± 0.016", "—"],
    ["without OPRO", "0.267 ± 0.031", "0.208 ± 0.079", "−0.023"],
    ["without APO", "0.227 ± 0.031", "0.142 ± 0.028", "−0.090"],
    ["without mutation", "0.187 ± 0.061", "0.127 ± 0.053", "−0.105"],
], Inches(0.85), Inches(2.3), Inches(6.6), Inches(2.1), col_widths=[2.4, 1.9, 1.8, 1.2],
    size=13)
bullets(s, [
    ("Mutation is load-bearing.", "Removing it costs 10.5 test points, significant in 2 of 3 repeats."),
    ("APO helps, evidence thinner.", "Same sign in 3/3, significant in 1/3 after correction."),
    ("OPRO is unresolved.", "The ablated arm had the best validation score and a worse test score."),
], top=Inches(4.75), width=Inches(6.4), size=13.5, space=7)
picture(s, "slide_ablation.png", left=Inches(7.65), top=Inches(2.15),
        width=Inches(5.0))
notes(s, "The paper has no leave-one-out ablation. This is the first one. The headline is "
         "that the 40 % operator is doing real work — and the caution is that the arm with "
         "the best validation score was worse on test, which is the same measurement "
         "problem again.")

# ---------------------------------------------------------------- 8 extension design
s = frame("The extension: learn the allocation instead of fixing it", "4 · Extension")
bullets(s, [
    ("Credit.", "After each generation, score every child by its improvement over its best parent."),
    ("Smooth.", "Exponential average per operator, because the search is non-stationary."),
    ("Select.", "Softmax over credit, with a 10 % exploration floor and a one-slot minimum."),
    ("Test it against controls.", "The paper's weights, uniform, and a random allocation redrawn "
     "every generation — that last one rules out “any variation helps”."),
], top=Inches(2.2), width=Inches(6.0), size=15, space=10)
table(s, [
    ["Arm", "Question it answers"],
    ["fixed", "does the paper's default hold up?"],
    ["uniform", "is the prior doing any work?"],
    ["random", "is a gain just extra noise?"],
    ["adaptive", "does learning the allocation help?"],
], Inches(7.2), Inches(2.35), Inches(5.3), Inches(2.3),
    col_widths=[1.4, 3.9], size=12.5)
textbox(s, "Twelve runs · population 10 × 6 generations · three paired seeds · identical call budget",
        Inches(0.85), Inches(5.55), Inches(11), Inches(0.4), size=13, bold=True, color=BLUE)
textbox(s, "Hypotheses fixed before looking at the results.",
        Inches(0.85), Inches(6.0), Inches(9), Inches(0.4), size=12.5, italic=True,
        color=MUTED)
notes(s, "Two points to make. First, the random-allocation control is the one that makes "
         "the result interpretable. Second, hypotheses were pre-registered, which is why "
         "the negative result is still a result.")

# ---------------------------------------------------------------- 9 extension result
s = frame("The controller does not beat the fixed weights", "5 · Result")
table(s, [
    ["Arm", "Best validation", "Held-out test", "Weight entropy"],
    ["fixed (paper)", "0.347 ± 0.042", "0.292 ± 0.028", "0.914"],
    ["adaptive", "0.347 ± 0.042", "0.293 ± 0.049", "0.963"],
    ["uniform", "0.333 ± 0.042", "0.262 ± 0.043", "1.000"],
    ["random", "0.327 ± 0.031", "0.228 ± 0.051", "0.776"],
], Inches(0.85), Inches(2.25), Inches(6.6), Inches(2.0),
    col_widths=[2.2, 2.0, 1.9, 1.5], size=12)
bullets(s, [
    ("Adaptive − fixed: +0.002.", "The sign flips between repeats; no p-value survives correction."),
    ("But the controls speak.", "Both prior-based arms beat random allocation by 6–7 points, "
     "consistently in sign. The 40/20/20/10/10 vector is not arbitrary."),
    ("And the response surface is flat.", "Two very different allocations perform identically."),
], top=Inches(4.55), width=Inches(7.1), size=13.5, space=7)
picture(s, "slide_adaptive_weights.png", left=Inches(7.75), top=Inches(2.1),
        width=Inches(5.05))
notes(s, "Lead with the null: no detectable difference. Then the useful part — the "
         "controls show the paper's weights encode something real, because random "
         "allocation is measurably worse. Flat response surface explains why two very "
         "different allocations tie.")

# ---------------------------------------------------------------- 10 why it failed
s = frame("It failed for an identifiable reason, not a mysterious one", "5 · Diagnosis")
bullets(s, [
    ("Credit arrives in ±0.2.", "One or two children per operator per generation, on 50 examples."),
    ("The controller could express a 1.5 : 1 odds ratio at most.", "Temperature 0.5 against that credit "
     "spread; a 20 % operator could reach 27 % at best."),
    ("So it drifted toward uniform", "while the credits said the opposite: few-shot had the worst "
     "credit every generation and still gained weight."),
    ("The fix is arithmetic, not conceptual.", "Match the temperature to the credit scale, "
     "use rank-based credit, and give it a longer horizon."),
], top=Inches(2.2), width=Inches(8.6), size=15.5, space=11)
fact(s, "±0.2", "spread of observed credit", Inches(9.7), Inches(2.5), width=Inches(2.6),
     color=BLUE)
fact(s, "0.5", "temperature it was divided by", Inches(9.7), Inches(3.9),
     width=Inches(2.6), color=RED)
textbox(s, "The credit was noisy. The controller was also built so it could not use what signal there was.",
        Inches(9.55), Inches(5.05), Inches(3.15), Inches(1.5), size=13, italic=True,
        color=INK, spacing=1.15)
notes(s, "This is the slide that turns a null result into a contribution. The failure is "
         "mechanical and demonstrated by reconstructing the controller's internal state "
         "from the logs — not asserted. Section 4.1 adds the second half: even with the "
         "arithmetic fixed, the credit it was learning from comes from a validation "
         "ranking that does not survive a change of examples.")

# ---------------------------------------------------------------- 11 what it means
s = frame("What the study establishes", "Discussion")
rows = [
    ("The method works.", "A 0.09 → 0.24 held-out gain, with the operators demonstrably "
                          "doing different amounts of work."),
    ("The paper's precision does not.", "A 22-point optimism, no derivation for the "
                                        "weights, a headline that mixes evaluation sets."),
    ("The weights are a reasonable prior.", "Better than random, but not an optimum — "
                                            "the response surface is flat."),
    ("Measurement, not operators, is the bottleneck.", "At this scale the selection "
                                                       "signal is too noisy to learn from."),
]
y = Inches(2.35)
for head, body in rows:
    bar = s.shapes.add_shape(1, Inches(0.85), y, Inches(0.06), Inches(0.78))
    bar.fill.solid()
    bar.fill.fore_color.rgb = RED
    bar.line.fill.background()
    bar.shadow.inherit = False
    textbox(s, head, Inches(1.15), y, Inches(4.1), Inches(0.4), size=17, bold=True,
            color=INK)
    textbox(s, body, Inches(5.3), y, Inches(7.1), Inches(0.8), size=14.5, color=MUTED,
            spacing=1.1)
    y += Inches(1.1)
notes(s, "Four sentences, in order of confidence. The last one is the one I would carry "
         "into a follow-up: spend the budget on measuring the candidates, not on smarter "
         "operators.")

# ---------------------------------------------------------------- 12 limitations
s = frame("Limitations, and what I would run next", "Honesty")
bullets(s, [
    ("Small models.", "qwen2.5:7b writing prompts for qwen2.5:3b — far below the paper's "
     "70B-class optimiser, so rankings may not transfer."),
    ("Few observations.", "Three seeds per arm; the same configuration varied by six points "
     "between sessions."),
    ("One dataset, one task.", "Multi-label hate-speech classification only; prompt "
     "optimisation helps most where the base prompt is weak."),
    ("Not run.", "The paper's selection-method comparison (bandit vs halving); it is "
     "implemented in the notebook and disclosed as unfinished."),
], top=Inches(2.2), width=Inches(7.6), size=15, space=10)
box = s.shapes.add_shape(1, Inches(8.75), Inches(2.3), Inches(3.75), Inches(2.75))
box.fill.solid()
box.fill.fore_color.rgb = SAND
box.line.fill.background()
box.shadow.inherit = False
textbox(s, "Next, in order", Inches(9.05), Inches(2.55), Inches(3.2), Inches(0.35),
        size=14, bold=True, color=RED)
textbox(s, "1  Bigger validation set\n\n2  Selection that accounts for noise\n\n"
           "3  Re-run the controller with matched temperature",
        Inches(9.05), Inches(3.05), Inches(3.2), Inches(2.5), size=13.5, color=INK,
        spacing=1.25)
notes(s, "Be explicit that the negative result is a statement about this scale. The one "
         "thing I would do with more compute is the second item: selection under noise, "
         "not more operators.")

# ---------------------------------------------------------------- 13 close
s = prs.slides.add_slide(BLANK)
s.background.fill.solid()
s.background.fill.fore_color.rgb = SAND
textbox(s, "Thank you", Inches(1.0), Inches(2.6), Inches(8), Inches(0.8), size=34,
        bold=True, color=INK)
textbox(s, "Questions, and the parts I got wrong.", Inches(1.0), Inches(3.45),
        Inches(9), Inches(0.6), size=18, color=MUTED, italic=True)
textbox(s, "Code, logs and per-example predictions: GAAPO_improved.ipynb, "
           "run_sweep.py, run_adaptive.py, run_probe.py",
        Inches(1.0), Inches(5.6), Inches(11), Inches(0.4), size=12, color=MUTED)
notes(s, "Invite the obvious challenge: 'why should I believe a null result from three "
         "seeds?' Answer: I do not claim equivalence, only that any effect is smaller than "
         "the design can see — and the report gives the interval that quantifies exactly "
         "how small.")

for n, slide in enumerate(prs.slides, 1):
    if n not in (1, len(prs.slides)):
        footer(slide, n)

out = ART / "GAAPO_case_study_slides.pptx"
prs.save(out)
print("wrote", out, "with", len(prs.slides), "slides")
