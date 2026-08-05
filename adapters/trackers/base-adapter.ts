/**
 * Base interface for task tracker adapters.
 * All tracker adapters must implement this interface.
 */
export interface Ticket {
  id: string;
  title: string;
  description: string;
  acceptanceCriteria: string[];
  status: string;
  assignee?: string;
  reporter?: string;
  created: string;
  updated: string;
}

export interface LinkedIssue {
  id: string;
  title: string;
  description: string;
  relationship: string;
}

export interface Attachment {
  filename: string;
  mimeType: string;
  url: string;
  size?: number;
}

export interface RemoteLink {
  title: string;
  url: string;
}

export interface Comment {
  author: string;
  body: string;
  created: string;
}

export interface TrackerAdapter {
  /**
   * Get a ticket by ID
   */
  getTicket(ticketId: string): Promise<Ticket>;

  /**
   * Get linked issues for a ticket
   */
  getLinkedIssues(ticketId: string): Promise<LinkedIssue[]>;

  /**
   * Get attachments for a ticket
   */
  getAttachments(ticketId: string): Promise<Attachment[]>;

  /**
   * Get remote links for a ticket
   */
  getRemoteLinks(ticketId: string): Promise<RemoteLink[]>;

  /**
   * Get comments for a ticket
   */
  getComments(ticketId: string): Promise<Comment[]>;

  /**
   * Search for tickets
   */
  searchTickets(query: string): Promise<Ticket[]>;

  /**
   * Test connection to the tracker
   */
  testConnection(): Promise<boolean>;
}

export type TrackerType = 'jira' | 'redmine' | 'github' | 'gitlab' | 'azure' | 'linear' | 'mock';

export interface TrackerConfig {
  type: TrackerType;
  url?: string;
  token?: string;
  username?: string;
  password?: string;
  apiKey?: string;
  customHeaders?: Record<string, string>;
}
