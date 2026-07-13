---
name: authoring-dbt-models
description: Author and review dbt models following team conventions for naming, layering, materialization, and testing. Use when creating a new dbt model, refactoring SQL into staging/intermediate/mart layers, or reviewing a model before opening a pull request.
---

# Authoring dbt Models

A worked example of a domain skill built with `skill-builder`. It captures a
data-engineering team's dbt conventions so every model looks the same regardless
of who wrote it. Replace the placeholder conventions with your team's real ones.

## When to use this skill
- Creating a new dbt model
- Refactoring raw SQL into the staging → intermediate → mart layering
- Reviewing a model before opening a pull request

## Core principles
1. **Layer discipline**: `stg_` reads only from sources; `int_` composes staging
   models; `mart_` (fct_/dim_) is what analysts query. Never skip layers.
2. **One grain per model**: state the grain in a top comment; every model has a
   single, documented primary key.
3. **Test the contract**: every model declares `unique` + `not_null` on its key,
   plus `relationships` tests on foreign keys.

## Process

```
Model progress:
- [ ] 1. Pick the layer and name (stg_/int_/fct_/dim_)
- [ ] 2. Declare the grain and primary key
- [ ] 3. Write the SQL using ref()/source(), no raw table names
- [ ] 4. Add the model to the layer's .yml with description + tests
- [ ] 5. Run: dbt build --select <model> (compiles, runs, tests)
```

**Step 1 — Layer and name.** Choose the layer, then name it:
`stg_<source>__<entity>`, `int_<entity>__<verb>`, `fct_<process>`, `dim_<entity>`.

**Step 2 — Grain and key.** Add a top comment: `-- grain: one row per order`.
Define the primary key (a surrogate key via `dbt_utils.generate_surrogate_key`
when there's no natural single-column key).

**Step 3 — SQL.** Reference upstream with `ref()` / `source()` only — never a raw
`schema.table`. Use CTEs named for what they hold; final CTE is `select * from final`.

**Step 4 — Contract.** Add the model to the layer `.yml` with a `description` and,
at minimum, `unique` + `not_null` on the key. Add `relationships` tests on FKs.

**Step 5 — Validate.** Run `dbt build --select <model>`. Fix compile/test
failures and re-run until green before opening a PR.

## Example

**Input:** "Create a staging model for the Stripe `charges` source."

**Output:** `models/staging/stripe/stg_stripe__charges.sql`
```sql
-- grain: one row per charge
with source as (
    select * from {{ source('stripe', 'charges') }}
),

renamed as (
    select
        id                       as charge_id,
        customer                 as customer_id,
        amount / 100.0           as amount_usd,
        status,
        created::timestamp       as created_at
    from source
),

final as (
    select * from renamed
)

select * from final
```
And in `models/staging/stripe/_stripe__models.yml`:
```yaml
models:
  - name: stg_stripe__charges
    description: One row per Stripe charge, amounts converted to USD.
    columns:
      - name: charge_id
        description: Primary key.
        tests: [unique, not_null]
```

## Anti-patterns
- **Raw table references** (`from analytics.stripe.charges`) — breaks lineage.
  Instead: `{{ source(...) }}` or `{{ ref(...) }}`.
- **Marts reading from sources directly** — skips the staging contract. Instead:
  always route through `stg_`.
- **Untested keys** — a model with no `unique`/`not_null` on its grain. Instead:
  test every primary key.
