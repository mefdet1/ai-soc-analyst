import express from 'express';
import { spawn } from 'node:child_process';
import { start } from 'node:repl';
import { analyzeAnomaly } from './ai_analyst.js';

const app = express();
const port = 3000;

app.use(express.json());

app.post('/api/v1/score-login', (req, res) => {
    const incomingLog = req.body;

    const pythonProcess = spawn('python', ['predict.py', JSON.stringify(incomingLog)]);

    let aiResult = '';
    let errorResult = '';

    pythonProcess.stdout.on('data', (data) => {
        aiResult += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorResult += data.toString();
    });

    pythonProcess.on('close', async (code) => {
        if (code !== 0 || errorResult) {
            console.error('Python script error: ${errorResult}');
            return res.status(500).json({ error: "Failed to process machine learning model."});
        }

        try {
            const startIndex = aiResult.indexOf('{');
            const endIndex = aiResult.indexOf('}');

            if (startIndex === -1 || endIndex === -1) {
                throw new Error("No JSON object found in Python output.");
            }

            const cleanJsonString = aiResult.substring(startIndex, endIndex + 1);

            const finalScore = JSON.parse(cleanJsonString);

            if (finalScore.risk_flag === true) {
                console.log(`\n [ALERT] High-risk anomaly detected! (Severity Score: ${finalScore.anomaly_score})`);
                console.log('Routing to AI Agent for investigation...\n');

                const aiReport = await analyzeAnomaly(incomingLog, finalScore.anomaly_score);

                console.log("\n============================================");
                console.log(aiReport);
                console.log("============================================\n");
            }

            res.status(200).json(finalScore);

        } catch (parseError) {
            console.error('\n--- PARSING ERROR ---');
            console.error('Reason:', parseError.message);
            console.error('Raw string received:', aiResult);
            console.error('-----------------------\n');
            res.status(500).json({ error: "Invalid response from scoring engine."});
        }
    });
});

app.listen(port, () => {
    console.log('Enterprise Risk API running on http://localhost:${port}');
    console.log('Awaiting sign-in logs on POST /api/v1/score-login...');
});