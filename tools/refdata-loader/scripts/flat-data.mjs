import { readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const dataDir = resolve(__dirname, '..', 'data');

const mappings = {
  'credit-applications.json': 'creditApplications',
  'quotes.json': 'salesQuotes',
  'contracts.json': 'pendingContracts',
};

for (const [file, key] of Object.entries(mappings)) {
  const path = resolve(dataDir, file);
  const raw = JSON.parse(readFileSync(path, 'utf-8'));
  const arr = Array.isArray(raw) ? raw : raw[key];
  if (!arr || !Array.isArray(arr)) {
    console.error(`\u26a0\ufe0f  Cannot find array '${key}' in ${file}`);
    process.exit(1);
  }
  const outPath = resolve(dataDir, file.replace('.json', '.flat.json'));
  writeFileSync(outPath, JSON.stringify(arr, null, 2));
  console.log(`\u2705 ${file} \u2192 ${arr.length} records \u2192 ${outPath.replace(/^.*\/data\//, 'data/')}`);
}
