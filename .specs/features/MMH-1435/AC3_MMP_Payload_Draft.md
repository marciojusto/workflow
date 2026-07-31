# Draft: Complete AC3 Payload for MMP Calculation

## Overview

If the AC3 formulas (Total Exc. VAT, Total Incl. VAT, Total Invoice Price) were calculated entirely by the MMP backend, the frontend would need to send a complete payload with all input fields.

---

## Payload Structure

### Main Request: `POST /sales-quotes/{sales_quote_id}/actions/calculations`

```json
{
  "payload": {
    "quotationTemplate": {
      "quotationTemplateId": "string"
    },
    "configOptions": [
      {
        "configOptionId": "string",
        "isSelected": true
      }
    ],
    "basePrice": 10950.00,
    "transportCost": 0.00,
    "tax": 0.00,
    "exemptQuote": 0.00,
    "options": [
      {
        "optionId": "string",
        "name": "string",
        "priceExcVat": 0.00
      }
    ],
    "accessories": [
      {
        "name": "string",
        "priceExcVat": 0.00
      }
    ],
    "transformAccessories": [
      {
        "name": "string",
        "priceIncVat": 0.00
      }
    ],
    "fees": [
      {
        "name": "string",
        "priceExcVat": 0.00
      }
    ],
    "oemServices": 0.00,
    "registrationTax": 0.00,
    "registrationTaxDiscount": 0.00,
    "freeFeeIncVat": 0.00,
    "tradeInValue": 0.00,
    "ecoBonus": 0.00
  },
  "calculationData": {
    "vatPercentage": 22,
    "oemDiscounts": {
      "amount": 0.00
    },
    "otherDiscounts": {
      "amount": 0.00
    },
    "productConfiguration": {
      "services": [
        {
          "reference": "ECO Bonus",
          "choices": [
            { "id": "400228", "isSelected": true },
            { "id": "400229", "isSelected": false }
          ],
          "qualifierSettings": [
            {
              "reference": "Hyperfront Value",
              "value": "0"
            }
          ]
        }
      ]
    }
  }
}
```

---

## Field Mapping to AC3 Formulas

### Formula 1: Total Exc. VAT
```
Total Exc. VAT = basePrice + optionsTotal + transportCost + tax + exemptQuote − oemDiscount − otherDiscount
```

| AC3 Field | Payload Field | Type | Required |
|-----------|---------------|------|----------|
| Catalogue Price | `basePrice` | `number` | ✅ |
| Options | `options[]` (sum of `priceExcVat`) | `array` | ✅ |
| Transport Cost | `transportCost` | `number` | ✅ |
| Car Tax | `tax` | `number` | ✅ |
| Exempt Quote | `exemptQuote` | `number` | ✅ |
| Discount (OEM) | `oemDiscounts.amount` | `number` | ✅ |
| Discount (Other) | `otherDiscounts.amount` | `number` | ✅ |

---

### Formula 4: Total Incl. VAT
```
Total Incl. VAT = Total Exc. VAT + vatAmount + oemServices + accessoriesTotalIncVat + registrationTaxNet + freeFeeIncVat
```

| AC3 Field | Payload Field | Type | Required |
|-----------|---------------|------|----------|
| Total Exc. VAT | *(calculated by MMP)* | `number` | Output |
| VAT Amount | *(calculated by MMP)* | `number` | Output |
| VAT Percentage | `vatPercentage` | `number` | ✅ |
| OEM Services | `oemServices` | `number` | ✅ |
| Accessories | `accessories[]` + `transformAccessories[]` | `array` | ✅ |
| Registration Tax Net | `registrationTax − registrationTaxDiscount` | `number` | ✅ |
| Free Fee Inc. VAT | `freeFeeIncVat` | `number` | ✅ |

---

### Formula 5: Total Invoice Price
```
Total Invoice Price = Total Incl. VAT − tradeInValue − ecoBonus
```

