import { ChatAnthropic } from "@langchain/anthropic";
import { PromptTemplate } from "@langchain/core/prompts";
import 'dotenv/config'; // Loads .env auto

// UNIT TEST FUNCTION (DO NOT DELETE!)
export async function testAnthropicConnection() {
    const llm = new ChatAnthropic({
        modelName: "claude-sonnet-4-5-20250929",
        temperature: 0 // set to 0 so its not creative?
    });

    try {
        const response = await llm.invoke("Reply with the exact word: Connected");
        return response.content;
    } catch (error) {
        console.error("Failed to connect to Claude:", error.message);
        throw error;
    }
}

// PRODUCTION AI ANALYST
export async function analyzeAnomaly(logData, anomalyScore) {
    const llm = new ChatAnthropic({
        modelName: "claude-sonnet-4-5-20250929",
        temperature: 0.2
    })

    const prompt = PromptTemplate.fromTemplate(`
        You are an elite Level 1 Security Operations Center (SOC) AI Analyst.
        Our machine learning model (Isolation Forest) has just flagged a network login as a high-risk anomaly.
        
        Anomaly Severity Score: {score} (Note: negative numbers are anomalies, further from 0 is worse).
        
        Raw Log Data:
        {log_data}
        
        Please analyze the raw log data and provide a concise, professional Incident Response Report for the engineering team. 
        Format your response EXACTLY like this:
        
        INCIDENT REPORT
        • What happened: [1-2 sentence explanation of the specific anomalous traits you see in the data, e.g., "A login was attempted at 3AM from an unmanaged Linux device using Firefox."]
        • Risk Level: [Low/Medium/Critical based on the anomaly score and data]
        • Recommended Action: [1 clear, immediate remediation step]
    `);

    const chain = prompt.pipe(llm);
    
    console.log("... AI Analyst is currently reviewing the log data ...");


    try {
        const response = await chain.invoke({
            score: anomalyScore,
            log_data: JSON.stringify(logData, null, 2)
        });

        return response.content;
    } catch (error) {
        console.error("AI Analysis Failed:", error.message);
        return "Error: Cound not generate AI report.";
    }
}