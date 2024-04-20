'''该脚本必须在脚本所在目录的上一级目录中即项目目录下执行
执行语句为：python ./custom_gpts/get_trees.copy
不能在custom_gpts目录下执行 否则会报错'''

from fpdf import FPDF  # 确保这里导入的是 fpdf2
import os
import datetime
from tqdm import tqdm

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font_path = os.path.join('custom_gpts', 'msyh.ttf')
        if os.path.isfile(font_path):
            self.add_font('msyh', '', font_path)
            self.font_family = 'msyh'
            self.set_font('msyh', '', 12)

    def add_creation_time(self):
        self.set_font('msyh', '', 18)
        self.cell(0, 10, '生成时间: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), new_x="LMARGIN", new_y="NEXT")


    def header(self):
        # 使用常规样式，不使用加粗
        self.set_font(self.font_family, '', 18)
        # 这里可以添加您希望在页眉中显示的内容，例如：
        # self.cell(0, 10, '页眉内容', new_x="LMARGIN", new_y="NEXT")

    def chapter_title(self, title):
        self.set_font(self.font_family, '', 14)  # 使用常规样式
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        
    def chapter_body(self, body):
        self.set_font(self.font_family, '', 12)
        self.multi_cell(0, 8, body)  # 第二个参数是行高
        self.ln(10)  # 在段落之后添加额外的空白行

def generate_directory_index(path, ignore_dirs, depth=0):
    index = ''
    items = os.listdir(path)
    last_item = len(items) - 1

    for i, item in enumerate(items):
        item_path = os.path.join(path, item)
        if item in ignore_dirs or not os.path.exists(item_path):
            continue

        prefix = '└── ' if i == last_item else '├── '

        if os.path.isdir(item_path):
            index += '│   ' * depth + prefix + item + '/\n'
            index += generate_directory_index(item_path, ignore_dirs, depth + 1)
        else:
            index += '│   ' * depth + prefix + item + '\n'
    
    if depth != 0 and index != '':
        index = '│\n' + index

    return index



def main():
    print("Starting")
    print("Current Working Dir:", os.getcwd())

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    root_directory = os.path.basename(project_root)  # 获取项目根目录的名称
    pdf_path = os.path.join(project_root, 'custom_gpts', f'{root_directory}.pdf')  # 使用动态获取的项目根目录名称
    ignore_dirs = ['custom_gpts', 'myvenv', '.git', 'staticfiles', 'venv','__pycache__','media','myvenv2','collectedstatic','ssimg/whoosh_index','ipv6test_venv']
    included_extensions = [
    '.py',      # Python
    '.html',    # HTML (HyperText Markup Language)
    '.js',      # JavaScript
    '.css',     # Cascading Style Sheets
    '.txt',      # Plain text
    '.go',       # Go
    '.c',       # C programming language
    '.cpp',     # C++
    '.java',    # Java
    '.jsx',     # JavaScript (used with React)
    '.ts',       # TypeScript
    '.tsx',     # TypeScript (used with JSX)
    '.rb',       # Ruby
    '.php',     # PHP: Hypertext Preprocessor
    '.asp',     # Active Server Pages (similar to .php)
    '.aspx',    # ASP.NET Web Forms
    '.rsx',      # Rust (used for HTML-like templates)
    '.swift',    # Swift
    '.scss',    # Sass (CSS preprocessor)
    '.less',    # LESS (CSS preprocessor)
    '.md',       # Markdown
    '.rs',      # Rust
    '.kt',       # Kotlin
    '.scala',   # Scala
    '.rbxm',     # Roblox Lua (used for Roblox game development)
    '.lua',     # Lua
    '.rs',       # R (similar to .R)
    '.R',        # R programming language
    '.sh',       # Shell script (Bash, Kornshell, etc.)
    '.bat',      # Batch file (Windows)
    '.sh',       # Shell script (Unix/Linux)
    '.pl',       # Perl
    '.ruby',    # Ruby (alternative to .rb)
    '.jl',       # Julia
    '.rnf',       # Racket
    '.elm',      # Elm
    '.hpp',      # C++ header file
    '.h',        # C header file
    '.pas',      # Pascal
    '.adb',      # Ada
    '.dart',      # Dart
    '.ktd',      # Kotlin (test files)
    '.spec',     # Rust (specification files)
    '.zsh',      # Zsh script
    '.fish',     # Fish shell script
    '.mdw',       # Markdown with additional attributes (e.g., for Jupyter notebooks)
    '.ipynb',    # Jupyter Notebook
    '.jlx',       # Julia with HTML-like syntax (alternative to .jl)
     ]
    pdf = PDF(format='A3')
    #pdf.set_auto_page_break(auto=False)  # 禁用自动分页
    pdf.add_page()
    pdf.add_creation_time()
    pdf.chapter_title(f"项目目录树,项目根目录名称:{root_directory}")  # 使用动态获取的项目根目录名称
    pdf.chapter_body(generate_directory_index(project_root, ignore_dirs))

    all_files = []
    for root, dirs, files in os.walk(project_root, topdown=True):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(tuple(included_extensions)):
                all_files.append((root, file))

    for root, file in tqdm(all_files, desc="处理中", unit="file"):
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, project_root)

        pdf.chapter_title(relative_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"无法读取文件内容: {e}"
        pdf.chapter_body("\n" + content + "\n" + ("-" * 50))

    pdf.output(pdf_path)
    print("\nPDF Dealt, The pwd is :", pdf_path)

if __name__ == "__main__":
    main()
