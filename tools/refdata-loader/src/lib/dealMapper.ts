import type { DealDocument } from "../types/deal.js";

function getValueAtPath(obj: any, path: string): unknown {
  return path.split(".").reduce((acc, key) => acc?.[key], obj);
}

function resolveOptions(
  carConfig: any,
  catalogOptions: any[] | null
): any[] | null {
  if (carConfig?.vehicleOptionConfigurations) {
    return carConfig.vehicleOptionConfigurations
      .filter((opt: any) => opt?.isSelected)
      .map((opt: any) => ({
        optionName: opt?.description?.translation,
        description: opt?.description?.translation,
        priceExcVat: opt?.catalogPrice?.value,
        priceIncVat: opt?.consumerPrice?.value,
        optionId: opt?.optionCode,
      }));
  }
  if (catalogOptions) {
    return catalogOptions.map((opt: any) => ({
      optionName: opt?.description?.translation,
      description: opt?.description?.translation,
      priceExcVat: opt?.catalogPrice?.value,
      priceIncVat: opt?.consumerPrice?.value,
      optionId: opt?.catalogOptionId,
    }));
  }
  return null;
}

function resolveCarConfig(quote: any): any {
  return quote?.carConfiguration || quote?.car || {};
}

function resolveCustomerName(customer: any): string | null {
  if (!customer) return null;
  const individual = customer?.individualPerson;
  if (!individual) return customer?.tradingName ?? null;
  const last = individual?.lastName ?? "";
  const first = individual?.firstName ?? "";
  return [last, first].filter(Boolean).join(" ");
}

function getContractStatus(contracts: any[]): { statusId: string | null; groupId: string | null } {
  if (!contracts || contracts.length === 0) return { statusId: null, groupId: null };
  const last = contracts[contracts.length - 1];
  return {
    statusId: last?.status?.enumId ?? last?.contractStatus?.enumId ?? null,
    groupId: last?.status?.enumGroupId ?? last?.contractStatus?.enumGroupId ?? null,
  };
}

function getContractId(contracts: any[]): string | null {
  if (!contracts || contracts.length === 0) return null;
  return contracts[contracts.length - 1]?.contractId ?? null;
}

function getBrokerContact(quote: any): any {
  return quote?.brokerContact ?? quote?.brokerContactRepresentation ?? null;
}