| AC3 Field | Payload Field | Type | Required |
|-----------|---------------|------|----------|
| Total Incl. VAT | *(calculated by MMP)* | `number` | Output |
| Trade In | `tradeInValue` | `number` | ✅ |
| Eco Bonus | `ecoBonus` | `number` | ✅ |

---

## Complete Field List

### Payload Fields

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `quotationTemplate.quotationTemplateId` | `string` | Template ID | `assetStore.quotationTemplateId` |
| `configOptions` | `array` | Selected catalog options | From asset options |
| `basePrice` | `number` | Catalogue price | `pricingDetails.basePrice` |
| `transportCost` | `number` | Transport cost | `pricingDetails.transportCost` |
| `tax` | `number` | Car tax | `pricingDetails.tax` or `totals.fees` |
| `exemptQuote` | `number` | Exempt quote | `pricingDetails.exemptQuote` |
| `options` | `array` | List of options | `assets[0].options[]` |
| `accessories` | `array` | List of accessories | `assets[0].accessories[]` |
| `transformAccessories` | `array` | Transform accessories | `assets[0].transformAccessories` |
| `fees` | `array` | List of fees | `assets[0].fees[]` |
| `oemServices` | `number` | OEM services | `pricingDetails.oemServices` |
| `registrationTax` | `number` | Registration tax | `pricingDetails.registrationTax` |
| `registrationTaxDiscount` | `number` | Registration tax discount | `pricingDetails.registrationTaxDiscount` |
| `freeFeeIncVat` | `number` | Free fee inc. VAT | `pricingDetails.freeFeeIncVat` |
| `tradeInValue` | `number` | Trade in value | `discount.tradeInValue` |
| `ecoBonus` | `number` | Eco bonus | `discount.ecoBonus` |

### CalculationData Fields

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| `vatPercentage` | `number` | VAT percentage (e.g., 22) | `pricingDetails.vatPercentage` |
| `oemDiscounts.amount` | `number` | OEM discount in € | `discount.oemDiscount` (if €) or calculated from % |
| `otherDiscounts.amount` | `number` | Other discount in € | `discount.otherDiscount` (if €) or calculated from % |
| `productConfiguration.services` | `array` | Services for ECO bonus | ECO bonus service structure |

---

## Response Expected from MMP

The MMP should return all calculated fields:

```json
{
  "data": {
    "basePrice": 10950.00,
    "priceExcVat": 10950.00,
    "optionsTotal": 0.00,
    "transportCost": 0.00,
    "tax": 0.00,
    "exemptQuote": 0.00,
    "totalDiscounts": 0.00,
    "totalExcVat": 10950.00,
    "vatPercentage": 22,
    "vatAmount": 2409.00,
    "oemServices": 0.00,
    "accessoriesIncVat": 0.00,
    "transformAccessoriesIncVat": 0.00,
    "accessoriesTotalIncVat": 0.00,
    "registrationTax": 0.00,
    "registrationTaxDiscount": 0.00,
    "registrationTaxNet": 0.00,
    "freeFeeIncVat": 0.00,
    "totalIncVat": 13359.00,
    "tradeInValue": 0.00,
    "ecoBonus": 0.00,
    "totalSalePrice": 13359.00
  }
}
```

---

## Implementation Considerations

### 1. When to send full payload?
- On initial load of Asset tab
- When any AC3 input field changes (options, accessories, fees, discounts, etc.)

### 2. Performance impact
- Current approach: Only changed items sent to backend
- Full AC3 approach: Entire payload sent on every change
- Mitigation: Debounce requests (350-500ms)

### 3. Caching
- Backend should cache calculated values
- Only recalculate when inputs change

### 4. Validation
- Frontend validates inputs before sending
- Backend re-validates all fields

---

## Questions for Backend Team

1. Does MMP support receiving all AC3 fields in a single calculation call?
2. What is the expected response structure?
3. Should we send VAT as `vatPercentage` or `vatCode`?
4. How should options/accessories totals be sent (pre-calculated or raw)?
5. Does MMP support the `productConfiguration.services` structure for ECO Bonus?
