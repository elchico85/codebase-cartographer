import os
import ast
import argparse
from pathlib import Path
from collections import defaultdict
import time

# --- Gestione delle Dipendenze Opzionali ---
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    VISUALS_AVAILABLE = True
except ImportError:
    VISUALS_AVAILABLE = False

try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
# ---------------------------------------------


class ReportGenerator:
    """Gestisce la creazione del report in formato Markdown."""
    def __init__(self, filename="codebase_audit_report.md"):
        self.filename = filename
        self.content = []
        self.add_title("Codebase Audit Report")

    def add_title(self, text, level=1):
        self.content.append(f"{'#' * level} {text}\n")

    def add_paragraph(self, text):
        self.content.append(f"{text}\n")

    def add_code_block(self, code, lang=""):
        self.content.append(f"```{lang}\n{code}\n```\n")

    def add_list(self, items, numbered=False):
        for i, item in enumerate(items):
            prefix = f"{i+1}." if numbered else "-"
            self.content.append(f"{prefix} {item}")
        self.content.append("") # Spazio extra

    def add_table(self, headers, data):
        if TABULATE_AVAILABLE:
            self.content.append(tabulate(data, headers=headers, tablefmt="github"))
        else: # Fallback a un formato semplice
            self.content.append(" | ".join(headers))
            self.content.append(" | ".join(["---"] * len(headers)))
            for row in data:
                self.content.append(" | ".join(map(str, row)))
        self.content.append("\n")

    def add_image(self, path, alt_text=""):
        # Usa percorsi relativi per la portabilità
        relative_path = Path(path).name
        self.content.append(f"![{alt_text}]({relative_path})\n")

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.content))
        print(f"   - ✅ Report salvato come '{self.filename}'")


