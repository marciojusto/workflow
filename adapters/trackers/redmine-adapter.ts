import { TrackerAdapter, Ticket, LinkedIssue, Attachment, RemoteLink, Comment, TrackerConfig } from './base-adapter';

/**
 * Redmine adapter using Redmine REST API.
 */
export class RedmineAdapter implements TrackerAdapter {
  private config: TrackerConfig;
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(config: TrackerConfig) {
    this.config = config;
    this.baseUrl = config.url || '';
    this.headers = {
      'Content-Type': 'application/json',
      ...(config.apiKey ? { 'X-Redmine-API-Key': config.apiKey } : {}),
      ...(config.customHeaders || {}),
    };
  }

  async getTicket(ticketId: string): Promise<Ticket> {
    const response = await fetch(`${this.baseUrl}/issues/${ticketId}.json`, {
      headers: this.headers,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch ticket: ${response.statusText}`);
    }

    const data = await response.json();
    const issue = data.issue;

    return {
      id: issue.id.toString(),
      title: issue.subject,
      description: issue.description || '',
      acceptanceCriteria: this.extractAcceptanceCriteria(issue.description || ''),
      status: issue.status?.name || '',
      assignee: issue.assigned_to?.name,
      reporter: issue.author?.name,
      created: issue.created_on,
      updated: issue.updated_on,
    };
  }

  async getLinkedIssues(ticketId: string): Promise<LinkedIssue[]> {
    const response = await fetch(`${this.baseUrl}/issues/${ticketId}.json?include=relations`, {
      headers: this.headers,
    });
    
    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    const relations = data.issue?.relations || [];

    return relations.map((rel: any) => ({
      id: rel.issue_to_id?.toString() || rel.issue_id?.toString(),
      title: rel.issue_to?.subject || rel.issue?.subject || '',
      description: '',
      relationship: rel.relation_type,
    }));
  }

  async getAttachments(ticketId: string): Promise<Attachment[]> {
    const response = await fetch(`${this.baseUrl}/issues/${ticketId}.json?include=attachments`, {
      headers: this.headers,
    });
    
    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    const attachments = data.issue?.attachments || [];

    return attachments.map((att: any) => ({
      filename: att.filename,
      mimeType: att.content_type,
      url: att.content_url,
      size: att.filesize,
    }));
  }

  async getRemoteLinks(ticketId: string): Promise<RemoteLink[]> {
    // Redmine doesn't have remote links in the same way as Jira
    return [];
  }

  async getComments(ticketId: string): Promise<Comment[]> {
    const response = await fetch(`${this.baseUrl}/issues/${ticketId}.json?include=journals`, {
      headers: this.headers,
    });
    
    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    const journals = data.issue?.journals || [];

    return journals.map((journal: any) => ({
      author: journal.user?.name || '',
      body: journal.notes || '',
      created: journal.created_on,
    }));
  }

  async searchTickets(query: string): Promise<Ticket[]> {
    const response = await fetch(`${this.baseUrl}/issues.json?limit=100&q=${encodeURIComponent(query)}`, {
      headers: this.headers,
    });
    
    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    const issues = data.issues || [];

    return issues.map((issue: any) => ({
      id: issue.id.toString(),
      title: issue.subject,
      description: issue.description || '',
      acceptanceCriteria: this.extractAcceptanceCriteria(issue.description || ''),
      status: issue.status?.name || '',
      created: issue.created_on,
      updated: issue.updated_on,
    }));
  }

  async testConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/users/current.json`, {
        headers: this.headers,
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  private extractAcceptanceCriteria(description: string): string[] {
    // Look for common AC patterns
    const acPatterns = [
      /acceptance criteria[:\s]*([\s\S]*?)(?=\n\n|\n#|$)/i,
      /ac[:\s]*([\s\S]*?)(?=\n\n|\n#|$)/i,
      /critérios de aceitação[:\s]*([\s\S]*?)(?=\n\n|\n#|$)/i,
    ];

    for (const pattern of acPatterns) {
      const match = description.match(pattern);
      if (match) {
        return match[1]
          .split('\n')
          .map(line => line.trim())
          .filter(line => line.startsWith('-') || line.startsWith('*') || line.match(/^\d+\./))
          .map(line => line.replace(/^[-*]\s*/, '').replace(/^\d+\.\s*/, ''));
      }
    }

    return [];
  }
}
