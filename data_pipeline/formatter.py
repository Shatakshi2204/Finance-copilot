"""
ChatML formatter for converting triangulated results into training samples.
"""

from .config import MetricType, ConfidenceLevel, TriangulatedResult, ChatMLMessage, ChatMLSample


class ChatMLFormatter:
    """Formats triangulated results into ChatML training samples."""

    SYSTEM_PROMPT = """You are a financial risk assistant specializing in macroeconomic analysis. \
You provide accurate, data-driven insights by cross-referencing multiple authoritative sources \
(FRED, World Bank, OECD). Always cite your sources and indicate confidence levels based on \
data agreement across sources."""

    METRIC_QUESTIONS = {
        MetricType.GDP_GROWTH: [
            "What is the current GDP growth rate for {country}?",
            "How is {country}'s economic growth performing?",
            "What's the GDP growth outlook for {country}?",
            "Tell me about {country}'s GDP growth.",
        ],
        MetricType.INFLATION: [
            "What is the inflation rate in {country}?",
            "What's the inflation risk for {country}?",
            "How high is inflation in {country}?",
            "Tell me about {country}'s inflation situation.",
        ],
        MetricType.UNEMPLOYMENT: [
            "What is the unemployment rate in {country}?",
            "How is the job market in {country}?",
            "What's the employment situation in {country}?",
            "Tell me about unemployment in {country}.",
        ],
        MetricType.INTEREST_RATE: [
            "What is the current interest rate in {country}?",
            "What are interest rates like in {country}?",
            "Tell me about {country}'s monetary policy rate.",
            "What's the policy rate in {country}?",
        ],
    }

    RISK_THRESHOLDS = {
        MetricType.GDP_GROWTH: {"low": 1.0, "moderate": 2.5, "high": 4.0},
        MetricType.INFLATION: {"low": 2.0, "moderate": 4.0, "high": 6.0},
        MetricType.UNEMPLOYMENT: {"low": 4.0, "moderate": 6.0, "high": 8.0},
        MetricType.INTEREST_RATE: {"low": 2.0, "moderate": 4.0, "high": 6.0},
    }

    def _assess_risk_level(self, metric: MetricType, value: float) -> str:
        """Assess risk level based on metric value."""
        if value is None:
            return "undetermined"

        thresholds = self.RISK_THRESHOLDS.get(metric, {})

        if metric == MetricType.GDP_GROWTH:
            # Lower GDP growth = higher risk
            if value >= thresholds.get("high", 4.0):
                return "low"
            elif value >= thresholds.get("moderate", 2.5):
                return "moderate"
            elif value >= thresholds.get("low", 1.0):
                return "elevated"
            else:
                return "high"
        else:
            # Higher values = higher risk for inflation, unemployment, interest rates
            if value <= thresholds.get("low", 2.0):
                return "low"
            elif value <= thresholds.get("moderate", 4.0):
                return "moderate"
            elif value <= thresholds.get("high", 6.0):
                return "elevated"
            else:
                return "high"

    def _generate_assistant_response(self, result: TriangulatedResult, metric: MetricType) -> str:
        """Generate a detailed assistant response based on triangulated data."""
        risk_level = self._assess_risk_level(metric, result.consensus_value)

        # Build source citations
        citations = []
        if result.fred_value is not None:
            citations.append(f"FRED ({result.fred_value:.2f}%)")
        if result.worldbank_value is not None:
            citations.append(f"World Bank ({result.worldbank_value:.2f}%)")
        if result.oecd_value is not None:
            citations.append(f"OECD ({result.oecd_value:.2f}%)")

        sources_text = ", ".join(citations) if citations else "no available sources"

        # Confidence explanation
        confidence_text = {
            ConfidenceLevel.HIGH: "high confidence (all sources agree)",
            ConfidenceLevel.MEDIUM: "medium confidence (majority of sources agree)",
            ConfidenceLevel.LOW: "low confidence (sources disagree significantly)",
            ConfidenceLevel.SINGLE_SOURCE: "limited confidence (single source only)",
            ConfidenceLevel.NO_DATA: "no confidence (no data available)",
        }.get(result.confidence, "unknown confidence")

        # Build response
        if result.consensus_value is not None:
            response = (
                f"Based on {sources_text}, {result.country}'s {result.metric.replace('_', ' ')} "
                f"is approximately {result.consensus_value:.2f}% (as of {result.period}).\n\n"
                f"**Confidence Level:** {confidence_text.capitalize()}\n"
                f"**Risk Assessment:** {risk_level.capitalize()} risk\n\n"
                f"**Analysis:** {result.explanation}"
            )

            # Add contextual insights based on metric
            if metric == MetricType.GDP_GROWTH:
                if result.consensus_value < 1.0:
                    response += (
                        "\n\n**Implication:** Weak growth suggests potential recession risk. "
                        "Consider defensive positioning in portfolios."
                    )
                elif result.consensus_value > 3.0:
                    response += (
                        "\n\n**Implication:** Strong growth may lead to inflationary pressures "
                        "and potential monetary tightening."
                    )
            elif metric == MetricType.INFLATION:
                if result.consensus_value > 4.0:
                    response += (
                        "\n\n**Implication:** Elevated inflation erodes purchasing power and may "
                        "prompt central bank rate hikes. Duration exposure should be monitored."
                    )
        else:
            response = (
                f"Unable to provide a reliable estimate for {result.country}'s "
                f"{result.metric.replace('_', ' ')}. {result.explanation}"
            )

        return response

    def format_sample(
        self,
        result: TriangulatedResult,
        metric: MetricType,
        question_variant: int = 0
    ) -> ChatMLSample:
        """
        Format a triangulated result into a ChatML training sample.
        
        Args:
            result: The triangulated data result
            metric: The metric type (for question selection)
            question_variant: Index of question variant to use
            
        Returns:
            ChatMLSample ready for .jsonl export
        """
        questions = self.METRIC_QUESTIONS.get(metric, [f"What is the {metric.value} for {{country}}?"])
        question_idx = question_variant % len(questions)
        question = questions[question_idx].format(country=result.country)

        assistant_response = self._generate_assistant_response(result, metric)

        return ChatMLSample(
            messages=[
                ChatMLMessage(role="system", content=self.SYSTEM_PROMPT),
                ChatMLMessage(role="user", content=question),
                ChatMLMessage(role="assistant", content=assistant_response),
            ]
        )

    def format_multi_turn(
        self,
        results: list[TriangulatedResult],
        metrics: list[MetricType]
    ) -> ChatMLSample:
        """
        Format multiple results into a multi-turn conversation sample.
        
        Useful for training the model on follow-up questions.
        """
        messages = [ChatMLMessage(role="system", content=self.SYSTEM_PROMPT)]

        for result, metric in zip(results, metrics):
            questions = self.METRIC_QUESTIONS.get(metric, [f"What is the {metric.value} for {{country}}?"])
            question = questions[0].format(country=result.country)
            response = self._generate_assistant_response(result, metric)

            messages.append(ChatMLMessage(role="user", content=question))
            messages.append(ChatMLMessage(role="assistant", content=response))

        return ChatMLSample(messages=messages)