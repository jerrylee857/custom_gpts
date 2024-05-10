from fpdf import FPDF
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
        self.set_font(self.font_family, '', 18)

    def chapter_title(self, title):
        self.set_font(self.font_family, '', 14)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        
    def chapter_body(self, body):
        self.set_font(self.font_family, '', 12)
        self.multi_cell(0, 8, body)
        self.ln(10)

def should_ignore_dir(path, ignore_dirs):
    for ignore_dir in ignore_dirs:
        if os.path.abspath(ignore_dir) == os.path.abspath(path):
            return True
    return False

def should_ignore_file(path, ignore_paths, project_root):
    # 获取文件的相对于项目根目录的路径
    relative_path = os.path.relpath(os.path.abspath(path), project_root)
    for ignore_path in ignore_paths:
        # 处理通配符
        if ignore_path.endswith('*'):
            ignore_dir = ignore_path.rstrip('*').rstrip('/')
            if relative_path.startswith(ignore_dir) and relative_path[len(ignore_dir):].lstrip('/').split('/')[0] == '':
                return True
        # 直接相对路径匹配
        elif os.path.normpath(ignore_path) == os.path.normpath(relative_path):
            return True
    return False

def generate_directory_index(path, ignore_dirs, depth=0):
    index = ''
    items = os.listdir(path)
    last_item = len(items) - 1

    for i, item in enumerate(items):
        item_path = os.path.join(path, item)
        if should_ignore_dir(item_path, ignore_dirs) or not os.path.exists(item_path):
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
    root_directory = os.path.basename(project_root)
    pdf_path = os.path.join(project_root, 'custom_gpts', f'{root_directory}.pdf')
    ignore_paths = [
        'custom_gpts', 'myvenv', '.git', 'staticfiles', 'venv', '__pycache__', 'media', 'myvenv2', 'collectedstatic',
        'ssimg/whoosh_index', 'ipv6test_venv', 'backend/node_modules', 'backend/package-lock.json', 'backend/*.db',
        'frontend/node_modules', 'frontend/package-lock.json', 'backend/.git', 'frontend/.git','new_server.js','backend_api.doc'
    ]
    
    included_extensions = [
        '.py', '.html', '.js', '.css', '.txt', '.go', '.c', '.cpp', '.java', '.jsx', '.ts', '.tsx', '.rb', '.php',
        '.asp', '.aspx', '.rsx', '.swift', '.scss', '.less', '.md', '.rs', '.kt', '.scala', '.rbxm', '.lua', '.rs', '.R',
        '.sh', '.bat', '.sh', '.pl', '.ruby', '.jl', '.rnf', '.elm', '.hpp', '.h', '.pas', '.adb', '.dart', '.ktd',
        '.spec', '.zsh', '.fish', '.mdw', '.ipynb', '.jlx', '.json', '.md', '.yaml', '.vue'
    ]

    pdf = PDF(format='A3')
    pdf.add_page()
    pdf.add_creation_time()
    pdf.chapter_title(f"项目目录树,项目根目录名称:{root_directory}")
    pdf.chapter_body(generate_directory_index(project_root, ignore_paths))

    # 添加用于处理文件的代码
    all_files = []
    for root, dirs, files in os.walk(project_root, topdown=True):
        dirs[:] = [d for d in dirs if not should_ignore_dir(os.path.join(root, d), ignore_paths)]
        files[:] = [f for f in files if not should_ignore_file(os.path.join(root, f), ignore_paths, project_root)]  # 修正了此处
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
    print("\nPDF generated, location:", pdf_path)

if __name__ == "__main__":
    main()
