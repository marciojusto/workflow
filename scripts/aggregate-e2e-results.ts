#!/usr/bin/env node
/**
 * E2E Result Aggregator for Multi-Agent Parallel Execution
 * 
 * Aggregates results from multiple parallel e2e-runner batches into a single report.
 * 
 * Usage:
 *   npx ts-node aggregate-e2e-results.ts <batch1.json> <batch2.json> [...]
 *   npx ts-node aggregate-e2e-results.ts --dir <batch-results-directory>
 * 
 * Output:
 *   JSON with aggregated results to stdout
 */

import * as fs from 'fs';
import * as path from 'path';

interface BatchResult {
  batch_id: string;
  ticket_id: string;
  ac_results: Record<number, 'pass' | 'fail'>;
  passed: boolean;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  duration_ms: number;
  screenshots: string[];
  errors: Array<{ ac: number; element: string; issue: string; severity: string; batch?: string }>;
}

interface AggregatedResult {
  ticket_id: string;
  total_acs: number;
  passed_acs: number;
  failed_acs: number;
  overall_passed: boolean;
  batches: Array<{ batch_id: string; passed: boolean; duration_ms: number }>;
  total_duration_ms: number;
  all_screenshots: string[];
  all_errors: Array<{ ac: number; element: string; issue: string; severity: string; batch: string }>;
  summary: string;
}

function aggregateResults(batchResults: BatchResult[]): AggregatedResult {
  if (batchResults.length === 0) {
    return {
      ticket_id: 'UNKNOWN',
      total_acs: 0,
      passed_acs: 0,
      failed_acs: 0,
      overall_passed: false,
      batches: [],
      total_duration_ms: 0,
      all_screenshots: [],
      all_errors: [],
      summary: 'No batch results provided'
    };
  }

  const ticketId = batchResults[0]?.ticket_id || 'UNKNOWN';
  
  const allAcResults: Record<number, 'pass' | 'fail'> = {};
  const allScreenshots: string[] = [];
  const allErrors: Array<{ ac: number; element: string; issue: string; severity: string; batch: string }> = [];
  
  let maxDuration = 0;
  
  for (const batch of batchResults) {
    // Merge AC results
    Object.assign(allAcResults, batch.ac_results);
    
    // Collect screenshots
    allScreenshots.push(...batch.screenshots);
    
    // Collect errors with batch info
    for (const error of batch.errors) {
      allErrors.push({ ...error, batch: batch.batch_id });
    }
    
    // Track max duration (parallel execution = slowest batch)
    maxDuration = Math.max(maxDuration, batch.duration_ms);
  }
  
  const passedAcs = Object.values(allAcResults).filter(v => v === 'pass').length;
  const failedAcs = Object.values(allAcResults).filter(v => v === 'fail').length;
  
  // Generate summary
  const batchSummary = batchResults.map(b => 
    `${b.batch_id}: ${b.passed ? 'PASS' : 'FAIL'} (${b.duration_ms}ms)`
  ).join(', ');
  
  const summary = `Total: ${passedAcs}/${Object.keys(allAcResults).length} ACs passed | Batches: ${batchSummary}`;

  return {
    ticket_id: ticketId,
    total_acs: Object.keys(allAcResults).length,
    passed_acs: passedAcs,
    failed_acs: failedAcs,
    overall_passed: failedAcs === 0,
    batches: batchResults.map(b => ({
      batch_id: b.batch_id,
      passed: b.passed,
      duration_ms: b.duration_ms
    })),
    total_duration_ms: maxDuration,
    all_screenshots: allScreenshots,
    all_errors: allErrors,
    summary
  };
}

function loadBatchResultsFromFile(filePath: string): BatchResult {
  const content = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(content);
}

function loadBatchResultsFromDir(dirPath: string): BatchResult[] {
  const results: BatchResult[] = [];
  
  if (!fs.existsSync(dirPath)) {
    console.error(`Directory not found: ${dirPath}`);
    return results  }
  
  const files = fs.readdirSync(dirPath).filter(f => f.endsWith('.json'));
  
  for (const file of files) {
    const filePath = path.join(dirPath, file);
    try {
      const result = loadBatchResultsFromFile(filePath);
      results.push(result);
    } catch (e) {
      console.error(`Error loading ${file}: ${e}`);
    }
  }
  
  return results;
}

// CLI entry point
const args = process.argv.slice(2);

if (args.length === 0) {
  console.error('Usage: aggregate-e2e-results.ts <file1.json> [file2.json ...] or --dir <directory>');
  process.exit(1);
}

let batchResults: BatchResult[] = [];

if (args[0] === '--dir' && args[1]) {
  // Load from directory
  batchResults = loadBatchResultsFromDir(args[1]);
} else {
  // Load from individual files
  batchResults = args.map(f => loadBatchResultsFromFile(f));
}

const aggregated = aggregateResults(batchResults);
console.log(JSON.stringify(aggregated, null, 2));
process.exit(aggregated.overall_passed ? 0 : 1);
