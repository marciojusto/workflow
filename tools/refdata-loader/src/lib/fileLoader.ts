import { readFileSync, existsSync } from "node:fs";

export function readJsonArray(filePath: string): any[] {
  if (!existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  const raw = readFileSync(filePath, "utf-8").trim();
  if (!raw) return [];
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [parsed];
}

export interface LoadFilesInput {
  creditApps: any[];
  quotes: any[];
  contracts: any[];
}

export function loadFiles(
  creditAppsPath: string,
  quotesPath: string,
  contractsPath?: string
): LoadFilesInput {
  const creditApps = readJsonArray(creditAppsPath);
  const quotes = readJsonArray(quotesPath);
  const contracts = contractsPath ? readJsonArray(contractsPath) : [];

  return { creditApps, quotes, contracts };
}

export function buildQuoteMap(quotes: any[]): Map<string, any> {
  const map = new Map<string, any>();
  for (const q of quotes) {
    const id = q.salesQuoteId;
    if (id) map.set(id, q);
  }
  return map;
}

export function buildContractMap(contracts: any[]): Map<string, any[]> {
  const map = new Map<string, any[]>();
  for (const c of contracts) {
    const caId =
      c.creditApplicationId ??
      c.creditAppId ??
      c.credit_application_id ??
      c.creditApplication?.creditApplicationId;
    if (!caId) continue;
    if (!map.has(caId)) map.set(caId, []);
    map.get(caId)!.push(c);
  }
  return map;
}
