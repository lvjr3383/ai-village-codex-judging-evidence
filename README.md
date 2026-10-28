# Codex judging replay evidence

This packet contains three selected AI Village source events, an executable replay verifier, the extracted original generator, and computed results. The verifier uses Python 3 standard-library modules and Git. It executes the archived generator in temporary directories; inspect the source first. No model API calls are used.

## Reproduce

```sh
git clone https://github.com/ai-village-agents/research-2026-05.git research-2026-05
python3 verify.py --repo research-2026-05
```

The script uses five immutable commits, not moving branch or tag names. The four release/snapshot mappings are 2442b493 (audited main snapshot), 37df6a31 (v1.1.5), 9cbb5d8a (v1.2.0), and 4efb64f5 (v1.3.0). It also checks surviving commit b2199247 and ancestry.

It extracts the generator unchanged from event t:55933f3a-5c78-4182-b233-1c9e9cdc711c and runs it on each commit's two Gemini session packets. It matches entries by blind_id and displayed_label and compares five score fields. Inspect results.json for mismatches; successful script execution alone does not mean scores match. File metadata and byte identity are not tested. Source stdout calling scores native is a claim made by the generator, not our assessment.

The archived execution records commit 090484a; surviving commit b2199247 has matching scores. No explanation for their hash difference is asserted.

## Public report

https://github.com/ai-village-agents/research-2026-05/blob/2442b493c0b6eb2fcd3045c77bf5b463b29b31c5/experiments/replication-wave/results/blogpost.md

Section 3.10 describes the replacement scores as native in-context judgments and reports Gemini label effects. A copy retrieved from that immutable URL is included. This establishes public repository reporting, not peer-reviewed publication.

Release: v1.0.0. The repository contains evidence and reproduction instructions only; article drafts and figures are excluded.

Source records originate from AI Village; the included public report was written by the AI Village research team. Inclusion preserves their attribution and does not assert a new license over third-party material. The scan performed before release was targeted and is not a comprehensive security audit.
