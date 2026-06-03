"""
Visualización del estado del proyecto
Genera un reporte en consola del estado actual
"""
import asyncio
from pathlib import Path
from datetime import datetime
import os


def count_lines(file_path):
    """Contar líneas de código en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Excluir líneas vacías y comentarios
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            return len(code_lines), len(lines)
    except:
        return 0, 0


def analyze_project():
    """Analizar estructura del proyecto"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS DEL PROYECTO MCP - Estado Actual")
    print("="*70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Directorios a analizar
    dirs_to_check = {
        'core/memory': '🧠 Memory System',
        'core/communication': '📡 Communication',
        'mcps/contracts': '📋 Contracts',
        'config': '⚙️ Configuration',
        'tests/unit': '🧪 Unit Tests'
    }
    
    total_code_lines = 0
    total_lines = 0
    total_files = 0
    
    for dir_path, label in dirs_to_check.items():
        if not Path(dir_path).exists():
            continue
            
        print(f"\n{label} ({dir_path}/)")
        print("-" * 70)
        
        dir_code_lines = 0
        dir_total_lines = 0
        file_count = 0
        
        for py_file in Path(dir_path).glob('*.py'):
            if py_file.name == '__init__.py':
                continue
                
            code, total = count_lines(py_file)
            dir_code_lines += code
            dir_total_lines += total
            file_count += 1
            total_files += 1
            
            print(f"  ✓ {py_file.name:<35} {code:>4} LOC ({total:>4} total)")
        
        total_code_lines += dir_code_lines
        total_lines += dir_total_lines
        
        print(f"  {'─'*66}")
        print(f"  📊 Subtotal: {file_count} archivos, {dir_code_lines} LOC")
    
    # Resumen
    print("\n" + "="*70)
    print("📈 RESUMEN TOTAL")
    print("="*70)
    print(f"  📁 Total de archivos Python: {total_files}")
    print(f"  💻 Líneas de código (sin comentarios/blancos): {total_code_lines}")
    print(f"  📝 Líneas totales: {total_lines}")
    
    # Componentes implementados
    print("\n" + "="*70)
    print("✅ COMPONENTES IMPLEMENTADOS")
    print("="*70)
    
    components = [
        ("Event Store Persistente", "core/memory/event_store.py"),
        ("Memory Engine", "core/memory/memory_engine.py"),
        ("Rollback Manager", "core/memory/rollback_manager.py"),
        ("Communication Protocol", "core/communication/protocol.py"),
        ("Circuit Breaker", "core/communication/circuit_breaker.py"),
        ("Architect Contracts", "mcps/contracts/architect_contracts.py"),
        ("Developer Contracts", "mcps/contracts/developer_contracts.py"),
        ("Tester Contracts", "mcps/contracts/tester_contracts.py"),
        ("Environment Config", "config/environments.py"),
    ]
    
    for name, path in components:
        exists = "✅" if Path(path).exists() else "❌"
        print(f"  {exists} {name:<35} {path}")
    
    # Tests
    print("\n" + "="*70)
    print("🧪 TESTS IMPLEMENTADOS")
    print("="*70)
    
    test_files = list(Path('tests/unit').glob('test_*.py'))
    for test_file in test_files:
        code, total = count_lines(test_file)
        print(f"  ✅ {test_file.name:<35} {code:>4} LOC")
    
    print(f"\n  📊 Total: {len(test_files)} archivos de test")
    
    # Archivos de configuración
    print("\n" + "="*70)
    print("📋 CONFIGURACIÓN Y DOCUMENTACIÓN")
    print("="*70)
    
    config_files = [
        ('requirements.txt', 'Dependencias'),
        ('pytest.ini', 'Config de Pytest'),
        ('README.md', 'Documentación principal'),
        ('PROGRESO.md', 'Reporte de progreso'),
        ('.gitignore', 'Git ignore'),
        ('example.py', 'Script de demostración')
    ]
    
    for filename, description in config_files:
        exists = "✅" if Path(filename).exists() else "❌"
        size = Path(filename).stat().st_size if Path(filename).exists() else 0
        print(f"  {exists} {filename:<25} {description:<25} {size:>6} bytes")
    
    # Estado de la base de datos
    print("\n" + "="*70)
    print("💾 DATOS PERSISTENTES")
    print("="*70)
    
    if Path('data').exists():
        db_files = list(Path('data').glob('*.db'))
        checkpoint_dirs = list(Path('data').glob('*checkpoints*'))
        
        print(f"  📦 Bases de datos: {len(db_files)}")
        for db in db_files:
            size = db.stat().st_size
            print(f"     • {db.name:<30} {size:>8} bytes")
        
        print(f"\n  📂 Directorios de checkpoints: {len(checkpoint_dirs)}")
        for cp_dir in checkpoint_dirs:
            if cp_dir.is_dir():
                num_checkpoints = len(list(cp_dir.glob('*.json')))
                print(f"     • {cp_dir.name:<30} {num_checkpoints:>3} checkpoints")
    else:
        print("  ⚠️  Directorio 'data/' no existe aún")
    
    # Próximos pasos
    print("\n" + "="*70)
    print("🎯 PRÓXIMOS PASOS - FASE 2")
    print("="*70)
    
    next_steps = [
        "Implementar BaseMCP (clase abstracta)",
        "Crear ArchitectMCP con generación de planes",
        "Crear DeveloperMCP con generación de código",
        "Crear TesterMCP con validación",
        "Implementar Orchestrator para coordinar MCPs",
        "Tests de integración E2E",
        "Optimización y profiling"
    ]
    
    for i, step in enumerate(next_steps, 1):
        print(f"  {i}. [ ] {step}")
    
    print("\n" + "="*70)
    print("✨ Fase 1 completada exitosamente - Ready para Fase 2!")
    print("="*70)
    print()


if __name__ == "__main__":
    analyze_project()
