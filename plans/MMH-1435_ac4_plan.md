# Plano Técnico - MMH-1435 AC4: Editing Total Invoice Price

## Contexto
- **Ticket**: MMH-1435 - CLONE - Review the Asset tab during Simulation
- **AC4**: Editing Total Invoice Price recalculates discounts using delta excl. VAT
- **AC1, AC2, AC3**: Já implementadas

## AC4 - Requisitos

> Given the Summary is displayed
> And a calculated Total Invoice Price is shown
> When the dealer edits the Total Invoice Price manually
> Then the system must:
> 1. Compute the delta between the original and the new Total Invoice Price (delta TTC)
> 2. Convert this delta to an excl. VAT value using: delta excl. VAT = delta incl. VAT / (1 + VAT%)
> 3. Add the delta excl. VAT to the "Other Discounts" field and update the discounts value on the summary section
> 4. Recalculate the new Total exc. VAT
> 5. Recalculate VAT amount and Total incl. VAT
> 6. Update all Summary fields accordingly
> 7. Display the new Total Invoice Price entered by the user

**Note1**: The user should only reduce the amount (cannot increase beyond original).

**Example (from ticket)**:
- Original Total Invoice Price = 14,209 €
- User edits it to = 13,209 €
- VAT = 22%
- deltaTTC = -1,000 €
- deltaExclVAT = -1,000 / 1.22 = -819.67 €
- Original Other Discount = 100 €
- New Other Discounts = 100 + 819.67 = 919.67 €
- Recalculated Total Invoice = 13,209 € ✓

## Arquitetura da Solução

### Fluxo de edição

```
User clicks Total Invoice Price in Summary
  → Total Invoice Price becomes editable (text input)
  → User enters new value
  → onChange handler:
      a. Validate: newValue <= originalTotalInvoicePrice (Note1)
      b. deltaTTC = newValue - originalTotalInvoicePrice
      c. deltaExclVAT = deltaTTC / (1 + VAT%)
      d. newOtherDiscount = currentOtherDiscount + deltaExclVAT
      e. store.setOtherDiscount(newOtherDiscount) [symbol stays "€"]
      f. triggerCalc() → calculateDeal() → backend sync
      h. Display new value
```

### Guardar "original calculated Total Invoice Price"

O valor original (antes de qualquer edição do utilizador) é necessário para calcular o delta. Este valor é guardado numa ref no componente Summary, inicializada com o valor calculado de `totalInvoicePrice` na primeira renderização.

### Validação

- Se newValue > originalTotalInvoicePrice → mostrar erro / não aplicar (Note1)
- Empty/invalid input → não aplicar

## Plano de Implementação

### Passo 1: Adicionar `originalTotalInvoicePrice` a `AssetDealState` (types.ts)

```typescript
// Em AssetDealState
export interface AssetDealState {
  // ... existing fields ...
  originalTotalInvoicePrice?: number | null;
}
```

### Passo 2: Adicionar método `applyDeltaToOtherDiscount` em `assets.ts`

Novo método no store:

```typescript
applyDeltaToOtherDiscount(newTotalInvoicePrice: number) {
  const original = this.originalTotalInvoicePrice ?? 0
  if (newTotalInvoicePrice > original) {
    throw new Error('Cannot increase Total Invoice Price beyond original value')
  }
  
  const vatPercent = this.pricingDetails?.vatPercentage ?? 20
  const deltaTTC = newTotalInvoicePrice - original
  const deltaExclVAT = deltaTTC / (1 + vatPercent / 100)
  
  const currentOther = Number(this.discount.otherDiscount || 0)
  const currentSymbol = this.discount.otherSymbol || '€'
  
  let currentOtherEuro = currentOther
  if (currentSymbol === '%') {
    const base = Number(this.pricingDetails?.basePrice || 1)
    currentOtherEuro = (currentOther / 100) * base
  }
  
  const newOtherEuro = currentOtherEuro + deltaExclVAT
  
  this.setOtherSymbol('€')
  this.setOtherDiscount(Number(newOtherEuro.toFixed(2)))
  
  this.calculateDeal()
}
```

Também, inicializar `originalTotalInvoicePrice` quando `pricingDetails` é guardado:

```typescript
// Em setPricingDetails action
if (this.originalTotalInvoicePrice == null) {
  this.originalTotalInvoicePrice = totalSalePrice || priceIncVat || 0
}
```

### Passo 3: Modificar `AssetSummary.vue` - Tornar Total Invoice Price editável

**Template changes** (inside the last row, Total Invoice Price):
- Add click handler to make editable
- Show text input when editing
- Call `applyDeltaToOtherDiscount` on confirm

**Script changes:**
```typescript
const isEditingTotal = ref(false)
const editedTotalInvoicePrice = ref(0)
const totalInvoiceInput = ref<any>(null)

const originalTotalInvoicePrice = ref(0)
const hasStoredOriginal = ref(false)

const totalInvoicePrice = computed(() => {
  const pd: any = pricingDetails.value
  const calculated = sanitizeToNumber(pd?.totalSalePrice) ||
    (sanitizeToNumber(totalIncVat.value) - sanitizeToNumber(tradeInValue.value) - sanitizeToNumber(ecoBonus.value))
  
  if (!hasStoredOriginal.value && calculated > 0) {
    originalTotalInvoicePrice.value = calculated
    hasStoredOriginal.value = true
  }
  
  return calculated
})

function startEditTotalInvoicePrice() {
  editedTotalInvoicePrice.value = totalInvoicePrice.value
  isEditingTotal.value = true
  nextTick(() => {
    totalInvoiceInput.value?.focus()
  })
}

function confirmEditTotalInvoicePrice() {
  isEditingTotal.value = false
  const newValue = editedTotalInvoicePrice.value
  
  if (!Number.isFinite(newValue) || newValue <= 0) return
  
  if (newValue > originalTotalInvoicePrice.value) {
    Notify.create({
      message: t('features.asset.components.demandAssetDetails.assetSummary.cannotIncreaseError'),
      type: 'negative',
      timeout: 3000
    })
    return
  }
  
  if (Math.abs(newValue - totalInvoicePrice.value) < 0.01) return
  
  assetStore.applyDeltaToOtherDiscount(newValue)
}

function cancelEditTotalInvoicePrice() {
  isEditingTotal.value = false
}
```

### Passo 4: Adicionar `Notify` import

```typescript
import { Notify } from 'quasar'
```

### Passo 5: Adicionar i18n keys

```json
// en-US
"cannotIncreaseError": "Total invoice price cannot be increased beyond the original value"

// fr-FR
"cannotIncreaseError": "Le prix total de la facture ne peut pas être supérieur à la valeur initiale"
```

## Ficheiros a alterar

1. `types/types.ts` — Adicionar `originalTotalInvoicePrice` a `AssetDealState`
2. `features/asset/stores/assets.ts` — `applyDeltaToOtherDiscount`, guardar `originalTotalInvoicePrice` em `setPricingDetails`
3. `features/asset/components/demandAssetDetails/AssetSummary.vue` — Tornar Total Invoice Price editável
4. `locales/en-US.json` — Adicionar `cannotIncreaseError`
5. `locales/fr-FR.json` — Adicionar tradução em francês

## Notas

1. **Ordem**: `applyDeltaToOtherDiscount` atualiza `otherDiscount` e chama `calculateDeal()`. O backend devolve os valores recalculados e o store atualiza.

2. **Circular dependency**: O valor Total Invoice Price recalculado pode diferir ligeiramente do valor introduzido devido a arredondamentos. Isto é aceite.
