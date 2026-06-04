import { ofetch } from "ofetch";

export interface BsApiConfig {
  baseURI: string;
  gatewayKey: string;
  gatewayEnv: string;
  oktaToken: string;
}

export interface CreditApplication {
  creditApplicationId: string;
  salesQuote?: { salesQuoteId?: string };
  status?: { enumId?: string; enumGroupId?: string; translation?: string };
  decision?: { enumId?: string; enumGroupId?: string };
  expiryDate?: string;
  creditDecisionExpiryDate?: string;
  [key: string]: unknown;
}

export interface SalesQuote {
  salesQuoteId?: string;
  reference?: string;
  car?: any;
  carConfiguration?: any;
  quoteProduct?: any;
  brokerContactRepresentation?: any;
  brokerCompanies?: any[];
  customer?: any;
  quoteStatus?: any;
  expirationDate?: string;
  quotationTemplateId?: string;
  vehicle?: any;
  quoteReason?: any;
  [key: string]: unknown;
}

export interface CatalogOptionsResponse {
  catalogOptions?: any[];
  [key: string]: unknown;
}

export function createBsApi(config: BsApiConfig) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-gateway-apikey": config.gatewayKey,
    "x-keycloak-token": config.oktaToken,
    "x-env": config.gatewayEnv,
  };

  const api = ofetch.create({
    headers,
    timeout: 30000,
  });

  async function getCreditApplications(
    brokerContactId?: string
  ): Promise<CreditApplication[]> {
    const params: Record<string, string> = {};
    if (brokerContactId) params.brokerContactId = brokerContactId;

    const response: any = await api(
      `${config.baseURI}/rcilocal-miles-credit-retail-core/v1/credit-applications`,
      { params }
    );
    return Array.isArray(response) ? response : response?.data ?? [];
  }

  async function getSalesQuote(quoteId: string): Promise<SalesQuote> {
    return api(
      `${config.baseURI}/rcilocal-miles-quotation-core/v1/sales-quotes/${quoteId}`
    );
  }

  async function getCatalogOptions(
    catalogVehicleId: string
  ): Promise<CatalogOptionsResponse> {
    return api(
      `${config.baseURI}/rcilocal-miles-catalog-core/v1/catalog-vehicles/${catalogVehicleId}/catalog-options`
    );
  }

  async function getCurrentBroker(): Promise<any> {
    return api(
      `${config.baseURI}/rcilocal-miles-supplier-core/v1/broker-contact/current`
    );
  }

  async function searchBrokers(search?: string): Promise<any[]> {
    const params: Record<string, string> = {};
    if (search) params.broker_contact_id = search;
    const response: any = await api(
      `${config.baseURI}/rcilocal-miles-supplier-core/v1/broker-contacts`,
      { params }
    );
    return Array.isArray(response) ? response : response?.data ?? [];
  }

  return { getCreditApplications, getSalesQuote, getCatalogOptions, getCurrentBroker, searchBrokers };
}
