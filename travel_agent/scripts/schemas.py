from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Literal

# todo: keep schema definitions here instead of in the agent files alone
class SignDetails(BaseModel):
    # Both are "Optional" in the type system, but the validator enforces presence
    western_sign: Optional[str] = Field(
        default=None,
        description="The Western Zodiac sign (e.g. Gemini, Leo). Null if user only provided Chinese."
    )

    western_decan: Optional[str] = Field(
        default=None,
        description="The specific decan (e.g. 'Decan 2') if mentioned. Null otherwise."
    )

    chinese_sign: Optional[str] = Field(
        default=None,
        description="The Chinese Zodiac animal (e.g. Monkey, Dragon). Null if user only provided Western."
    )

    # This validator runs AFTER the fields are populated to check your logic
    @model_validator(mode='after')
    def check_at_least_one_system(self):
        # Rule 1: User must have at least ONE of the two main signs
        if not self.western_sign and not self.chinese_sign:
            raise ValueError("You must identify either a Western Sign OR a Chinese Zodiac animal (or both).")

        # Rule 2 (Optional refinement): You can't have a decan without a western sign
        if self.western_decan and not self.western_sign:
            raise ValueError("Found a Decan but no Western Sign. Decans belong to Western astrology.")

        return self

# Sub-model for the travel specific data
class TravelPersona(BaseModel):
    vibe: str = Field(description="A short catchy title for their travel style")
    travel_style: str = Field(description="Adjectives describing their pace and preference")
    likes: List[str] = Field(description="List of 3-5 things they enjoy on trips")
    dislikes: Optional[List[str]] = Field(
        default_factory=list,
        description="List of things to avoid. Leave empty if none found."
    )

    ideal_destinations: Dict[str, str] = Field(
        min_length=5,
        description="A dictionary of at least 5 distinct recommendations. Key = City Name, Value = Country Name."
)

# The Main Response Model
class HoroscopeResponse(BaseModel):
    sign_details: SignDetails
    core_traits: List[str] = Field(description="List of personality traits based on the sign")
    travel_persona: TravelPersona
    marketing_hook: str = Field(description="A catchy one-sentence summary")