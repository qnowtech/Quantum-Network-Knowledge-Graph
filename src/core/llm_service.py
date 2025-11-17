"""
LLM Service for Problem Category Inference

This module provides a ReAct-based agent that infers problem categories
from contextual text using LangChain and structured outputs.

The agent uses a ReAct (Reasoning + Acting) pattern to analyze text and
classify it into one of the predefined problem categories for the knowledge graph.
"""

from typing import Optional, Dict, Any, List
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.core.logger import get_logger

_ = load_dotenv(find_dotenv())
logger = get_logger(__name__)


# ============================================================================
# GLOBAL PROBLEM CATEGORIES
# ============================================================================

PROBLEM_CATEGORIES = [
    "Falta de conocimiento general",
    "Falta de actualización",
    "Falta de networking",
    "Falta de información sobre aplicaciones",
    "Falta de información sobre madurez tecnológica",
    "Falta de información sobre viabilidad",
    "Falta de información sobre aplicaciones industriales",
    "Falta de oportunidades de colaboración",
    "Falta de información sobre demanda laboral",
    "Falta de información sobre productos",
    "Falta de ideas para implementación",
    "Gap entre negocio y tecnología",
    "SIN IDENTIFICAR PROBLEMA",  # Para casos donde no se puede inferir
]


# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# ============================================================================

class ProblemInference(BaseModel):
    """
    Structured output model for problem category inference.
    
    Uses ReAct pattern: Thought -> Action -> Observation -> Final Answer
    """
    thought: str = Field(
        description="El razonamiento inicial sobre qué tipo de problema podría estar presente en el texto"
    )
    action: str = Field(
        description="La acción de análisis que se está tomando para identificar el problema"
    )
    observation: str = Field(
        description="Lo que se observa en el texto que indica un problema específico"
    )
    problem_category: str = Field(
        description=f"La categoría de problema inferida. Debe ser exactamente una de: {', '.join(PROBLEM_CATEGORIES)}"
    )
    confidence: float = Field(
        description="Nivel de confianza en la inferencia (0.0 a 1.0)",
        ge=0.0,
        le=1.0
    )


# ============================================================================
# REACT PROMPT TEMPLATE
# ============================================================================

