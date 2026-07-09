import fs from 'node:fs';
import { ChatAnthropic } from "@langchain/anthropic";
import 'dotenv/config';

const csv = fs.readFileSync('top_anomalies_named.csv', 'utf-8');

const llm = new ChatAnthropic({
    modelName: "claude-sonnet-4-5-20250929",
    temperature: 0.2
});

const prompt = `You are a SOC analyst presenting findings to leadership.

Top anomalous logins flagged by our Isolation Forest model:

${csv}

Produce a SLIDE-READY report. Format EXACTLY like this — no preamble, no extra headers:

TOP USERS FLAGGED

1. [displayName]
   When/Where: [time + location]
   Why suspicious: [one plain-English sentence]
   Severity: Critical | High | Medium

2. [next user]
   ...

OVERALL: [one-sentence recommendation]

Be terse. This is for a slide. No fluff, no bullet points beyond what's shown.`;

console.log("Generating report...");
const response = await llm.invoke(prompt);
console.log("\n" + response.content);