import fs from 'node:fs';
import { ChatAnthropic } from "@langchain/anthropic";
import 'dotenv/config';

const csv = fs.readFileSync('presentation_blind_spots.csv', 'utf-8');
const lines = csv.trim().split('\n');
const headers = lines[0].split(',');
const records = lines.slice(1).map(line => {
    const vals = line.split(',');
    return Object.fromEntries(headers.map((h, i) => [h, vals[i]]));
});

const llm = new ChatAnthropic({ modelName: "claude-sonnet-4-5-20250929", temperature: 0.2 });

const prompt = `You are a SOC AI Analyst. Below are ${records.length} sign-in logs flagged as anomalies by our Isolation Forest model — these bypassed our legacy rules.

Produce a SECURITY POSTURE REPORT:
1. Top 3 attack patterns across these events
2. 5 most concerning individual logs (cite by their features)
3. Recommended new detection rules
4. Overall risk assessment

Data:
${JSON.stringify(records, null, 2)}`;

console.log(`Sending ${records.length} records to Claude...`);
const response = await llm.invoke(prompt);
console.log("\n=== BATCH ANOMALY REPORT ===\n");
console.log(response.content);