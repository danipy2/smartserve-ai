"""
SmartServe AI — RAG Chain
Core RAG (Retrieval-Augmented Generation) chain that answers user questions
using context retrieved from the knowledge base, with confidence scoring
and source citation.
"""

from typing import Dict, List, Optional, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import Document

import config
from core.vector_store import similarity_search_with_scores


# --- Prompt Templates ---

SYSTEM_PROMPT = """You are SmartServe AI, an intelligent customer support assistant. 
Your role is to answer customer questions accurately using ONLY the provided context from the company's knowledge base.

RULES:
1. Answer ONLY based on the provided context. Do not make up information.
2. If the context doesn't contain enough information to fully answer the question, clearly state what you found and what you couldn't find.
3. Be professional, helpful, and concise.
4. When referencing information, mention which source document it came from.
5. If the context is completely irrelevant to the question, say: "I don't have enough information in my knowledge base to answer this question. Let me connect you with a human agent."

CONTEXT FROM KNOWLEDGE BASE:
{context}

CONVERSATION HISTORY:
{chat_history}
"""

HUMAN_PROMPT = """{question}"""

CONFIDENCE_PROMPT = """Based on the context provided and the question asked, rate your confidence in your answer on a scale of 0.0 to 1.0.

Context: {context}
Question: {question}
Your Answer: {answer}

Respond with ONLY a number between 0.0 and 1.0, nothing else.
- 1.0 = The answer is directly and completely stated in the context
- 0.7 = The answer is mostly supported by the context with minor inference
- 0.4 = The answer requires significant inference or the context is partially relevant
- 0.1 = The context is barely relevant to the question
- 0.0 = The context has no relevant information"""


def get_llm() -> ChatGoogleGenerativeAI:
    """Initialize the Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=config.LLM_TEMPERATURE,
    )


def format_context(documents: List[Document]) -> str:
    """Format retrieved documents into a context string with source citations."""
    if not documents:
        return "No relevant documents found in the knowledge base."

    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "Unknown")
        chunk_idx = doc.metadata.get("chunk_index", "?")
        context_parts.append(
            f"[Source: {source}, Section {chunk_idx}]\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(context_parts)


def format_chat_history(history: List[Dict]) -> str:
    """Format conversation history for the prompt."""
    if not history:
        return "No previous conversation."

    formatted = []
    for msg in history[-6:]:  # Keep last 6 messages (3 turns)
        role = msg.get("role", "user")
        content = msg.get("content", "")
        formatted.append(f"{role.upper()}: {content}")

    return "\n".join(formatted)


def extract_sources(documents: List[Document]) -> List[Dict]:
    """Extract source information from retrieved documents."""
    sources = []
    seen = set()
    for doc in documents:
        source = doc.metadata.get("source", "Unknown")
        if source not in seen:
            seen.add(source)
            sources.append({
                "document": source,
                "chunk_index": doc.metadata.get("chunk_index", 0),
                "preview": doc.page_content[:150] + "...",
            })
    return sources


async def evaluate_confidence(
    llm: ChatGoogleGenerativeAI,
    context: str,
    question: str,
    answer: str,
) -> float:
    """
    Use the LLM to self-evaluate its confidence in the answer.
    Returns a confidence score between 0.0 and 1.0.
    """
    try:
        response = await llm.ainvoke(
            CONFIDENCE_PROMPT.format(
                context=context, question=question, answer=answer
            )
        )
        score = float(response.content.strip())
        return max(0.0, min(1.0, score))  # Clamp to [0, 1]
    except (ValueError, TypeError):
        return 0.5  # Default to medium confidence if parsing fails


async def query(
    question: str,
    chat_history: Optional[List[Dict]] = None,
    collection_name: str = "default",
) -> Dict:
    """
    Main RAG query function. Takes a user question, retrieves relevant context,
    generates an answer, and evaluates confidence.

    Args:
        question: The user's question.
        chat_history: Previous conversation messages.
        collection_name: Vector store collection to search.

    Returns:
        Dictionary with answer, confidence, sources, and escalation status.
    """
    if chat_history is None:
        chat_history = []

    llm = get_llm()

    # Step 1: Retrieve relevant documents with scores
    retrieved = similarity_search_with_scores(
        query=question,
        collection_name=collection_name,
        k=config.TOP_K_RESULTS,
    )

    documents = [doc for doc, score in retrieved]
    retrieval_scores = [score for doc, score in retrieved]

    # Step 2: Format context and history
    context = format_context(documents)
    history_str = format_chat_history(chat_history)

    # Step 3: Build the prompt and generate answer
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(HUMAN_PROMPT),
    ])

    chain = prompt | llm
    response = await chain.ainvoke({
        "context": context,
        "chat_history": history_str,
        "question": question,
    })

    answer = response.content

    # Step 4: Evaluate confidence
    confidence = await evaluate_confidence(llm, context, question, answer)

    # Step 5: Determine if escalation is needed
    needs_escalation = confidence < config.CONFIDENCE_THRESHOLD

    # Step 6: Extract source citations
    sources = extract_sources(documents)

    return {
        "answer": answer,
        "confidence": round(confidence, 2),
        "needs_escalation": needs_escalation,
        "sources": sources,
        "retrieval_scores": [round(s, 4) for s in retrieval_scores],
    }
