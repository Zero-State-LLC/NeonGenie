# IDEA 3: Autogive.app tenant workbench SKU (Zero State LLC)
----- SOURCE: Notion "2026-08-17 Autogive tenant COGS + price floor" (child of Growth packet — GAP / SIGNAL / Acquire), last edited 2026-08-18 -----
Shipped: Autogive.app / AGI tenant unit-econ (not AutoGive.com). AGI never processes donations. Stripe = tenant SaaS invoice only.
Engine: insurance (proof/SLA) sold; labor (Grok inference) is COGS; capital is the Heavy seat. Labor feeds insurance. No gift-flow arbitrage.
For: GAP (package tenant SKU to the floor) and Boof (Danny card). Not a live donor CTA.
## Assumptions
- SuperGrok Heavy seat ~$300/mo INFERRED. Does not include API.
- grok-4.6 OBSERVED: $2 in / $6 out per 1M below 200k prompt; $4 / $12 for the whole request at >=200k. https://docs.x.ai/developers/pricing
- CF Workers Paid $5/mo OBSERVED list. Supabase Pro $25/mo OBSERVED list. Shared until quotas break.
- Token bands SPECULATIVE (no measured tenant usage): low 2M in + 0.4M out = $6.40; med 20M in + 4M out = $64; high 80M in + 16M out = $256; high+cliff x2 = $512.
## Which line blows first
- Heavy per tenant: seats, immediately, linear $300xN. Heavy per operator (1 seat): tokens, then the 200k cliff. CF+Supabase last.
## Price floor (tenant MRR must clear this or the price is a subsidy)
Shared Heavy (1 seat, fixed $330): 1 tenant: $336/$394/$586 (low/med/high tokens); 10 tenants: $39/$97/$289; 50 tenants: $13/$71/$263
Heavy per tenant: 1: $636/$694/$886; 10: $309/$367/$559; 50: $307/$365/$557
A $49–$99 tenant SKU under per-tenant Heavy is a subsidy. Under shared Heavy it only clears at 10+ tenants and low/med tokens.
CM = P − allocated Heavy − E[tokens] − allocated infra − Stripe on P. LTV NOT_COMPUTABLE. No donation rake.
## GAP SKU package (2026-08-18) — ESTIMATE, not a published list. Login parked; not sellable live.
No observed tenants. Fail closed: price as N=1.
SKU 0 Public fixture $0. SKU 1 Shared-Heavy workbench list ESTIMATE $500/$650. SKU 2 Dedicated-Heavy list ESTIMATE $800/$1,000. SKU 3 Connector + impact loop: shared >= $650; dedicated >= $1,000. every.org live pointing PENDING.
Human-yes: publish/send of a price list is later human-yes.
----- SOURCE: Notion Growth packet page (2026-08-17 prior-packet line) -----
Autogive tenant COGS + price floor: Engine: insurance sold, labor COGS, capital = Heavy seat. GAP filed SKU package 2026-08-18 (N=1 floors; Shared $500/$650 or Dedicated $800/$1000). Next — SIGNAL: invoice copy only after human-yes to publish.
