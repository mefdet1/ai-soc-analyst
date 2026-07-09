import { test } from 'node:test';
import assert from 'node:assert';
import { testAnthropicConnection } from './ai_analyst.js';

test('Successfully connects to Anthropic Claude via LangChain', async () => {
    console.log("Pinging Claude via API...");
    

    const response = await testAnthropicConnection();
    

    assert.strictEqual(
        response.trim(), 
        "Connected", 
        "The model did not reply with the expected string."
    );
});