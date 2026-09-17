# Example gallery (sanitized)

Packaging and brief exemplars safe for demos. **Not** live customer data. **Not** execution authority.

## Briefs

| Path | Story |
|------|--------|
| [`../product-audit.brief.yaml`](../product-audit.brief.yaml) | Product + commercial + wayfinder handoff |
| [`../zero-option.brief.yaml`](../zero-option.brief.yaml) | Empty skills → honest NOT_COMPUTABLE |
| [`../zero-option-with-skills.brief.yaml`](../zero-option-with-skills.brief.yaml) | Declared skills → micro-loop stub |
| [`../fragmentation.brief.yaml`](../fragmentation.brief.yaml) | Multi-portal friction scan |
| [`../commercial.brief.yaml`](../commercial.brief.yaml) | Commercial scaffold + buyer request |
| [`../audit.brief.yaml`](../audit.brief.yaml) | Offline audit delivery scaffold |
| [`../agentic.brief.yaml`](../agentic.brief.yaml) | Agentic graph; x402 reject scaffold |
| [`../memetic.brief.yaml`](../memetic.brief.yaml) | Memetic pressure; Gate D cap |
| [`../evidence.brief.yaml`](../evidence.brief.yaml) | Evidence intelligence scaffold |
| [`../opportunity.brief.yaml`](../opportunity.brief.yaml) | Opportunity + completion proof |

## Packets

| Path | Story |
|------|--------|
| [`../packets/sample-opportunity.packet.json`](../packets/sample-opportunity.packet.json) | Opportunity with completion_proof |
| [`../packets/sample-commercial.packet.json`](../packets/sample-commercial.packet.json) | Commercial scaffold; no invented CAC/LTV |
| [`../packets/sample-receipt.packet.json`](../packets/sample-receipt.packet.json) | Advisory run receipt |
| [`../packets/sample-data-request.json`](../packets/sample-data-request.json) | Private DataRequest |
| [`../packets/sample-receipt-with-requests.json`](../packets/sample-receipt-with-requests.json) | Receipt + open blocking requests |

## Prose goldens

| Path | Story |
|------|--------|
| [`../../evals/transcripts/`](../../evals/transcripts/) | Full OPEN→SEAL exemplars |

## One-liner to run

```bash
python scripts/neon_genie.py do recipe --name product-audit --out out/neon-genie/gallery-audit
python scripts/neon_genie.py do validate --packet examples/packets/sample-opportunity.packet.json --type opportunity
```

Demo path: [`../../docs/DEMO.md`](../../docs/DEMO.md).  
Thesis: [`../../docs/PREMIERE.md`](../../docs/PREMIERE.md).
