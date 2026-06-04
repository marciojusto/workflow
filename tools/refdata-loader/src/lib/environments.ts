export interface EnvironmentConfig {
  baseURI: string;
  gatewayKey: string;
  /** Valor do header x-env: DEV | ASY | HFX */
  gatewayEnv: string;
  mongoUri: string;
  mongoDb: string;
}

const ENVIRONMENTS: Record<string, EnvironmentConfig> = {
  refdev: {
    baseURI: "https://rcidev-gateway.apie-rcibs.com/gateway",
    gatewayKey: "7c3dbd58-7762-4317-93f5-49f2d2fcc907",
    gatewayEnv: "DEV",
    mongoUri: "mongodb://localhost:27019",
    mongoDb: "hyperfront",
  },
  refasy: {
    baseURI: "https://rcidev-gateway.apie-rcibs.com/gateway",
    gatewayKey: "7c3dbd58-7762-4317-93f5-49f2d2fcc907",
    gatewayEnv: "ASY",
    mongoUri: "mongodb://localhost:27020",
    mongoDb: "hyperfront",
  },
};

export function getConfig(target: string): EnvironmentConfig {
  const env = ENVIRONMENTS[target];
  if (!env) {
    throw new Error(
      `Unknown target: ${target}. Available: ${Object.keys(ENVIRONMENTS).join(", ")}`
    );
  }

  return {
    baseURI: process.env.BASE_URI || env.baseURI,
    gatewayKey: process.env.GATEWAY_KEY || env.gatewayKey,
    gatewayEnv: process.env.GATEWAY_ENV || env.gatewayEnv,
    mongoUri: process.env[`MONGO_${target.toUpperCase()}_URI`] || env.mongoUri,
    mongoDb: process.env.MONGO_DB || env.mongoDb,
  };
}
