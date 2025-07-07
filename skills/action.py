"""
Action class for intelligent browser action handling.

This module defines the Action class that provides structured action handling
with fallback selectors and vision-based error recovery.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Action(BaseModel):
    """
    Represents a browser action with intelligent fallback mechanisms.
    
    This class encapsulates browser actions with primary and fallback selectors,
    enabling robust action execution with automatic error recovery.
    """
    
    action_type: str = Field(
        ..., 
        description="The type of action (e.g., 'click', 'type', 'navigate')"
    )
    
    selector: Optional[str] = Field(
        None, 
        description="The primary CSS selector to try."
    )
    
    fallback_selectors: List[str] = Field(
        default_factory=list, 
        description="Alternative selectors to try upon failure."
    )
    
    description: str = Field(
        ..., 
        description="A natural language description of the element (e.g., 'the main login button')."
    )
    
    text_to_type: Optional[str] = Field(
        None, 
        description="Text to type for 'type' actions."
    )
    
    url: Optional[str] = Field(
        None, 
        description="URL for 'navigate' actions."
    )
    
    coordinates: Optional[List[int]] = Field(
        None,
        description="Coordinates [x, y] for coordinate-based actions."
    )
    
    def get_all_selectors(self) -> List[str]:
        """
        Get all selectors (primary + fallbacks) for this action.
        
        Returns:
            List[str]: All available selectors to try
        """
        selectors = []
        if self.selector:
            selectors.append(self.selector)
        selectors.extend(self.fallback_selectors)
        return selectors
    
    def add_fallback_selector(self, selector: str) -> None:
        """
        Add a fallback selector to the action.
        
        Args:
            selector (str): The selector to add as fallback
        """
        if selector not in self.fallback_selectors:
            self.fallback_selectors.append(selector)
    
    def set_primary_selector(self, selector: str) -> None:
        """
        Set the primary selector for this action.
        
        Args:
            selector (str): The primary selector to use
        """
        self.selector = selector
    
    @classmethod
    def create_click_action(
        cls,
        description: str,
        selector: Optional[str] = None,
        fallback_selectors: Optional[List[str]] = None,
        coordinates: Optional[List[int]] = None
    ) -> 'Action':
        """
        Create a click action.
        
        Args:
            description (str): Natural language description of the element
            selector (str, optional): Primary CSS selector
            fallback_selectors (List[str], optional): Fallback selectors
            coordinates (List[int], optional): Coordinates [x, y] for coordinate-based clicking
            
        Returns:
            Action: A configured click action
        """
        return cls(
            action_type="click",
            description=description,
            selector=selector,
            fallback_selectors=fallback_selectors or [],
            coordinates=coordinates
        )
    
    @classmethod
    def create_type_action(
        cls,
        description: str,
        text_to_type: str,
        selector: Optional[str] = None,
        fallback_selectors: Optional[List[str]] = None
    ) -> 'Action':
        """
        Create a type action.
        
        Args:
            description (str): Natural language description of the element
            text_to_type (str): Text to type into the element
            selector (str, optional): Primary CSS selector
            fallback_selectors (List[str], optional): Fallback selectors
            
        Returns:
            Action: A configured type action
        """
        return cls(
            action_type="type",
            description=description,
            text_to_type=text_to_type,
            selector=selector,
            fallback_selectors=fallback_selectors or []
        )
    
    @classmethod
    def create_navigate_action(
        cls,
        url: str,
        description: Optional[str] = None
    ) -> 'Action':
        """
        Create a navigate action.
        
        Args:
            url (str): URL to navigate to
            description (str, optional): Description of the navigation
            
        Returns:
            Action: A configured navigate action
        """
        return cls(
            action_type="navigate",
            description=description or f"Navigate to {url}",
            url=url
        )
    
    def __str__(self) -> str:
        """String representation of the action."""
        if self.action_type == "click":
            return f"Click: {self.description}"
        elif self.action_type == "type":
            return f"Type '{self.text_to_type}' into: {self.description}"
        elif self.action_type == "navigate":
            return f"Navigate to: {self.url}"
        else:
            return f"{self.action_type}: {self.description}" 