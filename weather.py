from openai import OpenAI
import os

weather_tool = {
    "type": "function",
    "function": {
        "name": "get_current_temperature",
        "description": "Gets the current temperature for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, e.g. San Francisco",
                },
            },
            "required": ["location"],
        },
    },
}

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

response = client.chat.completions.create(
    model="nvidia/nemotron-3.5-super-vl:free",
    messages=[{"role": "user", "content": "What's the temperature in London?"}],
    tools=[weather_tool],
)

for tool_call in response.choices[0].message.tool_calls or []:
    print(f"Function to call: {tool_call.function.name}")
    print(f"Arguments: {tool_call.function.arguments}")