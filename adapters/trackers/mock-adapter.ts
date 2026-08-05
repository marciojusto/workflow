import { TrackerAdapter, Ticket, LinkedIssue, Attachment, RemoteLink, Comment, TrackerConfig } from './base-adapter';

/**
 * Mock adapter for testing and development.
 */
export class MockAdapter implements TrackerAdapter {
  private config: TrackerConfig;

  constructor(config: TrackerConfig) {
    this.config = config;
  }

  async getTicket(ticketId: string): Promise<Ticket> {
    return {
      id: ticketId,
      title: `Mock Ticket ${ticketId}`,
      description: 'This is a mock ticket for testing purposes.',
      acceptanceCriteria: [
        'User can perform action X',
        'System validates input Y',
        'Error handling works for case Z',
      ],
      status: 'In Progress',
      assignee: 'developer@example.com',
      reporter: 'user@example.com',
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
    };
  }

  async getLinkedIssues(ticketId: string): Promise<LinkedIssue[]> {
    return [
      {
        id: 'MOCK-001',
        title: 'Related mock issue',
        description: 'A related issue for testing',
        relationship: 'relates to',
      },
    ];
  }

  async getAttachments(ticketId: string): Promise<Attachment[]> {
    return [
      {
        filename: 'mock-attachment.pdf',
        mimeType: 'application/pdf',
        url: 'https://example.com/mock.pdf',
        size: 1024,
      },
    ];
  }

  async getRemoteLinks(ticketId: string): Promise<RemoteLink[]> {
    return [
      {
        title: 'Documentation',
        url: 'https://docs.example.com',
      },
    ];
  }

  async getComments(ticketId: string): Promise<Comment[]> {
    return [
      {
        author: 'user@example.com',
        body: 'This is a mock comment',
        created: new Date().toISOString(),
      },
    ];
  }

  async searchTickets(query: string): Promise<Ticket[]> {
    return [
      {
        id: 'MOCK-001',
        title: `Mock result for: ${query}`,
        description: 'Mock search result',
        acceptanceCriteria: [],
        status: 'Open',
        created: new Date().toISOString(),
        updated: new Date().toISOString(),
      },
    ];
  }

  async testConnection(): Promise<boolean> {
    return true;
  }
}
