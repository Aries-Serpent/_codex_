# BLEU Brevity Penalty Fix – Migration Note

**Audience:** Model owners and evaluation maintainers

## Summary
The corpus BLEU brevity penalty now aligns each hypothesis with its own reference
set. Corpora that reuse identical reference lists may see BLEU changes (usually
slightly higher BP). Any dashboards, acceptance thresholds, or alerts that relied
on the old buggy values should be reviewed.

## Recommended Actions
1. Re-run BLEU evaluations for currently deployed checkpoints and compare to the
   historical baseline.
2. Document any observed score deltas in the model evaluation record.
3. Update guardrails (dashboards, CI assertions, alert thresholds) if the BLEU
   range has shifted.
4. Communicate downstream if decisions were previously made with the incorrect
   BP.

## Email / Message Template
```
Subject: BLEU brevity penalty fix may shift evaluation results

Hi <team>,

We merged the P1 fix that pairs each BLEU hypothesis with its reference set when
computing the brevity penalty. Any corpus that reuses reference lists may see
numerically different BLEU scores. Please re-run your evaluation pipeline,
compare against stored baselines, and adjust CI/dashboard thresholds if they no
longer reflect the corrected values.

Let us know if you need help interpreting the updated metrics.

Thanks,
<Model owner / Evaluation contact>
```
