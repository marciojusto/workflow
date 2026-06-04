import { readFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

interface TokenInfo {
  token: string;
  source: string;
}

function findTokenFile(): string | null {
  const candidates = [
    join(process.cwd(), ".okta-token"),
    join(homedir(), ".config", "refdata-loader", "okta-token"),
  ];
  for (const path of candidates) {
    if (existsSync(path)) return path;
  }
  return null;
}

export function resolveOktaToken(): TokenInfo {
  const envToken = process.env.OKTA_TOKEN;
  if (envToken && envToken.length > 20) {
    return { token: envToken, source: "OKTA_TOKEN env" };
  }

  const file = findTokenFile();
  if (file) {
    const token = readFileSync(file, "utf-8").trim();
    if (token.length > 20) {
      return { token, source: file };
    }
  }

  throw new Error(
    "Okta token not found.\n" +
    "  1. Open http-clients/token.http in IntelliJ and run the request\n" +
    "  2. Copy the access_token to ~/.config/refdata-loader/okta-token\n" +
    "  Or set OKTA_TOKEN environment variable"
  );
}

export function decodeTokenPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const payload = parts[1];
    const decoded = Buffer.from(payload, "base64url").toString("utf-8");
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

export function getTokenExpiration(token: string): Date | null {
  const payload = decodeTokenPayload(token);
  if (!payload || typeof payload.exp !== "number") return null;
  return new Date(payload.exp * 1000);
}
