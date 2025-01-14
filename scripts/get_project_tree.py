import os

file_extensions  = ('.py', '.json', '.yaml', '.txt', '.js', '.css', '.html', '.png')

def get_project_tree(directory, max_depth=2, exclude_dirs=None):
    tree = {}
    exclude_dirs = exclude_dirs or []  # Список папок для исключения

    for root, dirs, files in os.walk(directory):
        # Вычисляем текущую глубину
        depth = root[len(directory):].count(os.sep)

        # Если текущая папка в списке исключений, пропускаем её
        if any(exclude_dir in os.path.abspath(root) for exclude_dir in exclude_dirs):
            continue

        # Если текущая глубина больше или равна max_depth, исключаем эту директорию
        if depth >= max_depth:
            # Останавливаем обход по этой директории и ее подкаталогам
            dirs.clear()

        # Собираем только основные файлы
        important_files = [file for file in files if file.endswith(file_extensions)]
        if important_files:
            tree[root] = important_files

    return tree


def print_tree(tree):
    for directory, files in tree.items():
        print(f"{directory}:")
        for file in files:
            print(f"  - {file}")


# Пример использования
project_directory = '..'  # Путь к корню проекта
exclude_dirs = [
    os.path.join('.venv', 'Lib', 'site-packages'),
    os.path.join('.venv', 'Scripts')
]

tree = get_project_tree(project_directory, max_depth=3, exclude_dirs=exclude_dirs)
print_tree(tree)