class CodebaseAuditor:
    """
    Uno strumento completo per analizzare, mappare e comprendere un codebase Python.
    Genera un report completo in formato Markdown.
    """
    def __init__(self, root_dir, report_filename="codebase_audit_report.md"):
        self.root_dir = Path(root_dir).resolve()
        self.report = ReportGenerator(report_filename)
        
        # Strutture dati
        self.python_files = []
        self.project_modules = set()
        self.functions = {}
        self.classes = {}
        self.main_entry_points = []
        self.dependencies = defaultdict(set)
        self.data_files = []

    def _discover_files(self):
        """Scopre tutti i file Python e i moduli del progetto."""
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '_build', '.pytest_cache', '.venv']]
            
            for file in files:
                file_path = Path(root) / file
                if file.endswith('.py'):
                    self.python_files.append(str(file_path))
                    module_name = str(file_path.relative_to(self.root_dir)).replace(os.sep, '.')[:-3]
                    self.project_modules.add(module_name)
                elif file.endswith(('.csv', '.xlsx', '.json', '.yaml')):
                    self.data_files.append(file_path)

    def _analyze_file(self, file_path):
        """Esegue un'analisi AST completa su un singolo file."""
        file_path_obj = Path(file_path)
        relative_path = file_path_obj.relative_to(self.root_dir)
        module_name = str(relative_path).replace(os.sep, '.')[:-3]

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)

            if 'if __name__ == "__main__"' in content:
                self.main_entry_points.append(module_name)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = f"{module_name}.{node.name}"
                    self.functions[func_name] = {
                        'complexity': sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With))) + 1
                    }
                elif isinstance(node, ast.ClassDef):
                    class_name = f"{module_name}.{node.name}"
                    methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
                    self.classes[class_name] = {'methods': methods, 'is_strategy': 'strategy' in node.name.lower() or 'strategies' in module_name}
                elif isinstance(node, ast.Import):
                    for alias in node.names: self._add_dependency(module_name, alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module: self._add_dependency(module_name, node.module, node.level)
                        
        except Exception as e:
            print(f"   - ⚠️  Errore nell'analisi di {relative_path}: {e}")

    def _add_dependency(self, module_name, dep_name, level=0):
        if level > 0:
            parts = module_name.split('.')
            base = parts[: -level]
            resolved_dep = '.'.join(base + ([dep_name] if dep_name else []))
        else:
            resolved_dep = dep_name

        if any(resolved_dep.startswith(proj_mod) for proj_mod in self.project_modules if proj_mod == resolved_dep):
             self.dependencies[module_name].add(resolved_dep)

    # --- Metodi di generazione dei contenuti del Report ---

    def generate_architecture_overview(self):
        self.report.add_title("Architecture Overview", level=2)
        components = defaultdict(list)
        for module in self.project_modules:
            if module.startswith('pages'): components["🖥️ User Interface (Streamlit Pages)"].append(module)
            elif module.startswith('src.strategies'): components["🧠 Optimization Strategies"].append(module)
            elif 'pipeline' in module or 'run' in module: components["⚙️ Business Logic / Pipelines"].append(module)
            elif module.startswith('src.models') or module.startswith('src.schemas'): components["🧱 Data Models & Schemas"].append(module)
            elif module.startswith('src.data_'): components["💾 Data Processing"].append(module)
            elif module.startswith('src.utils'): components["🛠️ Support Utilities"].append(module)
            elif module.startswith('src.config'): components["⚙️ Configuration"].append(module)
            elif module.startswith('tests'): components["✅ Tests"].append(module)
            elif module == 'app': components["🚀 Main Entry Point"].append(module)
            else: components["🧩 Other Components"].append(module)
            
        for component_name, modules in sorted(components.items()):
            self.report.add_title(f"{component_name} ({len(modules)} modules)", level=3)
            self.report.add_list(sorted(modules))

    def generate_logical_flow(self):
        self.report.add_title("Logical & Execution Flow", level=2)

        self.report.add_title("Detected Entry Points", level=3)
        entry_points = sorted(list(set(['app'] + self.main_entry_points)))
        self.report.add_list([f"`{e}`" for e in entry_points])
        
        strategies = [c for c, v in self.classes.items() if v['is_strategy']]
        if strategies:
            self.report.add_title("Optimization Strategies", level=3)
            data = [[f"`{s}`", ", ".join(self.classes[s]['methods'][:4]) + ('...' if len(self.classes[s]['methods'])>4 else '')] for s in sorted(strategies)]
            self.report.add_table(["Strategy Class", "Key Methods"], data)

        pipeline_funcs = [f for f in self.functions.keys() if 'pipeline' in f or 'run' in f or 'solve' in f]
        if pipeline_funcs:
            self.report.add_title("Key Pipeline Functions", level=3)
            data = [[f"`{f}`", self.functions[f]['complexity']] for f in sorted(pipeline_funcs)]
            self.report.add_table(["Function", "Estimated Complexity"], data)
    
    def generate_data_flow(self):
        self.report.add_title("Data Flow Analysis", level=2)
        if self.data_files:
            self.report.add_title("Identified Data Files", level=3)
            data = []
            for file in self.data_files:
                rel_path = file.relative_to(self.root_dir)
                file_type = "Tabular Data" if ".csv" in file.name else "Excel Sheet" if ".xlsx" in file.name else "Config" if ".yaml" in file.name else "JSON Data"
                data.append([f"`{rel_path}`", file_type])
            self.report.add_table(["File Path", "Type"], data)

        data_funcs = [f for f in self.functions.keys() if any(w in f for w in ['load', 'save', 'process', 'read', 'write', 'preprocess'])]
        if data_funcs:
            self.report.add_title("Data Manipulation Functions", level=3)
            self.report.add_list([f"`{f}`" for f in sorted(data_funcs)])

    def generate_dependency_report(self):
        self.report.add_title("Internal Dependency Map", level=2)
        
        # Genera il grafico visuale per primo, così può essere incluso nel report
        image_path = "codebase_dependency_map.png"
        if VISUALS_AVAILABLE:
            print("🎨 Generating visual graph...")
            try:
                self.visualize_dependencies(image_path)
                self.report.add_title("Visual Dependency Graph", level=3)
                self.report.add_image(image_path, "Dependency map of the project modules")
            except Exception as e:
                self.report.add_paragraph(f"**Warning:** Could not generate visual graph. Error: {e}")
        else:
            self.report.add_paragraph("**Info:** To generate a visual graph, install required libraries: `pip install matplotlib networkx`")

        self.report.add_title("Textual Dependency Report", level=3)
        for module in sorted(self.dependencies.keys()):
            self.report.add_paragraph(f"**`{module}`** depends on:")
            if self.dependencies[module]:
                self.report.add_list([f"`{d}`" for d in sorted(list(self.dependencies[module]))])
            else:
                self.report.add_list(["(No internal dependencies)"])

    def visualize_dependencies(self, output_file):
        G = nx.DiGraph()
        for module, deps in self.dependencies.items():
            G.add_node(module)
            for dep in deps:
                G.add_node(dep)
                G.add_edge(dep, module)

        if not G.nodes(): return

        plt.figure(figsize=(20, 20), dpi=100)
        pos = nx.spring_layout(G, k=0.9, iterations=50, seed=42)
        node_sizes = [2000 + 2000 * G.in_degree(n) for n in G.nodes()]
        node_colors = [G.in_degree(n) for n in G.nodes()]

        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, cmap=plt.cm.viridis, alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, arrowsize=15, edge_color='gray')
        nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
        
        plt.title('Codebase Dependency Map', size=20)
        plt.axis('off'); plt.tight_layout()
        plt.savefig(output_file); plt.close()
        print(f"   - ✅ Visual graph saved as '{output_file}'")

    def generate_summary_stats(self):
        self.report.add_title("Project Statistics", level=2)
        total_funcs = len(self.functions)
        total_classes = len(self.classes)
        avg_complexity = (sum(f['complexity'] for f in self.functions.values()) / total_funcs) if total_funcs > 0 else 0
        total_deps = sum(len(d) for d in self.dependencies.values())

        data = [
            ["Python Files Analyzed", len(self.python_files)],
            ["Project Modules", len(self.project_modules)],
            ["Total Functions", total_funcs],
            ["Total Classes", total_classes],
            ["Optimization Strategies", len([c for c, v in self.classes.items() if v['is_strategy']])],
            ["Avg. Function Complexity", f"{avg_complexity:.2f}"],
            ["Internal Dependency Links", total_deps]
        ]
        self.report.add_table(["Metric", "Value"], data)

    def run(self):
        """Esegue l'intero processo di audit e genera il report."""
        start_time = time.time()
        print("🚀 Starting codebase audit...")
        
        print("1. Discovering project files...")
        self._discover_files()

        print(f"2. Analyzing {len(self.python_files)} Python files...")
        for file_path in self.python_files:
            self._analyze_file(file_path)

        print("3. Generating report sections...")
        self.generate_summary_stats()
        self.generate_architecture_overview()
        self.generate_logical_flow()
        self.generate_data_flow()
        self.generate_dependency_report() # Deve essere l'ultimo per includere il grafico

        print("4. Saving final report...")
        self.report.save()

        end_time = time.time()
        print(f"🎉 Audit complete in {end_time - start_time:.2f} seconds.")


def main():
    parser = argparse.ArgumentParser(description="Analyzes a Python codebase and generates a Markdown report.")
    parser.add_argument('directory', nargs='?', default='.', help="The project root directory (default: current directory).")
    parser.add_argument('--output', default='codebase_audit_report.md', help="Output Markdown file name.")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"❌ Error: Directory '{args.directory}' not found.")
        return

    auditor = CodebaseAuditor(args.directory, report_filename=args.output)
    auditor.run()

if __name__ == "__main__":
    main()