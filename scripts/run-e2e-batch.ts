#!/usr/bin/env node
/**
 * E2E Batch Runner for Multi-Agent Parallel Execution
 * 
 * Runs a batch of Playwright tests and outputs JSON results.
 * Used by e2e-runner agents in parallel execution mode.
 * 
 * Usage:
 *   npx ts-node run-e2e-batch.ts '{"ticketId":"MMH-1435","workflowId":"wf-123","acIndices":[1,2]}'
 * 
 * Output:
 *   JSON with batch results to stdout
 */

import { execSync } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

interface BatchConfig {
  ticketId: string;
  workflowId: string;
  acIndices: number[];
  appUrl?: string;
  timeout?: number;
}

interface AcResult {
  ac: number;
  status: 'pass' | 'fail';
  duration_ms: number;
  error?: string;
}

interface BatchResult {
  ticketId: string;
  batchId: string;
  acResults: Record<number, 'pass' | 'fail'>;
  acDetails: AcResult[];
  passed: boolean;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  duration_ms: number;
  screenshots: string[];
  errors: Array<{ ac: number; element: string; issue: string; severity: string }>;
}

function parsePlaywrightOutput(output: string, acIndices: number[]): {
  acResults: Record<number, 'pass' | 'fail'>;
  acDetails: AcResult[];
  totalTests: number;
  passedTests: number;
  failedTests: number;
  screenshots: string[];
  errors: Array<{ ac: number; element: string; issue: string; severity: string }>;
} {
  const acResults: Record<number, 'pass' | 'fail'> = {};
  const acDetails: AcResult[] = [];
  const screenshots: string[] = [];
  const errors: Array<{ ac: number; element: string; issue: string; severity: string }> = [];
  
  let totalTests = 0;
  let passedTests = 0;
  let failedTests = 0;

  try {
    // Parse JSON reporter output
    const report = JSON.parse(output);
    
    if (report.suites) {
      for (const suite of report.suites) {
        if (suite.specs) {
          for (const spec of suite.specs) {
            totalTests++;
            
            // Extract AC number from test title
            const acMatch = spec.title.match(/AC(\d+)/i);
            const acNumber = acMatch ? parseInt(acMatch[1]) : 0;
            
            const passed = spec.ok !== false;
            if (passed) {
              passedTests++;
              acResults[acNumber] = 'pass';
            } else {
              failedTests++;
              acResults[acNumber] = 'fail';
            }
            
            acDetails.push({
              ac: acNumber,
              status: passed ? 'pass' : 'fail',
              duration_ms: spec.duration || 0,
              error: spec.tests?.[0]?.results?.[0]?.error?.message
            });

            // Extract screenshots from results
            if (spec.tests?.[0]?.results) {
              for (const result of spec.tests[0].results) {
                if (result.attachments) {
                  for (const att of result.attachments) {
                    if (att.path && att.name === 'screenshot') {
                      screenshots.push(att.path);
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  } catch (e) {
    // Fallback: parse text output
    const lines = output.split('\n');
    for (const line of lines) {
      const passMatch = line.match(/(\d+)\s+passed/);
      const failMatch = line.match(/(\d+)\s+failed/);
      if (passMatch) passedTests = parseInt(passMatch[1]);
      if (failMatch) failedTests = parseInt(failMatch[1]);
    }
    totalTests = passedTests + failedTests;
  }

  return { acResults, acDetails, totalTests, passedTests, failedTests, screenshots, errors };
}

async function runBatch(config: BatchConfig): Promise<BatchResult> {
  const startTime = Date.now();
  const batchId = `batch-${config.acIndices.join('-')}`;
  
  // 1. Find test files for this batch
  const testFiles = config.acIndices.map(ac => 
    `tests/regression/${config.ticketId}_ac${ac}.spec.ts`
  );
  
  // 2. Check which test files exist
  const playwrightDir = path.join(__dirname, '../../playwright');
  const existingTests = testFiles.filter(f => {
    const fullPath = path.join(playwrightDir, f);
    return fs.existsSync(fullPath);
  });

  if (existingTests.length === 0) {
    return {
      ticketId: config.ticketId,
      batchId,
      acResults: Object.fromEntries(config.acIndices.map(ac => [ac, 'fail'])),
      acDetails: [],
      passed: false,
      totalTests: config.acIndices.length,
      passedTests: 0,
      failedTests: config.acIndices.length,
      duration_ms: Date.now() - startTime,
      screenshots: [],
      errors: [{ ac: 0, element: 'runner', issue: `No test files found for ACs: ${config.acIndices.join(', ')}`, severity: 'critical' }]
    };
  }

  // 3. Run Playwright with specific files
  const testPath = existingTests.join(' ');
  const reportDir = path.join(playwrightDir, 'reports/batches', batchId);
  
  // Ensure report directory exists
  fs.mkdirSync(reportDir, { recursive: true });

  try {
    const output = execSync(
      `cd "${playwrightDir}" && npx playwright test ${testPath} --reporter=json --output="${reportDir}"`,
      { 
        encoding: 'utf-8', 
        timeout: config.timeout || 300000,
        env: { ...process.env, CI: 'true' }
      }
    );
    
    // 4. Parse results
    const parsed = parsePlaywrightOutput(output, config.acIndices);
    
    return {
      ticketId: config.ticketId,
      batchId,
      acResults: parsed.acResults,
      acDetails: parsed.acDetails,
      passed: parsed.failedTests === 0,
      totalTests: parsed.totalTests,
      passedTests: parsed.passedTests,
      failedTests: parsed.failedTests,
      duration_ms: Date.now() - startTime,
      screenshots: parsed.screenshots,
      errors: parsed.errors
    };
  } catch (error: any) {
    // Parse error output
    const stderr = error.stderr || '';
    const stdout = error.stdout || '';
    
    const parsed = parsePlaywrightOutput(stdout, config.acIndices);
    
    return {
      ticketId: config.ticketId,
      batchId,
      acResults: { ...parsed.acResults, ...Object.fromEntries(config.acIndices.map(ac => [ac, 'fail'])) },
      acDetails: parsed.acDetails,
      passed: false,
      totalTests: config.acIndices.length,
      passedTests: parsed.passedTests,
      failedTests: config.acIndices.length,
      duration_ms: Date.now() - startTime,
      screenshots: parsed.screenshots,
      errors: [
        ...parsed.errors,
        { ac: 0, element: 'runner', issue: stderr || error.message, severity: 'critical' }
      ]
    };
  }
}

// CLI entry point
const args = process.argv.slice(2);
const config: BatchConfig = JSON.parse(args[0] || '{}');

runBatch(config).then(result => {
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.passed ? 0 : 1);
}).catch(error => {
  console.error(JSON.stringify({
    error: error.message,
    stack: error.stack
  }, null, 2));
  process.exit(1);
});
