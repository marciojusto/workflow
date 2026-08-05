# Mission: LangChain4J for Personal AI Projects

## Why
You want to build a personal AI project on the JVM using modern Java (21+) with Kilo.ai as the LLM provider. The immediate goal is to understand LangChain4J's core concepts well enough to evaluate whether it's the right fit, and to be able to build a prototype that chains models, manages memory, calls tools, and coordinates multiple agents.

## Success looks like
- Run a working LangChain4J prototype against Kilo.ai in under 30 minutes
- Explain the difference between AiServices, agents, and chains in your own words
- Implement a simple RAG flow with document ingestion and retrieval
- Set up tool calling and see the model invoke it correctly
- Run two agents that communicate through a shared state or message bus
- Trace agent and chain calls end-to-end with OpenTelemetry
- Monitor token usage and cost per request in real time
- Debug a RAG pipeline by inspecting retrieved chunks and embedding distances

## Constraints
- Learning-first, not production-first: concepts before optimisation
- Kilo.ai is the required LLM provider
- Modern Java (21+) syntax expected; no legacy Java 8 patterns

## Out of scope
- Fine-tuning or custom model deployment
- Non-JVM frameworks (Python LangChain, etc.)
- Advanced prompt engineering psychology