def create_react_prompt() -> ChatPromptTemplate:
    """
    Create a ReAct prompt template for problem category inference.
    
    The prompt guides the LLM through:
    1. Thought: Initial reasoning about the problem
    2. Action: What analysis to perform
    3. Observation: What evidence is found
    4. Final Answer: The problem category
    
    Returns:
        ChatPromptTemplate configured for ReAct pattern
    """
    
    system_prompt = """Eres un agente experto en análisis de necesidades y problemas en el contexto de computación cuántica.

Tu misión es analizar texto contextual y inferir la categoría de problema más apropiada que representa una necesidad o desafío relacionado con computación cuántica.

CONTEXTO DEL PROYECTO:
Este grafo de conocimiento tiene como máxima crear representaciones semánticas de valor asociadas a la computación cuántica. El objetivo es facilitar conexiones estratégicas entre investigadores y problemas empresariales, generar valor semántico para descubrir colaboraciones potenciales, y orientar conversaciones y estrategias en el ecosistema cuántico.

CATEGORÍAS DE PROBLEMAS DISPONIBLES:
{problem_categories}

INSTRUCCIONES PARA EL ANÁLISIS (Patrón ReAct):

1. THOUGHT (Pensamiento):
   - Analiza el texto contextual proporcionado
   - Identifica palabras clave, frases y conceptos relacionados con necesidades o problemas
   - Considera el contexto del ecosistema de computación cuántica
   - Piensa en qué tipo de problema o necesidad está expresando la persona

2. ACTION (Acción):
   - Especifica qué análisis estás realizando
   - Indica qué aspectos del texto estás examinando
   - Menciona qué categorías de problemas estás considerando

3. OBSERVATION (Observación):
   - Describe qué evidencia específica encontraste en el texto
   - Menciona las palabras clave o frases que indican el problema
   - Explica por qué este texto sugiere una categoría específica

4. PROBLEM_CATEGORY (Categoría Final):
   - Selecciona EXACTAMENTE UNA categoría de la lista proporcionada
   - Si el texto no contiene suficiente información para inferir un problema claro, usa "SIN IDENTIFICAR PROBLEMA"
   - La categoría debe ser exactamente como aparece en la lista (respetando mayúsculas, minúsculas y acentos)

5. CONFIDENCE (Confianza):
   - Asigna un valor entre 0.0 y 1.0
   - 1.0 = Muy seguro, evidencia clara y específica
   - 0.5-0.9 = Evidencia moderada pero clara
   - 0.0-0.4 = Poca evidencia, posiblemente "SIN IDENTIFICAR PROBLEMA"

IMPORTANTE:
- NO uses datos personales (nombres, emails, organizaciones específicas) en tu análisis
- Enfócate en el CONTENIDO y CONTEXTO de las necesidades expresadas
- Si el texto es muy genérico o no contiene información suficiente, usa "SIN IDENTIFICAR PROBLEMA"
- Sé preciso y específico en tu análisis
- Responde SOLO con un objeto JSON válido que contenga los campos: thought, action, observation, problem_category, confidence"""

    human_prompt = """Analiza el siguiente texto contextual y determina la categoría de problema más apropiada:

TEXTO CONTEXTUAL:
{contextual_text}

FORMATO DE RESPUESTA:
{format_instructions}

Aplica el patrón ReAct para realizar tu análisis y proporciona tu respuesta estructurada en el formato especificado."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt),
    ])
    
    return prompt


# ============================================================================
# LLM INITIALIZATION
# ============================================================================

def create_llm_agent() -> ChatOllama:
    """
    Create and configure the LLM agent for problem inference.
    
    Returns:
        Configured ChatOllama instance
    """
    llm = ChatOllama(
        model="llama3.2:3b",
        base_url="http://localhost:11434",
        temperature=0.0,  # Low temperature for consistent classification
    )
    
    return llm


# ============================================================================
# PROBLEM INFERENCE FUNCTION
# ============================================================================

def infer_problem_category(
    contextual_text: str,
    llm: Optional[ChatOllama] = None
) -> Dict[str, Any]:
    """
    Infer problem category from contextual text using ReAct pattern.
    
    This function uses a ReAct-based agent to analyze text and classify
    it into one of the predefined problem categories.
    
    Args:
        contextual_text: Text containing contextual information about
                        a person's needs/problems (without personal data)
        llm: Optional LLM instance (creates new one if not provided)
        
    Returns:
        Dictionary with:
        - problem_category: The inferred problem category
        - confidence: Confidence level (0.0 to 1.0)
        - thought: The reasoning process
        - action: The analysis action taken
        - observation: Evidence found in the text
        
    Example:
        >>> context = "Necesito entender mejor cómo aplicar computación cuántica en mi industria"
        >>> result = infer_problem_category(context)
        >>> print(result['problem_category'])
        "Falta de información sobre aplicaciones industriales"
    """
    if not contextual_text or contextual_text.strip() == "":
        logger.warning("Empty contextual text provided, returning SIN IDENTIFICAR PROBLEMA")
        return {
            "problem_category": "SIN IDENTIFICAR PROBLEMA",
            "confidence": 0.0,
            "thought": "No hay texto contextual para analizar",
            "action": "N/A",
            "observation": "Texto vacío",
        }
    
    # Initialize LLM if not provided
    if llm is None:
        llm = create_llm_agent()
    
    # Create prompt with problem categories
    prompt = create_react_prompt()
    formatted_prompt = prompt.partial(
        problem_categories="\n".join(f"- {cat}" for cat in PROBLEM_CATEGORIES)
    )
    
    # Create output parser
    parser = PydanticOutputParser(pydantic_object=ProblemInference)
    
    # Add format instructions to the prompt
    formatted_prompt_with_instructions = formatted_prompt.partial(
        format_instructions=parser.get_format_instructions()
    )
    
    # Create chain with format instructions
    chain = (
        {"contextual_text": RunnablePassthrough()}
        | formatted_prompt_with_instructions
        | llm
        | parser
    )
    
    try:
        # Execute inference
        result: ProblemInference = chain.invoke(contextual_text)
        
        # Validate that the category is in our list
        if result.problem_category not in PROBLEM_CATEGORIES:
            logger.warning(
                f"LLM returned invalid category '{result.problem_category}', "
                f"defaulting to 'SIN IDENTIFICAR PROBLEMA'"
            )
            result.problem_category = "SIN IDENTIFICAR PROBLEMA"
            result.confidence = 0.0
        
        logger.debug(
            f"Inferred problem category: {result.problem_category} "
            f"(confidence: {result.confidence:.2f})"
        )
        
        return {
            "problem_category": result.problem_category,
            "confidence": result.confidence,
            "thought": result.thought,
            "action": result.action,
            "observation": result.observation,
        }
        
    except Exception as e:
        logger.error(f"Error during problem inference: {e}", exc_info=True)
        return {
            "problem_category": "SIN IDENTIFICAR PROBLEMA",
            "confidence": 0.0,
            "thought": f"Error durante el análisis: {str(e)}",
            "action": "N/A",
            "observation": "Error en el procesamiento",
        }


# ============================================================================
# CONTEXT BUILDER FUNCTION
# ============================================================================

def build_contextual_text(
    event_expectations: Optional[str] = None,
    quantum_experience: Optional[str] = None,
    interests: Optional[List[str]] = None,
    industry_sector: Optional[str] = None,
    role: Optional[str] = None
) -> str:
    """
    Build contextual text from relevant information (excluding personal data).
    
    This function concatenates contextual information that helps infer problems,
    but excludes personal identifiers like name, email, organization name, etc.
    
    Args:
        event_expectations: What the person expects from the event
        quantum_experience: Level of quantum experience (active, exploration, etc.)
        interests: List of quantum computing interests
        industry_sector: Industry sector (general, not specific company)
        role: Professional role (general, not specific person)
        
    Returns:
        Concatenated contextual text ready for problem inference
        
    Example:
        >>> context = build_contextual_text(
        ...     event_expectations="Quiero aprender sobre aplicaciones",
        ...     quantum_experience="interested",
        ...     interests=["Finanzas", "Algoritmos"]
        ... )
    """
    context_parts = []
    
    # Add event expectations (most important for problem inference)
    if event_expectations and str(event_expectations).strip():
        context_parts.append(f"Expectativas del evento: {event_expectations.strip()}")
    
    # Add quantum experience context
    if quantum_experience:
        experience_map = {
            "active": "Tiene experiencia activa en proyectos cuánticos",
            "exploration": "Está en etapa de exploración o piloto",
            "academic": "Solo interés académico o general",
            "interested": "Interesado en iniciar",
            "industry_interest": "Interesado en aplicaciones industriales",
        }
        exp_text = experience_map.get(quantum_experience, f"Experiencia: {quantum_experience}")
        context_parts.append(exp_text)
    
    # Add interests context
    if interests and len(interests) > 0:
        interests_str = ", ".join([i.strip() for i in interests if i and str(i).strip()])
        if interests_str:
            context_parts.append(f"Áreas de interés: {interests_str}")
    
    # Add industry sector (general context, not specific company)
    if industry_sector and str(industry_sector).strip():
        context_parts.append(f"Sector industrial: {industry_sector.strip()}")
    
    # Add role context (general, not specific person)
    if role and str(role).strip():
        context_parts.append(f"Rol profesional: {role.strip()}")
    
    # Join all parts
    contextual_text = ". ".join(context_parts)
    
    return contextual_text if contextual_text else ""


# ============================================================================
# LEGACY FUNCTION FOR BACKWARD COMPATIBILITY
# ============================================================================

def data_enhancer() -> ChatOllama:
    """
    Legacy function for backward compatibility.
    
    Returns:
        ChatOllama instance
    """
    return create_llm_agent()


# Initialize default LLM instance
llm = create_llm_agent()
