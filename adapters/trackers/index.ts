import { TrackerAdapter, TrackerConfig, TrackerType } from './base-adapter';
import { JiraAdapter } from './jira-adapter';
import { RedmineAdapter } from './redmine-adapter';
import { MockAdapter } from './mock-adapter';

export * from './base-adapter';

/**
 * Factory function to create the appropriate tracker adapter.
 */
export function createTrackerAdapter(config: TrackerConfig): TrackerAdapter {
  switch (config.type) {
    case 'jira':
      return new JiraAdapter(config);
    case 'redmine':
      return new RedmineAdapter(config);
    case 'mock':
    default:
      return new MockAdapter(config);
  }
}

/**
 * Load tracker configuration from the workflow state file.
 */
export function loadTrackerConfig(): TrackerConfig {
  try {
    const stateFile = `${process.env.HOME}/.workflow-installer-state.json`;
    const state = require(stateFile);
    
    return state.tracker || { type: 'mock' };
  } catch {
    return { type: 'mock' };
  }
}
