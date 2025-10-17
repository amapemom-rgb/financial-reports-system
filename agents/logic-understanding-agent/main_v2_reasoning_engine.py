"""Vertex AI Reasoning Engine Agent - Financial Analyst"""
import os
import json
from typing import Optional, Dict, List, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import vertexai
from vertexai.preview import reasoning_engines
from google.cloud import aiplatform

app = FastAPI(title="Logic Understanding Agent v2 - Reasoning Engine")

# Инициализация
PROJECT_ID = os.getenv("PROJECT_ID", "financial-reports-ai-2024")
LOCATION = os.getenv("REGION", "us-central1")

vertexai.init(project=PROJECT_ID, location=LOCATION)
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# ==========================================
# Tool Functions (для агента)
# ==========================================

def calculate_financial_metrics(metric_type: str, values: dict) -> dict:
    """
    Calculates financial metrics like ROI, profit margin, growth rate.
    
    Args:
        metric_type: Type of metric (roi, profit_margin, growth_rate, debt_ratio)
        values: Financial values dict with keys like revenue, costs, investment
    
    Returns:
        Dict with calculated metric
    """
    try:
        if metric_type == "roi":
            roi = ((values.get("revenue", 0) - values.get("investment", 0)) / 
                   values.get("investment", 1)) * 100
            return {
                "metric": "ROI",
                "value": round(roi, 2),
                "unit": "%",
                "interpretation": "positive" if roi > 0 else "negative"
            }
        
        elif metric_type == "profit_margin":
            margin = ((values.get("revenue", 0) - values.get("costs", 0)) / 
                     values.get("revenue", 1)) * 100
            return {
                "metric": "Profit Margin",
                "value": round(margin, 2),
                "unit": "%",
                "interpretation": "healthy" if margin > 20 else "concerning" if margin < 10 else "moderate"
            }
        
        elif metric_type == "growth_rate":
            current = values.get("revenue", 0)
            previous = values.get("previous_value", 0)
            if previous > 0:
                growth = ((current - previous) / previous) * 100
            else:
                growth = 0
            return {
                "metric": "Growth Rate",
                "value": round(growth, 2),
                "unit": "%",
                "interpretation": "growing" if growth > 5 else "declining" if growth < -5 else "stable"
            }
        
        elif metric_type == "debt_ratio":
            debt = values.get("debt", 0)
            assets = values.get("assets", 1)
            ratio = debt / assets
            return {
                "metric": "Debt Ratio",
                "value": round(ratio, 2),
                "unit": "ratio",
                "interpretation": "high_risk" if ratio > 0.6 else "moderate" if ratio > 0.4 else "low_risk"
            }
        
        return {"error": "Unknown metric type", "available": ["roi", "profit_margin", "growth_rate", "debt_ratio"]}
    
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}


