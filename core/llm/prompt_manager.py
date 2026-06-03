"""
Prompt Manager for handling TOON (Token Optimized Object Notation) prompts.

This module provides functionality to load, cache, and combine TOON prompt templates
for different MCP roles with support for includes, caching, and hot-reloading.
"""
import os
import re
import time
from pathlib import Path
from typing import Dict, Optional, Set, List, Tuple
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Manages loading and resolving TOON prompt templates with advanced features:
    - Hot-reload support via file modification tracking
    - Optional includes with [INCLUDE:optional filename]
    - Efficient caching with automatic invalidation
    - Section-based prompt management
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the PromptManager with advanced caching and include support.
        
        Args:
            base_dir: Base directory containing TOON files. Defaults to 'config/toon/'
        """
        self.base_dir = Path(base_dir) if base_dir else Path("config") / "toon"
        self._prompt_cache: Dict[str, str] = {}
        self._cache_mtime: Dict[str, float] = {}
        self._include_pattern = re.compile(
            r'\[INCLUDE(?::\s*(optional))?\]\s*(\S+)', 
            re.IGNORECASE
        )
        self._section_pattern = re.compile(r'\[(\w+)\]')
        logger.info(f"Initialized PromptManager with base_dir: {self.base_dir}")
        
    def clear_cache(self) -> None:
        """Clear the prompt cache and modification times."""
        self._prompt_cache.clear()
        self._cache_mtime.clear()
        logger.debug("Prompt cache cleared")
    
    def get_prompt(self, role: str, extra_context: Optional[Dict[str, str]] = None) -> str:
        """
        Get the combined prompt for a specific role with template variables applied.
        
        Args:
            role: The role to get the prompt for (e.g., 'architect', 'developer')
            extra_context: Optional template variables for string formatting
            
        Returns:
            The fully resolved prompt string
            
        Raises:
            FileNotFoundError: If the role's TOON file doesn't exist
            KeyError: If a template variable is missing (only if extra_context is provided)
        """
        try:
            # Load and combine prompts
            global_prompt = self._load_toon_file("global_rules")
            role_prompt = self._load_toon_file(role)
            combined = f"{global_prompt}\n\n{role_prompt}"
            
            # Apply template variables if provided
            if extra_context:
                combined = combined.format(**extra_context)
                
            return combined
            
        except FileNotFoundError as e:
            logger.error(f"Failed to load prompt for role '{role}': {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing template variable in prompt: {e}")
            raise
    
    def _load_toon_file(self, name: str, seen: Optional[Set[str]] = None) -> str:
        """
        Load and process a TOON file with includes and caching.
        
        Args:
            name: Name of the TOON file (without extension)
            seen: Set of already included files to detect circular includes
            
        Returns:
            Processed content with all includes resolved
            
        Raises:
            FileNotFoundError: If the TOON file is required but not found
        """
        if seen is None:
            seen = set()

        file_path = self.base_dir / f"{name}.toon"
        if not file_path.exists():
            raise FileNotFoundError(f"TOON file not found: {file_path}")

        # Use file path as cache key
        cache_key = str(file_path)
        current_mtime = file_path.stat().st_mtime

        # Invalidate cache if file has been modified
        if cache_key in self._cache_mtime and self._cache_mtime[cache_key] < current_mtime:
            self._prompt_cache.pop(cache_key, None)
            logger.debug(f"Invalidated cache for {file_path}")

        # Return cached content if available
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]

        # Read and process the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        def process_include(match: re.Match) -> str:
            """Process a single include directive."""
            is_optional = bool(match.group(1))
            include_name = match.group(2).strip()

            if include_name in seen:
                logger.warning(f"Circular include detected: {include_name}")
                return ""

            seen.add(include_name)
            try:
                return self._load_toon_file(include_name, seen)
            except FileNotFoundError:
                if not is_optional:
                    logger.warning(f"Required include not found: {include_name}")
                return ""
            finally:
                seen.remove(include_name)

        # Process all includes
        content = self._include_pattern.sub(process_include, content)
        
        # Update cache
        self._prompt_cache[cache_key] = content
        self._cache_mtime[cache_key] = current_mtime
        
        return content
    
    def get_section(self, role: str, section: str, extra_context: Optional[Dict[str, str]] = None) -> str:
        """
        Get a specific section from a role's prompt.
        
        Args:
            role: The role to get the prompt for
            section: The section name (e.g., 'COMPORTAMIENTO')
            extra_context: Optional template variables
            
        Returns:
            The content of the specified section, or an empty string if not found
        """
        try:
            prompt = self.get_prompt(role, extra_context)
            sections = self._split_into_sections(prompt)
            return sections.get(section.upper(), "")
        except FileNotFoundError:
            logger.warning(f"Could not load prompt for role '{role}'")
            return ""
    
    def _split_into_sections(self, content: str) -> Dict[str, str]:
        """
        Split TOON content into sections, preserving empty lines within sections.
        
        Args:
            content: The raw TOON content
            
        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}
        current_section = "_GLOBAL"
        current_content = []
        
        for line in content.splitlines():
            line = line.rstrip()
            section_match = self._section_pattern.match(line.strip())
            if section_match:
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                    current_content = []
                current_section = section_match.group(1).upper()
            elif line or current_content:  # Preserve empty lines between content
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
            
        return sections
        
    def list_available_roles(self) -> List[str]:
        """
        List all available roles by scanning for .toon files.
        
        Returns:
            List of role names (filenames without .toon extension)
        """
        return [
            f.stem for f in self.base_dir.glob("*.toon") 
            if f.is_file() and f.stem != "global_rules"
        ]
