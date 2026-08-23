"""Design engine: deterministic intake review, hydrozoning, compatibility
checks, product selection and assumption/risk tracking.

These modules encode the design rules from docs/03 and docs/04. They are
deliberately separate from language-model judgment (docs/08 section 24):
every decision here is rule-based, cites its basis, and refuses to
proceed on missing critical data instead of guessing.
"""
