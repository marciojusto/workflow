import { MongoClient, Db } from "mongodb";
import type { DealDocument } from "../types/deal.js";

export async function connectToMongo(
  uri: string,
  dbName = "hyperfront"
): Promise<{ client: MongoClient; db: Db }> {
  const client = new MongoClient(uri);
  await client.connect();
  await client.db(dbName).command({ ping: 1 });
  const db = client.db(dbName);
  return { client, db };
}

export async function bulkUpsertDeals(
  db: Db,
  deals: DealDocument[]
): Promise<{ inserted: number; updated: number; errors: number }> {
  if (deals.length === 0) {
    return { inserted: 0, updated: 0, errors: 0 };
  }

  const collection = db.collection("deal");
  let inserted = 0;
  let updated = 0;
  let errors = 0;

  for (const deal of deals) {
    try {
      const result = await collection.updateOne(
        { miles_sales_quote_id: deal.miles_sales_quote_id },
        { $set: deal as any },
        { upsert: true }
      );
      if (result.upsertedCount > 0) inserted++;
      if (result.modifiedCount > 0) updated++;
    } catch (err) {
      console.error(
        `Error upserting deal ${deal.miles_sales_quote_id}:`,
        err
      );
      errors++;
    }
  }

  return { inserted, updated, errors };
}
