# Plano Técnico - MMH-1435 AC3: Summary price computation

## Contexto
- **Ticket**: MMH-1435 - CLONE - Review the Asset tab during Simulation
- **AC3**: Summary price computation applies the defined formulas
- **AC1 e AC2**: Já implementadas

## Fórmulas AC3

1. **Total exc. VAT** = Catalogue Price + Options + Transport cost + Car tax (if any) + Exempt quote (if any) – Discounts (OEM + Other)
2. **Accessories** = Accessories Price inc VAT + Transform accessories inc VAT
3. **Registration Tax** = Price of registration tax – Discount registration tax (If applicable)
4. **Total incl. VAT** = Total exc. VAT + VAT amount + OEM Services + Accessories + Registration Tax + Free fee inc VAT
5. **Total Invoice Price** = Total incl. VAT – Ecobonus – Trade in

## Nota sobre Note2 do ticket
> "Accessories should be inserted excl vat"

O campo `Accessories` na fórmula é calculado como inc VAT (AC3 Formula 2), mas a Note2 do ticket diz que accessories devem ser inseridos excl VAT. Isto significa que no display do Summary, o valor de Accessories deve ser mostrado **excl VAT**, e não inc VAT. No entanto, para o cálculo de Total incl. VAT, o valor inc VAT é necessário.

**Resolução**: O campo `accessoriesIncVat` será armazenado mas exibido como excl VAT (accessoriesIncVat / (1 + VAT%)). O Total incl. VAT usará o valor inc VAT na fórmula.

## Ordem do Summary (confirmada pelo utilizador)

```
Catalogue Price
Options
Transport cost         ← placeholder (MFSCC-338)
Car tax
Exempt quote           ← placeholder (MFSCC-338), zero for now
Discount               ← OEM + Other discount combinados (single line)
──────────────────
Total exc VAT          ← subtotal
VAT pourcentage
VAT amount
OEM Services
Accessories            ← excl VAT no display (inc VAT na fórmula)
Registration tax       ← placeholder (MFSCC-338)
Free fee inc VAT       ← placeholder (MFSCC-338)
──────────────────
Total included VAT     ← subtotal
Trade in
Eco Bonus
──────────────────
Total invoice price    ← total final
```

## Fontes dos campos (Miles API)

| Campo | Fonte Miles | Status |
|---|---|---|
| Catalogue Price | `car.catalogPrice.value` | ✅ Já temos (`basePrice`) |
| Options | `car.vehicleConfigurations[]` optionType="Option" → sum `catalogPrice.value` | ✅ Já temos |
| Transport cost | `deliveryCostComponents` (Delivery Fees) | ⚠️ Placeholder (MFSCC-338) |
| Car tax | `car.tax.value` | ✅ Já temos |
| Exempt quote | Por definir no MFSCC-338 | ⚠️ Placeholder (MFSCC-338) |
| OEM Discount | `vehicleDiscountConfigurations[]` type 100001 | ✅ Parcialmente (discountAmount) |
| Other Discount | `vehicleDiscountConfigurations[]` type Dealer | ✅ Parcialmente |
| VAT pourcentage | `car.catalogVatCode.enumId` → MongoDB lookup | ✅ Já temos (AC2) |
| VAT amount | `car.netPriceInclVat.value - car.netPrice.value` | ✅ Já temos |
| OEM Services | `productConfiguration.services[reference='Assistance']` | ⚠️ Placeholder (precisa extrair) |
| Accessories (inc VAT) | `vehicleConfigurations[]` optionType="Accessory" → sum `consumerPrice.value` | ⚠️ Placeholder (parcial - só exc VAT) |
| Transform accessories (inc VAT) | Por definir | ⚠️ Placeholder (sem dados Miles) |
| Registration tax | `deliveryCostComponents` com `costTypeId` específico | ⚠️ Placeholder (MFSCC-338) |
| Registration tax discount | `deliveryCostComponents` | ⚠️ Placeholder (MFSCC-338) |
| Free fee inc VAT | `deliveryCostComponents` com `costTypeId` específico | ⚠️ Placeholder (MFSCC-338) |
| Trade in | `productConfiguration.services[reference=TRADE_IN]` | ✅ Já temos |
| Eco Bonus | `productConfiguration.qualifierSettings` | ✅ Já temos |

