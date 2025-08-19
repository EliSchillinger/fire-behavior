import { Configuration, OpenAIApi } from "openai";

const openai = new OpenAIApi(new Configuration({
    apiKey: "",
}));

const functions = [
    /*{
        name: "query",
        description: "Searches a Weaviate database for relevant links.",
        parameters: {
            type: "object",
            properties: {
                query: { type: "string", description: "Search phrase to find links for." }
            },
            required: ["query"]
        }
    },*/
    {
        name: "fetch",
        description: "Fetches and extracts text from a provided URL.",
        parameters: {
            type: "object",
            properties: {
                url: { type: "string", description: "The URL to scrape." }
            },
            required: ["url"]
        }
    }
];

export async function generateResponse(userPrompt) {
    //Call LLM
    const initRes = await openai.createChatCompletion({
        model: "o3-mini",
        messages: [{ role: "user", content: userPrompt }],
        functions,
        function_call: auto
    });

    const call = initRes.data.choices[0].message.function_call;
    if(!call) return initRes.data.choices[0].message.content;
    const args = JSON.parse(call.arguments);
    let toolResponse = null;

    //Call MCP tools
    if(call.name === "query") {
        toolResponse = await fetch("http://localhost:5001/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(args)
        });
    }

    const toolResult = await toolResponse.json();

    //Send result back to LLM
    const finalRes = await openai.createChatCompletion({
        model: "o3-mini",
        messages: [
            { role: "user", content: userPrompt },
            {
                role:"function",
                name: call.name,
                content: JSON.stringify(toolResult)
            }
        ]
    });

    return finalRes.data.choices[0].message.content;
}