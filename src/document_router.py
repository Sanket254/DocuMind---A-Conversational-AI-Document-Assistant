import json


class DocumentRouter:
    """
    Uses the LLM to decide whether retrieval should be restricted
    to specific uploaded documents.
    """

    def __init__(self, llm):
        self.llm = llm

    def route(self, question: str, available_files: list[str]):
        if not available_files:
            return None

        prompt = f"""
            You are a document routing assistant.

            The user has uploaded these documents:

            {json.dumps(available_files, indent=2)}

            User question:
            "{question}"

            Your job:

            - Decide whether the question clearly refers to one or more specific uploaded documents.
            - If yes, return ONLY a JSON array containing the matching filenames exactly as written.
            - If the question is general or could require searching every document, return null.
            - Never invent filenames.
            - Never explain your reasoning.

            Examples:

            Question:
            "What does my resume say?"
            Output:
            ["Resume.pdf"]

            Question:
            "Summarize the AI paper."
            Output:
            ["AI Paper.pdf"]

            Question:
            "What is my CGPA?"
            Output:
            null

            Question:
            "Compare my resume and transcript."
            Output:
            ["Resume.pdf", "Transcript.pdf"]

            Examples:

            Uploaded files:
            [
            "AnnualReport.pdf",
            "PhysicsNotes.pdf",
            "MeetingMinutes.pdf",
            "UserManual.pdf"
            ]

            Question:
            "What does the annual report say about revenue?"

            Output:
            ["AnnualReport.pdf"]


            Question:
            "Summarize chapter 4."

            Output:
            ["PhysicsNotes.pdf"]


            Question:
            "What was decided in the meeting?"

            Output:
            ["MeetingMinutes.pdf"]


            Question:
            "Compare the report and the meeting notes."

            Output:
            ["AnnualReport.pdf", "MeetingMinutes.pdf"]


            Question:
            "Explain this topic."

            Output:
            null

            Return ONLY valid JSON.
            """

        response = self.llm.invoke(prompt).content.strip()

        try:
            parsed = json.loads(response)

            if parsed is None:
                return None

            if isinstance(parsed, list):
                valid = [f for f in parsed if f in available_files]

                if valid:
                    return valid

            return None

        except Exception:
            return None