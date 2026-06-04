export interface DealDocument {
  miles_sales_quote_id: string | null;
  offer_id: string | null;
  offer_reference: string | null;

  customer_name: string | null;
  customer_id: string | null;
  person_id: string | null;
  customer_official_registration: string | null;

  creation_date: Date | null;
  expiration_date: Date | null;
  creditDecisionExpiryDate: Date | null;
  last_sync_timestamp: Date | null;
  last_update_time: Date | null;
  rejected_at: Date | null;

  brand: string | null;
  model: string | null;
  asset_id: string | null;
  base_catalog_price: number | null;
  price_inc_vat: number | null;
  price_exc_vat: number | null;
  total_sale_price: number | null;
  power_hp: number | null;
  power_kw: number | null;
  agw: number | null;
  fuel_type: string | null;
  fiscal_type: string | null;

  monthly_payment: number | null;
  financed_amount: number | null;
  discount: number | null;
  tax: number | null;
  vat_percent: string | null;
  vat_percentage: number | null;
  vat_amount: number | null;

  quote_options: any;
  quote_calculation: any;
  quotation_template: string | null;
  quotation_template_id: string | null;
  bareme_restrictions: any;

  workflow: string | null;
  status: string | null;

  overview_status: string | null;
  hyper_front_status: string | null;
  hyper_front_action: string | null;

  contractValidated: boolean | null;
  all_proposal_stipulation_filled: boolean | null;

  miles_sales_quote_status_id: string | null;
  miles_sales_quote_status_groupe_id: string | null;
  miles_credit_application_status_id: string | null;
  miles_credit_application_status_groupe_id: string | null;
  miles_credit_application_decision_id: string | null;
  miles_credit_application_decision_groupe_id: string | null;
  miles_pending_contract_status_id: string | null;
  miles_pending_contract_status_groupe_id: string | null;

  cancel_raison: string | null;

  product_type: string | null;
  client_type: string | null;
  client_subtype: string | null;
  new_used: string | null;
  sales_channel: string | null;
  signature_type: string;
  seller: string | null;
  seller_id: string | null;
  dealership: string | null;

  miles_credit_application_id: string | null;
  miles_pending_contract_id: string | null;

  is_deal?: boolean | null;
  is_reopened?: boolean | null;
  read_state: boolean | null;
  freezed: boolean | null;
  to_be_expired: boolean | null;

  is_syncing: boolean;
  sync_locked_at: Date | null;

  dealership_id: string | null;
  aditional_data: {
    additional_data_id: string | null;
    bareme_description: string | null;
    asset_price: number | null;
    financed_amount: number | null;
    installment: number | null;
    duration: number | null;
    proposal_submission_date: Date | null;
    end_of_validity_period: Date | null;
    dealership_location: string | null;
    sales_channel: string | null;
    signature_type: string;
  };

  parties: any[];
  old_sales_quote: string | null;
  old_reference: string | null;
}
