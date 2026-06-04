import "dotenv/config";
import { Command } from "commander";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { resolveOktaToken, getTokenExpiration } from "./lib/auth.js";
import { createBsApi } from "./lib/bsApi.js";
import { toDealDocument } from "./lib/dealMapper.js";
import { connectToMongo, bulkUpsertDeals } from "./lib/mongo.js";
import { getConfig } from "./lib/environments.js";
import type { LoadFilesInput } from "./lib/fileLoader.js";
import { loadFiles, buildQuoteMap, buildContractMap } from "./lib/fileLoader.js";

function setupApi(target: string) {
  const cfg = getConfig(target);
  const { token } = resolveOktaToken();
  const exp = getTokenExpiration(token);
  const expiresIn = exp
    ? Math.round((exp.getTime() - Date.now()) / 60000)
    : "?";
  console.log(`🔧 ${cfg.baseURI} (x-env: ${cfg.gatewayEnv})`);
  console.log(`🔐 Token expires in: ${expiresIn} min\n`);
  const api = createBsApi({
    baseURI: cfg.baseURI,
    gatewayKey: cfg.gatewayKey,
    gatewayEnv: cfg.gatewayEnv,
    oktaToken: token,
  });
  return { cfg, api };
}

async function main() {
  const program = new Command()
    .name("refdata-loader")
    .description("Load salesperson data into reference MongoDB");

  // ── login ──────────────────────────────────
  program
    .command("login")
    .description("Fetch token via Keycloak password grant and save to ~/.config/refdata-loader/okta-token")
    .requiredOption("--username <user>", "Keycloak username")
    .requiredOption("--password <pass>", "Keycloak password")
    .option("--client-id <id>", "Keycloak client ID", "rcies-api-client")
    .option("--client-secret <secret>", "Keycloak client secret", "dVl2lxqBJkr7nqURxCDzM3SeWbpYLA9J")
    .option("--base-uri <uri>", "API gateway base URI", "https://rcidev-gateway.apie-rcibs.com/gateway")
    .option("--gateway-key <key>", "x-gateway-apikey", "7c3dbd58-7762-4317-93f5-49f2d2fcc907")
    .action(async (opts) => {
      const tokenUrl = `${opts.baseUri}/rcilocal-miles-keycloak-token-core/v1/auth/realms/master/protocol/openid-connect/token`;
      console.log(`🔑 Requesting token for ${opts.username}...`);

      const params = new URLSearchParams({
        grant_type: "password",
        client_id: opts.clientId,
        client_secret: opts.clientSecret,
        username: opts.username,
        password: opts.password,
      });

      let response: Response;
      try {
        response = await fetch(tokenUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-gateway-apikey": opts.gatewayKey,
          },
          body: params.toString(),
        });
      } catch (err: any) {
        console.error(`❌ Network error: ${err.message}`);
        process.exit(1);
      }

      if (!response.ok) {
        const body = await response.text().catch(() => "");
        console.error(`❌ Token request failed (${response.status}): ${body}`);
        process.exit(1);
      }

      const data = await response.json();
      const token = data.access_token;
      if (!token) {
        console.error(`❌ No access_token in response`);
        process.exit(1);
      }

      const configDir = join(homedir(), ".config", "refdata-loader");
      const tokenPath = join(configDir, "okta-token");
      const { writeFileSync } = await import("node:fs");
      writeFileSync(tokenPath, token + "\n", "utf-8");
      console.log(`✅ Token saved to ${tokenPath}`);
      console.log(`   Expires in: ${data.expires_in ?? "?"}s`);
      console.log("\nAgora podes usar os comandos whoami, sellers ou load.");
    });

  // ── whoami ─────────────────────────────────
  program
    .command("whoami")
    .description("Show current authenticated broker")
    .option("--target <name>", "Target: refdev | refasy", "refdev")
    .action(async (opts) => {
      try {
        const { api } = setupApi(opts.target);
        const broker = await api.getCurrentBroker();
        console.log("👤 Current broker:");
        console.log(JSON.stringify(broker, null, 2));
      } catch (err: any) {
        console.error(`❌ ${err.message}`);
        process.exit(1);
      }
    });

  // ── sellers ────────────────────────────────
  program
    .command("sellers")
    .description("List/search broker contacts")
    .argument("[search]", "Filter by broker ID or name")
    .option("--target <name>", "Target: refdev | refasy", "refdev")
    .action(async (search, opts) => {
      try {
        const { api } = setupApi(opts.target);
        const brokers = await api.searchBrokers(search || undefined);
        console.log(`📋 ${brokers.length} broker(s) found:\n`);
        for (const b of brokers) {
          const id = b.brokerContactId ?? b.id ?? "?";
          const name = b.brokerContactIdentification ?? b.name ?? b.identification ?? "?";
          console.log(`  [${id}] ${name}`);
        }
      } catch (err: any) {
        console.error(`❌ ${err.message}`);
        process.exit(1);
      }
    });

  // ── load-files ─────────────────────────────
  program
    .command("load-files")
    .description("Load credit apps, quotes and contracts from JSON files into MongoDB")
    .requiredOption("--target <name>", "Target: refdev | refasy")
    .requiredOption("--credit-apps <path>", "Path to credit-applications JSON file (array)")
    .requiredOption("--quotes <path>", "Path to quotes JSON file (array)")
    .option("--contracts <path>", "Path to contracts JSON file (array, optional)")
    .option("--dry-run", "Preview only, no DB write")
    .option("--mongo-uri <uri>", "Override MongoDB URI")
    .action(async (opts) => {
      // Validate files
      for (const key of ["creditApps", "quotes"]) {
        if (!existsSync(opts[key])) {
          console.error(`❌ File not found: ${opts[key]}`);
          process.exit(1);
        }
      }
      if (opts.contracts && !existsSync(opts.contracts)) {
        console.error(`❌ File not found: ${opts.contracts}`);
        process.exit(1);
      }

      // Load JSON
      console.log("📂 Loading JSON files...");
      const input: LoadFilesInput = loadFiles(opts.creditApps, opts.quotes, opts.contracts);
      console.log(`   → ${input.creditApps.length} credit applications`);
      console.log(`   → ${input.quotes.length} quotes`);
      console.log(`   → ${input.contracts.length} contracts\n`);

      // Build lookup maps
      const quoteMap = buildQuoteMap(input.quotes);
      const contractMap = buildContractMap(input.contracts);
      console.log(`🔗 Quote lookup: ${quoteMap.size} entries`);
      console.log(`🔗 Contract lookup: ${contractMap.size} entries\n`);

      // Convert to Deal documents
      const deals: any[] = [];
      let matched = 0;
      let skipped = 0;

      for (let i = 0; i < input.creditApps.length; i++) {
        const ca = input.creditApps[i];
        const quoteId =
          ca.salesQuote?.salesQuoteId ??
          ca.salesQuoteId ??
          ca.originatingQuote?.originatingQuoteId;

        if (!quoteId) {
          console.warn(`   ⚠️  [${i + 1}/${input.creditApps.length}] Credit app ${ca.creditApplicationId} has no salesQuoteId, skipping`);
          skipped++;
          continue;
        }

        const quote = quoteMap.get(quoteId);
        if (!quote) {
          console.warn(`   ⚠️  [${i + 1}/${input.creditApps.length}] Quote ${quoteId} not found in quotes file, skipping`);
          skipped++;
          continue;
        }

        const caId = ca.creditApplicationId;
        const contracts = caId ? contractMap.get(caId) ?? null : null;

        const deal = toDealDocument(quote, ca, null, contracts);
        deals.push(deal);
        matched++;
        process.stdout.write(`   ✅ [${i + 1}/${input.creditApps.length}] ${ca.creditApplicationId ?? quoteId}\n`);
      }

      console.log(`\n📊 Results: ${matched} converted, ${skipped} skipped\n`);

      if (deals.length === 0) {
        console.log("⚠️  No deals to load.");
        return;
      }

      // MongoDB config
      let cfg: ReturnType<typeof getConfig>;
      try {
        cfg = getConfig(opts.target);
      } catch (err: any) {
        console.error(`❌ ${err.message}`);
        process.exit(1);
      }

      // Update mongoUri if --mongo-uri provided
      if (opts.mongoUri) {
        cfg = { ...cfg, mongoUri: opts.mongoUri };
      }

      console.log(`🔌 Connecting to MongoDB: ${cfg.mongoUri}...`);
      let client: Awaited<ReturnType<typeof connectToMongo>>["client"] | null = null;

      try {
        const connected = await connectToMongo(cfg.mongoUri, cfg.mongoDb);
        client = connected.client;
        const db = connected.db;
        console.log("   ✅ Connected\n");

        if (opts.dryRun) {
          console.log("🏁 Dry-run mode. No data written.");
          console.log(`   Would upsert ${deals.length} documents into ${cfg.mongoDb}.deal`);
        } else {
          console.log(`💾 Writing ${deals.length} deals to MongoDB...`);
          const result = await bulkUpsertDeals(db, deals);
          console.log(`   ✅ ${result.inserted} inserted, ${result.updated} updated, ${result.errors} errors`);
        }

        console.log("\n═══════════════════════════════════════");
        console.log("  SUMMARY");
        console.log("═══════════════════════════════════════");
        console.log(`  Target:        ${opts.target}`);
        console.log(`  MongoDB:       ${cfg.mongoUri}/${cfg.mongoDb}`);
        console.log(`  Credit apps:   ${input.creditApps.length}`);
        console.log(`  Quotes loaded: ${input.quotes.length}`);
        console.log(`  Contracts:     ${input.contracts.length}`);
        console.log(`  Matched:       ${matched}`);
        console.log(`  Deals loaded:  ${deals.length}`);
        console.log(`  Skipped:       ${skipped}`);
        console.log("═══════════════════════════════════════\n");
      } finally {
        await client?.close();
      }
    });

  // ── load (API) ──────────────────────────────
  program
    .command("load")
    .description("Load credit applications and quotes from API into MongoDB")
    .requiredOption("--seller-id <id>", "Broker/salesperson ID")
    .requiredOption("--target <name>", "Target: refdev | refasy")
    .option("--dry-run", "Preview only, no DB write")
    .action(async (opts) => {
      const { cfg, api } = setupApi(opts.target);

      console.log(`🔌 Connecting to MongoDB: ${cfg.mongoUri}...`);
      let client: Awaited<ReturnType<typeof connectToMongo>>["client"] | null = null;

      try {
        const connected = await connectToMongo(cfg.mongoUri, cfg.mongoDb);
        client = connected.client;
        const db = connected.db;
        console.log("   ✅ Connected\n");

        console.log(`📡 Fetching credit applications for seller ${opts.sellerId}...`);
        let creditApps: any[];
        try {
          creditApps = await api.getCreditApplications(opts.sellerId);
        } catch (err: any) {
          console.error(`   ❌ API error: ${err.message}`);
          process.exit(1);
        }
        console.log(`   → ${creditApps.length} credit applications found\n`);

        if (creditApps.length === 0) {
          console.log("⚠️  No credit applications found.");
          return;
        }

        const deals: any[] = [];
        let errors = 0;

        for (let i = 0; i < creditApps.length; i++) {
          const ca = creditApps[i];
          const quoteId =
            ca.salesQuote?.salesQuoteId ??
            ca.salesQuoteId ??
            ca.originatingQuote?.originatingQuoteId;

          if (!quoteId) {
            console.warn(`   ⚠️  [${i + 1}/${creditApps.length}] Credit app ${ca.creditApplicationId} has no salesQuoteId, skipping`);
            errors++;
            continue;
          }

          try {
            const quote = await api.getSalesQuote(quoteId);
            const carConfig = quote?.carConfiguration || quote?.car || {};
            const catalogCarId = carConfig?.catalogCarId;

            let catalogOptions: any[] | null = null;
            if (catalogCarId) {
              try {
                const resp = await api.getCatalogOptions(catalogCarId);
                catalogOptions = resp?.catalogOptions ?? null;
              } catch {
                // non-fatal
              }
            }

            const deal = toDealDocument(quote, ca, catalogOptions);
            deals.push(deal);
            process.stdout.write(`   ✅ [${i + 1}/${creditApps.length}] Quote ${quoteId}\n`);
          } catch (err: any) {
            console.error(`   ❌ [${i + 1}/${creditApps.length}] Quote ${quoteId}: ${err.message}`);
            errors++;
          }
        }

        console.log(`\n📊 Results: ${deals.length} converted, ${errors} errors\n`);

        if (opts.dryRun) {
          console.log("🏁 Dry-run mode.");
          console.log(`   Would upsert ${deals.length} documents into ${opts.target}.deal`);
        } else {
          console.log(`💾 Writing ${deals.length} deals to MongoDB...`);
          const result = await bulkUpsertDeals(db, deals);
          console.log(`   ✅ ${result.inserted} inserted, ${result.updated} updated, ${result.errors} errors`);
        }

        console.log("\n═══════════════════════════════════════");
        console.log("  SUMMARY");
        console.log("═══════════════════════════════════════");
        console.log(`  Seller ID:     ${opts.sellerId}`);
        console.log(`  Target:        ${opts.target}`);
        console.log(`  API Gateway:   ${cfg.baseURI} (x-env: ${cfg.gatewayEnv})`);
        console.log(`  MongoDB:       ${cfg.mongoUri}/${cfg.mongoDb}`);
        console.log(`  Credit apps:   ${creditApps.length}`);
        console.log(`  Deals loaded:  ${deals.length}`);
        console.log(`  Errors:        ${errors}`);
        console.log("═══════════════════════════════════════\n");
      } finally {
        await client?.close();
      }
    });

  const args = process.argv.slice(2);
  if (args.length === 0) {
    program.outputHelp();
    return;
  }

  await program.parseAsync(process.argv);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