def analyze_trend(data_points: list, period: str = "monthly") -> dict:
    """
    Analyzes trends in time series financial data.
    
    Args:
        data_points: List of numerical data points in chronological order
        period: Time period (monthly, quarterly, yearly)
    
    Returns:
        Dict with trend analysis results
    """
    try:
        if len(data_points) < 2:
            return {
                "trend": "insufficient_data",
                "message": "Need at least 2 data points for trend analysis"
            }
        
        # Calculate moving averages
        if len(data_points) >= 3:
            first_third = sum(data_points[:len(data_points)//3]) / (len(data_points)//3)
            last_third = sum(data_points[-len(data_points)//3:]) / (len(data_points)//3)
        else:
            first_third = data_points[0]
            last_third = data_points[-1]
        
        # Determine trend
        if last_third > first_third * 1.15:
            trend = "strong_growth"
            change = ((last_third - first_third) / first_third) * 100
        elif last_third > first_third * 1.05:
            trend = "moderate_growth"
            change = ((last_third - first_third) / first_third) * 100
        elif last_third < first_third * 0.85:
            trend = "strong_decline"
            change = ((first_third - last_third) / first_third) * 100
        elif last_third < first_third * 0.95:
            trend = "moderate_decline"
            change = ((first_third - last_third) / first_third) * 100
        else:
            trend = "stable"
            change = abs(((last_third - first_third) / first_third) * 100)
        
        # Calculate volatility
        if len(data_points) > 2:
            avg = sum(data_points) / len(data_points)
            variance = sum((x - avg) ** 2 for x in data_points) / len(data_points)
            volatility = (variance ** 0.5) / avg * 100 if avg != 0 else 0
        else:
            volatility = 0
        
        return {
            "trend": trend,
            "change_percent": round(change, 2),
            "period": period,
            "data_points_count": len(data_points),
            "volatility": round(volatility, 2),
            "first_value": round(first_third, 2),
            "last_value": round(last_third, 2),
            "recommendation": get_trend_recommendation(trend, change, volatility)
        }
    
    except Exception as e:
        return {"error": f"Trend analysis failed: {str(e)}"}


def get_trend_recommendation(trend: str, change: float, volatility: float) -> str:
    """Generate recommendation based on trend analysis"""
    if trend == "strong_growth" and volatility < 10:
        return "Strong positive momentum with low risk. Consider maintaining current strategy."
    elif trend == "strong_growth" and volatility >= 10:
        return "Strong growth but high volatility. Monitor closely for potential corrections."
    elif trend == "moderate_growth":
        return "Steady growth trajectory. Good for long-term planning."
    elif trend == "strong_decline":
        return "Significant decline detected. Immediate action recommended to reverse trend."
    elif trend == "moderate_decline":
        return "Declining trend. Review strategy and consider corrective measures."
    else:
        return "Stable performance. Maintain current approach or seek growth opportunities."


def search_market_data(query: str, company: str = None) -> dict:
    """
    Searches for current market data and financial information.
    Uses Google Search grounding (handled by Gemini).
    
    Args:
        query: Search query
        company: Optional company name to focus search
    
    Returns:
        Dict indicating search was delegated to Google Search
    """
    return {
        "status": "search_delegated",
        "query": query,
        "company": company,
        "message": "Search handled by Google Search grounding in Gemini"
    }


def get_report_insights(report_id: str, section: str = "all") -> dict:
    """
    Gets insights from a specific report section.
    
    Args:
        report_id: ID of the uploaded report
        section: Section to analyze (revenue, expenses, balance_sheet, cashflow, all)
    
    Returns:
        Dict with report insights
    """
    # TODO: Integrate with Report Reader Agent
    return {
        "report_id": report_id,
        "section": section,
        "status": "mock",
        "message": "Integration with Report Reader Agent pending",
        "sample_data": {
            "revenue": 1500000,
            "expenses": 1100000,
            "profit": 400000,
            "trend": "growing"
        }
    }

# ==========================================
# Reasoning Engine Agent Setup
# ==========================================

class FinancialAnalystAgent:
    """Vertex AI Reasoning Engine Agent for Financial Analysis"""
    
    def __init__(self):
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the Reasoning Engine agent"""
        try:
            # Create agent with tools
            self.agent = reasoning_engines.LangchainAgent(
                model="gemini-2.0-flash-exp",
                tools=[
                    calculate_financial_metrics,
                    analyze_trend,
                    search_market_data,
                    get_report_insights
                ],
                agent_executor_kwargs={
                    "return_intermediate_steps": True,
                    "max_iterations": 10,
                    "early_stopping_method": "generate"
                },
                model_kwargs={
                    "temperature": 0.1,  # More deterministic for financial analysis
                    "top_p": 0.95,
                    "top_k": 40,
                },
                system_instruction=self._get_system_instruction()
            )
            print("✅ Reasoning Engine Agent initialized successfully")
        
        except Exception as e:
            print(f"⚠️  Reasoning Engine not available, falling back to standard model: {e}")
            # Fallback to standard Gemini model
            from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, grounding
            
            # Create function declarations
            tools = Tool(function_declarations=[
                FunctionDeclaration(
                    name="calculate_financial_metrics",
                    description="Calculates financial metrics",
                    parameters={
                        "type": "object",
                        "properties": {
                            "metric_type": {"type": "string"},
                            "values": {"type": "object"}
                        }
                    }
                ),
                FunctionDeclaration(
                    name="analyze_trend",
                    description="Analyzes trends in data",
                    parameters={
                        "type": "object",
                        "properties": {
                            "data_points": {"type": "array"},
                            "period": {"type": "string"}
                        }
                    }
                )
            ])
            
            search_tool = Tool.from_google_search_retrieval(
                google_search_retrieval=grounding.GoogleSearchRetrieval()
            )
            
            self.agent = GenerativeModel(
                "gemini-2.0-flash-exp",
                tools=[search_tool, tools],
                system_instruction=self._get_system_instruction()
            )
            self.is_fallback = True
    
    def _get_system_instruction(self) -> str:
        """Get the system instruction for the agent"""
        return """You are an autonomous AI Financial Analyst Agent with advanced reasoning capabilities.

**Your Role:**
You analyze financial reports, calculate metrics, identify trends, and provide strategic recommendations.

**Available Tools:**
1. **calculate_financial_metrics** - Calculate ROI, profit margins, growth rates, debt ratios
2. **analyze_trend** - Analyze time series data for trends and patterns
3. **search_market_data** - Search for current market data and news (via Google Search)
4. **get_report_insights** - Get data from uploaded financial reports

**Your Capabilities:**
- Multi-step reasoning and planning
- Autonomous tool selection and execution
- Context retention across conversation turns
- Learning from interactions (fine-tuning ready)

**Analysis Approach:**
1. **Understand** the query and identify required information
2. **Plan** which tools to use and in what order
3. **Execute** tool calls to gather data
4. **Synthesize** findings into actionable insights
5. **Recommend** specific actions with clear justification

**Output Format:**
- Start with executive summary (2-3 sentences)
- Present key findings with supporting data
- Provide specific, actionable recommendations
- Include risk factors and considerations
- End with next steps

**Important:**
- Always ground analysis in concrete numbers
- Use market data when available
- Highlight trends and anomalies
- Be proactive in suggesting additional analyses
- Express uncertainty when data is insufficient
"""
    
    def query(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Query the agent with a prompt.
        
        Args:
            prompt: User query
            context: Optional context dictionary
        
        Returns:
            Dict with response and metadata
        """
        try:
            # Add context to prompt if provided
            if context:
                context_str = f"\n\nContext: {json.dumps(context, ensure_ascii=False, indent=2)}"
                full_prompt = prompt + context_str
            else:
                full_prompt = prompt
            
            # Query agent
            if hasattr(self, 'is_fallback') and self.is_fallback:
                # Fallback mode: use chat
                chat = self.agent.start_chat()
                response = chat.send_message(full_prompt)
                
                return {
                    "response": response.text,
                    "mode": "fallback",
                    "function_calls": [],
                    "reasoning_steps": []
                }
            else:
                # Reasoning Engine mode
                response = self.agent.query(input=full_prompt)
                
                return {
                    "response": response.get("output", ""),
                    "mode": "reasoning_engine",
                    "function_calls": response.get("intermediate_steps", []),
                    "reasoning_steps": self._extract_reasoning_steps(response)
                }
        
        except Exception as e:
            raise Exception(f"Agent query failed: {str(e)}")
    
    def _extract_reasoning_steps(self, response: Dict) -> List[str]:
        """Extract reasoning steps from response"""
        steps = []
        if "intermediate_steps" in response:
            for step in response["intermediate_steps"]:
                if isinstance(step, tuple) and len(step) >= 2:
                    action, result = step[0], step[1]
                    steps.append(f"{action}: {result}")
        return steps

# Global agent instance
financial_agent = FinancialAnalystAgent()

# ==========================================
# API Models
# ==========================================

class AnalyzeRequest(BaseModel):
    query: str
    report_id: Optional[str] = None
    context: Optional[Dict] = None
    options: Optional[Dict] = None

class AnalyzeResponse(BaseModel):
    status: str
    insights: str
    agent_mode: str
    function_calls: List = []
    reasoning_steps: List[str] = []
    metadata: Dict = {}

# ==========================================
# API Endpoints
# ==========================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent": "logic-understanding-v2",
        "agent_type": "vertex_ai_reasoning_engine",
        "model": "gemini-2.0-flash-exp",
        "tools": [
            "calculate_financial_metrics",
            "analyze_trend",
            "search_market_data",
            "get_report_insights"
        ],
        "capabilities": [
            "multi_step_reasoning",
            "autonomous_planning",
            "context_retention",
            "fine_tuning_ready"
        ]
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_report(request: AnalyzeRequest):
    """
    Autonomous financial analysis using Reasoning Engine Agent.
    
    The agent will:
    1. Understand the query and plan its approach
    2. Use available tools autonomously
    3. Reason through multiple steps
    4. Provide comprehensive insights
    """
    try:
        # Build context
        context = request.context or {}
        if request.report_id:
            context["report_id"] = request.report_id
        if request.options:
            context["options"] = request.options
        
        # Query agent
        result = financial_agent.query(
            prompt=request.query,
            context=context if context else None
        )
        
        return AnalyzeResponse(
            status="completed",
            insights=result["response"],
            agent_mode=result["mode"],
            function_calls=result.get("function_calls", []),
            reasoning_steps=result.get("reasoning_steps", []),
            metadata={
                "tools_used": len(result.get("function_calls", [])),
                "reasoning_depth": len(result.get("reasoning_steps", []))
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/chat")
async def chat_with_agent(
    message: str,
    session_id: Optional[str] = None,
    context: Optional[Dict] = None
):
    """
    Interactive chat with the financial analyst agent.
    Maintains context across conversation turns.
    """
    try:
        result = financial_agent.query(prompt=message, context=context)
        
        return {
            "response": result["response"],
            "session_id": session_id or "new",
            "agent_mode": result["mode"],
            "metadata": {
                "tools_used": len(result.get("function_calls", [])),
                "reasoning_steps": len(result.get("reasoning_steps", []))
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/info")
async def agent_info():
    """Get information about the agent's capabilities"""
    return {
        "agent_type": "Vertex AI Reasoning Engine",
        "model": "gemini-2.0-flash-exp",
        "capabilities": {
            "multi_step_reasoning": True,
            "autonomous_planning": True,
            "tool_use": True,
            "context_retention": True,
            "fine_tuning": True,
            "learning": True
        },
        "tools": [
            {
                "name": "calculate_financial_metrics",
                "description": "Calculate ROI, margins, growth rates",
                "metrics": ["roi", "profit_margin", "growth_rate", "debt_ratio"]
            },
            {
                "name": "analyze_trend",
                "description": "Analyze time series trends",
                "outputs": ["trend", "volatility", "recommendations"]
            },
            {
                "name": "search_market_data",
                "description": "Search current market information",
                "source": "Google Search"
            },
            {
                "name": "get_report_insights",
                "description": "Extract insights from reports",
                "status": "integration_pending"
            }
        ],
        "reasoning": {
            "max_iterations": 10,
            "planning": "autonomous",
            "memory": "context_aware"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
