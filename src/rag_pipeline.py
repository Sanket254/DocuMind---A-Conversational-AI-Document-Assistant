from typing import Dict, Any


class RAGPipeline:
    """
    Complete RAG Pipeline

    Features
    --------
    ✔ Retrieval
    ✔ Streaming
    ✔ Citations
    ✔ Conversation History
    ✔ Summarization
    ✔ Context Return
    """

    def __init__(self, llm, document_router, vector_store, hybrid_search,):
        self.llm = llm
        self.document_router = document_router
        self.vector_store = vector_store
        self.hybrid_search = hybrid_search

    def rewrite_query(self, question, history_text):
        """
        Rewrite the user's question into a better search query
        for vector retrieval.
        """

        prompt = f"""
        You are helping a Retrieval-Augmented Generation (RAG) system.

        Your job is NOT to answer the question.

        Your ONLY job is to rewrite the user's latest question into
        the best possible semantic search query.

        Rules:

        - Preserve the user's intent.
        - Use conversation history only to resolve ambiguous references.
        - Expand pronouns and vague references (such as "it", "they", "that", "this", "he", "she", "those") using previous conversation.
        - Include important names, places, products, documents, or topics mentioned earlier when necessary.
        - Do not invent information.
        - Keep the rewritten query concise.
        - Return ONLY the rewritten search query.
        - Do not answer the user's question.
        - Do not explain your reasoning.

        Conversation History:
        {history_text}

        Current Question:
        {question}

        Search Query:
        """

        return self.llm.invoke(prompt).content.strip()

    def ask(
        self,
        question,
        history=None,
        top_k=5,
        distance_threshold=0.75,
        stream=False,
        summarize=False,
        return_context=False,
    ):

        #################################
        # Retrieval
        #################################
        history_text = ""
        
        if history:
            history_text = "\n".join(
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in history
            )
        search_query = self.rewrite_query(
            question,
            history_text
        )

        print(f"\nSearch Query: {search_query}\n")

        available_files = self.vector_store.get_uploaded_files()

        allowed_files = self.document_router.route(
            question=question,
            available_files=available_files,
        )

        if allowed_files:
            print(f"Document Router selected: {allowed_files}")
        else:
            print("Document Router selected: ALL DOCUMENTS")

        results = self.hybrid_search.search(
            query=search_query,
            top_k=top_k,
            allowed_files=allowed_files,
        )

        if results:
            context = "\n\n".join(
                doc["content"] for doc in results
            )
        else:
            context = "No document context available."


        #################################
        # Context
        #################################


        history_text = ""

        if history:
            history_text = "\n".join(
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in history
            )

        #################################
        # Prompt
        #################################

        prompt = f"""
            You are an AI assistant.

            You have access to two sources of information:

            1. Conversation History:
            Previous messages between you and the user.

            2. Document Context:
            Information retrieved from uploaded documents.

            Rules:

            - Prefer document context over conversation history for factual information.
            - Use conversation history only for maintaining context and previous discussion flow.
            - If document context and conversation history conflict, trust document context.
            - Never mention internal sources or retrieval.
            - Answer directly.

            Conversation History:
            {history_text}


            Document Context:
            {context}


            Current Question:
            {question}


            Answer:
            """

        #################################
        # LLM
        #################################

        if stream:
            print("\nStreaming Response:\n")
            answer = ""

            for chunk in self.llm.stream(prompt):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                    answer += chunk.content
            print()

        else:
            answer = self.llm.invoke(prompt).content

        #################################
        # Sources
        #################################

        sources = []

        for doc in results:
            sources.append(
                {
                    "source": doc["file_name"],
                    "page": doc["page"],    
                    "preview": doc["content"][:150] + "...",
                }
            )

        citations = "\n".join(
            [
                f"[{i+1}] {s['source']} (page {s['page']})"
                for i, s in enumerate(sources)
            ]
        )

        if sources:
            final_answer = answer + "\n\nSources:\n" + citations
        else:
            final_answer = answer

        #################################
        # Summary
        #################################

        summary = None

        if summarize:
            summary_prompt = f"""
                Summarize the following answer in two sentences.
                {answer}
                """
            summary = self.llm.invoke(summary_prompt).content

        #################################
        # History
        #################################

        #################################
        # Output
        #################################

        output = {
            "question": question,
            "answer": final_answer,
            "sources": sources,
            "summary": summary,
        }

        if return_context:
            output["context"] = context

        return output
