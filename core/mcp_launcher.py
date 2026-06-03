"""
MCP Launcher - Flexible Version Selector
Allows launching v5 or v6 based on environment variable or argument
"""

import sys
import os
import logging
from pathlib import Path

# Setup paths statically for analyzers
current_dir = Path(__file__).resolve().parent
mcp_hub_root = current_dir.parent
if str(mcp_hub_root) not in sys.path: sys.path.insert(0, str(mcp_hub_root))
if str(current_dir) not in sys.path: sys.path.insert(0, str(current_dir))

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "mcp_launcher.log"

# Stream handler that handles encoding issues gracefully on Windows consoles
class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            try:
                stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                # Fallback to ascii or replacement characters
                stream.write(msg.encode('ascii', errors='replace').decode('ascii') + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        SafeStreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


def check_dependencies(version='v6'):
    """Check if all required dependencies are installed"""
    if version == 'v5':
        required = [
            'sentence_transformers',
            'hnswlib',
            'numpy',
            'torch'
        ]
    else:
        required = [
            'numpy',
            'mempalace',
            'mcp',
            'pydantic'
        ]
    
    missing = []
    for module in required:
        try:
            __import__(module)
            logger.info(f"✓ {module} disponible")
        except ImportError:
            missing.append(module)
            logger.error(f"✗ {module} NO disponible")
    
    if missing:
        logger.error(f"Dependencias faltantes para {version.upper()}: {', '.join(missing)}")
        logger.error("Ejecuta: pip install " + " ".join(missing))
        return False
    
    return True


def setup_paths():
    """Setup Python paths"""
    current_dir = Path(__file__).resolve().parent
    mcp_hub_root = current_dir.parent
    
    # Add to path
    sys.path.insert(0, str(mcp_hub_root))
    sys.path.insert(0, str(current_dir))
    
    logger.info(f"MCP Hub Root: {mcp_hub_root}")
    logger.info(f"Current Dir: {current_dir}")
    
    return mcp_hub_root


def create_required_directories(mcp_hub_root):
    """Create required directories if they don't exist"""
    directories = [
        mcp_hub_root / "data",
        mcp_hub_root / "data" / "sessions",
        mcp_hub_root / "data" / "code_index",
        mcp_hub_root / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directorio verificado: {directory}")


def get_version_from_args():
    """Get version from command line arguments or environment variable"""
    # Check command line arguments
    if len(sys.argv) > 1:
        version_arg = sys.argv[1].lower()
        if version_arg in ['v5', '5']:
            return 'v5'
        elif version_arg in ['v6', '6']:
            return 'v6'
    
    # Check environment variable
    version_env = os.environ.get('MCP_VERSION', '').lower()
    if version_env in ['v5', '5']:
        return 'v5'
    elif version_env in ['v6', '6']:
        return 'v6'
    
    # Default to v6
    return 'v6'


def main():
    """Main entry point"""
    try:
        logger.info("="*80)
        logger.info("MCP Launcher - Flexible Version Selector")
        logger.info("="*80)
        
        # Determine version
        version = get_version_from_args()
        logger.info(f"🎯 Version seleccionada: {version.upper()}")
        
        # Check dependencies
        logger.info("Verificando dependencias...")
        if not check_dependencies(version):
            logger.error("Faltan dependencias críticas. Abortando.")
            sys.exit(1)
        
        # Setup paths
        logger.info("Configurando rutas...")
        mcp_hub_root = setup_paths()
        
        # Create directories
        logger.info("Creando directorios necesarios...")
        create_required_directories(mcp_hub_root)
        
        # Import and run appropriate server
        if version == 'v5':
            logger.info("Importando servidor MCP v5...")
            from mcp_server_v5 import main as server_main
            logger.info("Iniciando servidor MCP v5...")
        else:  # v6
            logger.info("Importando servidor MCP v6 (nuevo v6.py)...")
            from v6 import main as server_main
            logger.info("Iniciando servidor MCP v6...")
        
        server_main()
        
    except ImportError as e:
        logger.error(f"Error de importación: {e}", exc_info=True)
        logger.error("Verifica que todas las dependencias estén instaladas")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}", exc_info=True)
        logger.error("Verifica la estructura del proyecto")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