## Decisão: Implementar com placeholders

Os campos que dependem de `deliveryCostComponents` (Transport cost, Registration tax, Registration tax discount, Free fee inc VAT) e `Exempt quote` serão exibidos como `-` (zero) até o ticket MFSCC-338 ser resolvido. `Transform accessories` também será placeholder. As fórmulas serão implementadas para os calcular quando os dados ficarem disponíveis.

## Campos já existentes em PricingDetails (dead code a ativar)

Os seguintes campos **já existem** no `PricingDetails` mas nunca são populados, normalizados ou exibidos:
- `transportCost` ← ativar
- `accessoriesIncVat` ← ativar
- `oemServices` ← ativar
- `registrationTax` ← ativar
- `registrationTaxDiscount` ← ativar
- `freeFeeIncVat` ← ativar

Campos **novos** a adicionar:
- `exemptQuote` ← placeholder para MFSCC-338
- `transformAccessoriesIncVat` ← placeholder para Transform accessories

Nota: OEM Discount e Other Discount são combinados numa única linha "Discount" no UI. Internamente, `oemDiscountAmount` e `otherDiscountAmount` existem no store para a fórmula, mas o display é combinado.

## Plano de Implementação

### Passo 1: Adicionar campos novos ao `PricingDetails` em `types/types.ts`

```typescript
export interface PricingDetails {
  // ... existentes (incluindo 6 campos dead code) ...
  exemptQuote?: number | null;            // Placeholder MFSCC-338
  transformAccessoriesIncVat?: number | null; // Placeholder
}
```

### Passo 2: Atualizar `mappingResponse.ts` - `mappingCreateDealResponse`

Extrair novos campos quando disponíveis no `carConfig`:
- `accessoriesIncVat` ← somar `consumerPrice.value` dos accessories em `optionsResApi`
- `transformAccessoriesIncVat` ← placeholder (0)
- `oemServices` ← extrair de services com reference 'Assistance'
- `exemptQuote` ← placeholder (0, MFSCC-338)
- `oemDiscountAmount` ← `vehicleDiscountConfigurations[]` type 100001 → `discountAmount` (usado na fórmula)
- `otherDiscountAmount` ← `vehicleDiscountConfigurations[]` type Dealer → `discountAmount` (usado na fórmula)

### Passo 3: Atualizar `mappingResponse.ts` - `buildCalculateResponse`

Extrair novos campos de `salesQuote`:
- `accessoriesIncVat` ← somar `consumerPrice.value` dos vehicleConfigurations com optionType="Accessory"
- `transformAccessoriesIncVat` ← placeholder (0)
- `oemServices` ← extrair de `quoteProduct.productConfiguration.services` com reference='Assistance'
- `transportCost` ← `totalDealerDeliveryCosts?.value` (quando disponível)
- `exemptQuote` ← placeholder (0, MFSCC-338)
- `registrationTax` ← filtrar `deliveryCostComponents` por costTypeId (quando disponível)
- `registrationTaxDiscount` ← placeholder (0)
- `freeFeeIncVat` ← filtrar `deliveryCostComponents` por costTypeId (quando disponível)
- `oemDiscountAmount` ← extrair de descontos OEM
- `otherDiscountAmount` ← extrair de descontos Dealer

### Passo 4: Atualizar normalização no store `assets.ts`
- `normalizePricingDetails` → adicionar novos campos (exemptQuote, transformAccessoriesIncVat, oemDiscountAmount, otherDiscountAmount) + ativar dead code fields
- `_applyCalcResponse` → adicionar novos campos
- `calculateDeal` → adicionar novos campos

### Passo 5: Atualizar `assetService.ts` - `mapToAssetPricingDetails`
Adicionar mapeamento dos novos campos + ativar dead code fields.

### Passo 6: Atualizar `useInit.ts`
Adicionar novos campos ao pricingDetails construction + ativar dead code fields.

### Passo 7: Reescrever `AssetSummary.vue`

