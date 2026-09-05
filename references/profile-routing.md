# Profile routing (load when choosing specialized modes)

Core and privacy always apply. Auto-load evidence intelligence when external facts matter.

   ```yaml
   profile_router:
     core: always
     privacy:
       triggers: [always]
       default_when: always_with_core
     product_architecture:
       triggers: [product audit, app design, game design, system design, feature coherence]
     opportunity_mining:
       triggers: [new venture, unmet need, market opportunity, blocked transition, roadmap, business idea, go into business, side project, app idea, product idea, what should I build, where do I start, next steps]
     fragmentation:
       triggers: [many portals, repeated handoffs, incompatible systems, coordination problem]
     zero_option:
       triggers: [zero capital, first cash, immediate executable opportunity, constrained launch, limited money, limited resources, limited capital, between jobs, bootstrapped, no budget, first revenue]
     agentic_services:
       triggers: [agent workflow, delegated outcome, automation, x402, machine services]
     commercial:
       triggers: [pricing, buyer, revenue, costs, market pressure, business model]
     evidence_intelligence:
       triggers:
         - grants
         - boards
         - philanthropy
         - competitive research
         - current external facts
         - auto: any material external gap that research can close
       default_when: improves_result
     memetic:
       triggers: [name, hook, pitch language, public framing, shareability]
     audit_delivery:
       triggers: [client audit, cost of inaction, diagnostic package, implementation offer]
     wayfinder_handoff:
       triggers: [build plan, engineering readiness, execution packet]
     capital_sprint:
       triggers:
         - capital sprint
         - annual fund
         - donation drive
         - membership drive
         - fundraising deadline
         - impact object
         - donor sprint
         - nonprofit capital raise
   ```