export function toDealDocument(
  quote: any,
  creditApp: any | null,
  catalogOptions: any[] | null,
  contracts: any[] | null = null
): DealDocument {
  const carConfig = resolveCarConfig(quote);
  const customer = quote?.customer ?? {};
  const options = resolveOptions(carConfig, catalogOptions);
  const broker = getBrokerContact(quote);

  const vatEnumId: string | null =
    carConfig?.catalogVatCode?.enumId ??
    carConfig?.catalogVATCode?.enumId ??
    null;

  const now = new Date();
  const contractStatus = getContractStatus(contracts ?? []);

  const brokerId: string | null = broker?.brokerContactId ?? null;

  return {
    miles_sales_quote_id: quote?.salesQuoteId ?? null,
    offer_id: quote?.salesQuoteId ?? null,
    offer_reference: quote?.reference ?? null,

    customer_name: resolveCustomerName(customer),
    customer_id: getValueAtPath(customer, "customerId") as string ?? null,
    person_id:
      (getValueAtPath(customer, "individualPerson.personId") as string) ??
      null,
    customer_official_registration:
      (getValueAtPath(customer, "individualPerson.officialRegistration") as string) ??
      null,

    creation_date: now,
    expiration_date: quote?.expirationDate
      ? new Date(quote.expirationDate)
      : null,
    creditDecisionExpiryDate: creditApp?.creditDecisionExpiryDate
      ? new Date(creditApp.creditDecisionExpiryDate)
      : null,
    last_sync_timestamp: now,
    last_update_time: now,
    rejected_at: null,

    brand: (getValueAtPath(carConfig, "makeName.translation") as string) ?? null,
    model: (getValueAtPath(carConfig, "modelName.translation") as string) ?? null,
    asset_id: (carConfig?.catalogCarId as string) ?? null,
    base_catalog_price: (getValueAtPath(carConfig, "catalogPrice.value") as number) ?? null,
    price_inc_vat:
      (carConfig?.netPriceInclVAT?.value ??
        carConfig?.netPriceInclVat?.value ??
        null) as number | null,
    price_exc_vat: (carConfig?.netPrice?.value as number) ?? null,
    total_sale_price: (getValueAtPath(carConfig, "consumerPrice.value") as number) ?? null,
    power_hp: (carConfig?.dinHp as number) ?? null,
    power_kw: ((carConfig?.kW ?? carConfig?.kw) as number) ?? null,
    agw: (getValueAtPath(carConfig, "maxWeight.value") as number) ?? null,
    fuel_type:
      (getValueAtPath(carConfig, "engineFuelType.translation") as string | null) ??
      (getValueAtPath(carConfig, "fuelType.translation") as string | null) ??
      null,
    fiscal_type:
      (getValueAtPath(carConfig, "nature.translation") as string | null) ??
      (getValueAtPath(carConfig, "fiscalType.translation") as string | null) ??
      null,

    monthly_payment: null,
    financed_amount: 0,
    discount: (carConfig?.defaultDiscountAmount as number) ?? null,
    tax: (getValueAtPath(carConfig, "tax.value") as number) ?? null,
    vat_percent: vatEnumId,
    vat_percentage: null,
    vat_amount: null,

    quote_options: options,
    quote_calculation: {
      options: options ?? [],
      vatPercent: vatEnumId,
    },
    quotation_template: null,
    quotation_template_id: (quote?.quotationTemplateId as string) ?? null,
    bareme_restrictions: null,

    workflow: creditApp?.creditApplicationId ? "proposal" : "simulation",
    status: (getValueAtPath(quote, "quoteStatus.translation") as string) ?? null,

    overview_status: null,
    hyper_front_status: null,
    hyper_front_action: null,

    contractValidated: null,
    all_proposal_stipulation_filled: null,

    miles_sales_quote_status_id: (getValueAtPath(quote, "quoteStatus.enumId") as string) ?? null,
    miles_sales_quote_status_groupe_id: (getValueAtPath(quote, "quoteStatus.enumGroupId") as string) ?? null,
    miles_credit_application_status_id: creditApp?.status?.enumId ?? null,
    miles_credit_application_status_groupe_id: creditApp?.status?.enumGroupId ?? null,
    miles_credit_application_decision_id: creditApp?.decision?.enumId ?? null,
    miles_credit_application_decision_groupe_id: creditApp?.decision?.enumGroupId ?? null,
    miles_pending_contract_status_id: contractStatus.statusId,
    miles_pending_contract_status_groupe_id: contractStatus.groupId,

    cancel_raison: null,

    product_type: (getValueAtPath(quote, "quoteProduct.productConfiguration.reference") as string) ?? null,
    client_type: null,
    client_subtype: null,
    new_used: (getValueAtPath(quote, "vehicle.condition.translation") as string | null) ?? null,
    sales_channel: (getValueAtPath(quote, "quoteReason.translation") as string) ?? null,
    signature_type: "ELECTRONIC",
    seller: broker?.brokerContactIdentification?.trim() || null,
    seller_id: brokerId,
    dealership:
      (Array.isArray(quote?.brokerCompanies) && quote.brokerCompanies.length > 0
        ? quote.brokerCompanies[0]?.tradingName
        : null) ?? null,

    miles_credit_application_id: creditApp?.creditApplicationId ?? null,
    miles_pending_contract_id: getContractId(contracts ?? []),

    read_state: true,
    freezed: false,
    to_be_expired: false,

    is_syncing: false,
    sync_locked_at: null,

    dealership_id: brokerId,
    aditional_data: {
      additional_data_id: null,
      bareme_description: null,
      asset_price: (getValueAtPath(carConfig, "consumerPrice.value") as number) ?? null,
      financed_amount: 0,
      installment: 0,
      duration: (getValueAtPath(quote, "quoteProduct.term.value") as number) ?? 36,
      proposal_submission_date: null,
      end_of_validity_period: null,
      dealership_location: null,
      sales_channel: (getValueAtPath(quote, "quoteReason.translation") as string) ?? null,
      signature_type: "ELECTRONIC",
    },

    parties: [],
    old_sales_quote: null,
    old_reference: null,
  };
}