**Nova estrutura do template (ordem confirmada):**
```
Catalogue Price        → basePrice
Options                → totals.options
Transport cost         → pricingDetails.transportCost (placeholder: '-')
Car tax                → pricingDetails.tax
Exempt quote           → pricingDetails.exemptQuote (placeholder: '-')
Discount               → oemDiscountAmount + otherDiscountAmount (combined display)
─────────────────────
Total exc VAT          → FORMULA 1 (subtotal, bold)
VAT pourcentage        → vatPercentageDisplay
VAT amount             → vatAmountSafe
OEM Services           → pricingDetails.oemServices (placeholder: '-')
Accessories            → accessoriesExclVat (display excl VAT; uses accessoriesIncVat / (1+VAT%))
Registration tax       → pricingDetails.registrationTax - registrationTaxDiscount (placeholder: '-')
Free fee inc VAT       → pricingDetails.freeFeeIncVat (placeholder: '-')
─────────────────────
Total included VAT     → FORMULA 4 (subtotal, bold)
Trade in               → discount.tradeInValue
Eco Bonus              → discount.ecoBonus
─────────────────────
Total invoice price    → FORMULA 5 (total final, bold)
```

**Fórmulas computed:**
```typescript
const totalDiscounts = computed(() =>
  (pricingDetails.oemDiscountAmount ?? 0) + (pricingDetails.otherDiscountAmount ?? 0)
)

const accessoriesTotalIncVat = computed(() =>
  (pricingDetails.accessoriesIncVat ?? 0) + (pricingDetails.transformAccessoriesIncVat ?? 0)
)

const accessoriesExclVat = computed(() =>
  accessoriesTotalIncVat / (1 + (pricingDetails.vatPercentage ?? 0) / 100)
)

const registrationTaxNet = computed(() =>
  (pricingDetails.registrationTax ?? 0) - (pricingDetails.registrationTaxDiscount ?? 0)
)

// Formula 1: Total exc VAT
const totalExcVat = computed(() =>
  cataloguePrice + optionsTotal + transportCost + carTax + exemptQuote - totalDiscounts
)

// Formula 4: Total incl VAT
const totalIncVat = computed(() =>
  totalExcVat + vatAmount + oemServices + accessoriesTotalIncVat + registrationTaxNet + freeFeeIncVat
)

// Formula 5: Total invoice price
const totalInvoicePrice = computed(() =>
  totalIncVat - tradeInValue - ecoBonus
)
```

### Passo 8: Adicionar i18n keys

**Keys que JÁ EXISTEM** (não duplicar): `oemServices`, `accessories`, `ecoBonus`, `totalInvoicePrice`

**Keys novas a adicionar:**
```json
// en-US
"transportCost": "Transport cost",
"carTax": "Car tax",
"exemptQuote": "Exempt quote",
"registrationTax": "Registration tax",
"freeFeeIncVat": "Free fee inc. VAT",
"totalExcVat": "Total exc. VAT",
"totalIncVat": "Total incl. VAT",
"tradeIn": "Trade in",
"discount": "Discount"

// fr-FR
"transportCost": "Frais de transport",
"carTax": "Taxe automobile",
"exemptQuote": "Devis exempté",
"registrationTax": "Taxe d'immatriculation",
"freeFeeIncVat": "Frais gratuits TTC",
"totalExcVat": "Total HT",
"totalIncVat": "Total TTC",
"tradeIn": "Reprise",
"discount": "Remise"
```

## Ficheiros a alterar

1. `types/types.ts` — Adicionar novos campos a PricingDetails (exemptQuote, transformAccessoriesIncVat)
2. `server/utils/mappingResponse.ts` — Extrair novos campos do Miles + ativar dead code fields
3. `features/asset/stores/assets.ts` — Normalização dos novos campos + ativar dead code fields
4. `features/asset/stores/services/assetService.ts` — Mapeamento + ativar dead code fields
5. `composables/useInit.ts` — Mapeamento ao carregar deal + ativar dead code fields
6. `features/asset/components/demandAssetDetails/AssetSummary.vue` — Reescrever UI e fórmulas
7. `locales/en-US.json` — Novas traduções (apenas keys que não existem)
8. `locales/fr-FR.json` — Novas traduções (apenas keys que não existem)
