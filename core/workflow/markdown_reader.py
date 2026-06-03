"""
Markdown Reader - Lee y parsea archivos markdown con requerimientos
Extrae secciones, tareas y especificaciones estructuradas
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import structlog

logger = structlog.get_logger()


class MarkdownRequirement:
    """Representa un requerimiento extraído del markdown"""
    def __init__(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        tags: List[str] = None,
        acceptance_criteria: List[str] = None
    ):
        self.title = title
        self.description = description
        self.priority = priority
        self.tags = tags or []
        self.acceptance_criteria = acceptance_criteria or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "tags": self.tags,
            "acceptance_criteria": self.acceptance_criteria
        }


class MarkdownReader:
    """
    Lee archivos markdown y extrae información estructurada
    
   Soporta:
    - Headers (H1-H6) como secciones
    - Listas como tareas
    - Code blocks como especificaciones técnicas
    - Metadata en YAML frontmatter
    - Tags y prioridades
    """
    
    def __init__(self):
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.list_pattern = re.compile(r'^\s*[-*+]\s+(.+)$', re.MULTILINE)
        self.checkbox_pattern = re.compile(r'^\s*[-*+]\s+\[([ xX])\]\s+(.+)$', re.MULTILINE)
        self.code_block_pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
        self.priority_pattern = re.compile(r'\[(!{1,3}|priority:\s*(high|medium|low))\]', re.IGNORECASE)
        self.tag_pattern = re.compile(r'#(\w+)')
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Lee un archivo markdown y retorna estructura parseada
        
        Returns:
            {
                "metadata": {...},
                "sections": [...],
                "requirements": [...],
                "tasks": [...],
                "code_blocks": [...]
            }
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        
        logger.info("markdown_file_read", file_path=file_path, size=len(content))
        
        return {
            "metadata": self._extract_metadata(content),
            "sections": self._extract_sections(content),
            "requirements": self._extract_requirements(content),
            "tasks": self._extract_tasks(content),
            "code_blocks": self._extract_code_blocks(content),
            "raw_content": content
        }
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extrae YAML frontmatter si existe"""
        frontmatter_pattern = re.compile(r'^---\n(.*?)\n---', re.DOTALL)
        match = frontmatter_pattern.match(content)
        
        if not match:
            return {}
        
        # Parsing simple de YAML (key: value)
        metadata = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extrae secciones basadas en headers"""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            header_match = self.header_pattern.match(line)
            if header_match:
                # Guardar sección anterior
                if current_section:
                    current_section['content'] = '\n'.join(current_content).strip()
                    sections.append(current_section)
                
                # Nueva sección
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = {
                    "level": level,
                    "title": title,
                    "content": ""
                }
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Guardar última sección
        if current_section:
            current_section['content'] = '\n'.join(current_content).strip()
            sections.append(current_section)
        
        return sections
    
    def _extract_requirements(self, content: str) -> List[MarkdownRequirement]:
        """Extrae requerimientos de formato estructurado"""
        requirements = []
        sections = self._extract_sections(content)
        
        for section in sections:
            # Buscar secciones que sean requerimientos
            title_lower = section['title'].lower()
            if any(keyword in title_lower for keyword in ['requerimiento', 'requirement', 'feature', 'funcionalidad']):
                
                # Extraer prioridad del título o contenido
                priority = self._extract_priority(section['title'] + section['content'])
                
                # Extraer tags
                tags = self.tag_pattern.findall(section['content'])
                
                # Extraer criterios de aceptación (listas bajo "Criterios" o "Acceptance")
                acceptance_criteria = []
                criteria_section = re.search(
                    r'(?:criterios?|acceptance).*?\n(.*?)(?=\n#|\Z)',
                    section['content'],
                    re.IGNORECASE | re.DOTALL
                )
                if criteria_section:
                    acceptance_criteria = self.list_pattern.findall(criteria_section.group(1))
                
                req = MarkdownRequirement(
                    title=section['title'],
                    description=section['content'],
                    priority=priority,
                    tags=tags,
                    acceptance_criteria=acceptance_criteria
                )
                requirements.append(req)
        
        return requirements
    
    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Extrae tareas (checkboxes o listas)"""
        tasks = []
        
        # Buscar checkboxes
        for match in self.checkbox_pattern.finditer(content):
            checked = match.group(1).lower() == 'x'
            description = match.group(2).strip()
            priority = self._extract_priority(description)
            tags = self.tag_pattern.findall(description)
            
            tasks.append({
                "description": description,
                "completed": checked,
                "priority": priority,
                "tags": tags
            })
        
        return tasks
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extrae bloques de código con lenguaje"""
        code_blocks = []
        
        for match in self.code_block_pattern.finditer(content):
            language = match.group(1) or "text"
            code = match.group(2).strip()
            
            code_blocks.append({
                "language": language,
                "code": code
            })
        
        return code_blocks
    
    def _extract_priority(self, text: str) -> str:
        """Extrae prioridad de texto"""
        match = self.priority_pattern.search(text)
        
        if not match:
            return "medium"
        
        # Contar '!' o usar keyword
        priority_str = match.group(1)
        if '!!!' in priority_str:
            return "high"
        elif '!!' in priority_str:
            return "medium"
        elif '!' in priority_str:
            return "low"
        else:
            # Usar keyword
            return match.group(2) if match.group(2) else "medium"
    
    def extract_user_stories(self, content: str) -> List[Dict[str, Any]]:
        """
        Extrae user stories en formato:
        "Como [rol], quiero [acción], para [beneficio]"
        """
        user_story_pattern = re.compile(
            r'(?:como|as a?)\s+(.+?),?\s+(?:quiero|want to|i want)\s+(.+?),?\s+(?:para|so that)\s+(.+)',
            re.IGNORECASE
        )
        
        user_stories = []
        for match in user_story_pattern.finditer(content):
            user_stories.append({
                "role": match.group(1).strip(),
                "action": match.group(2).strip(),
                "benefit": match.group(3).strip()
            })
        
        return user_stories
