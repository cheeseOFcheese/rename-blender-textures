# rename_albedo_textures.py
import bpy
import os

# Расширения файлов, которые нужно обрабатывать
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

# Скрипт переименовывает файлы текстур, подключенные к Base Color,
# используя имя материала и суффикс "_albedo"
for mat in bpy.data.materials:
    # Обработка только материалов с нодами
    if not mat.use_nodes:
        continue

    # Поиск ноды Principled BSDF
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf:
        continue

    # Проверка связей входа Base Color
    base_input = bsdf.inputs.get('Base Color')
    if not base_input or not base_input.is_linked:
        continue

    # Подключенный узел текстуры
    tex_node = base_input.links[0].from_node
    if tex_node.type != 'TEX_IMAGE':
        continue

    img = tex_node.image
    if not img or not img.filepath:
        continue

    # Получаем абсолютный путь к файлу
    orig_path = bpy.path.abspath(img.filepath)
    if not os.path.isfile(orig_path):
        print(f"Файл не найден: {orig_path}")
        continue

    # Проверяем расширение
    dirpath, filename = os.path.split(orig_path)
    name, ext = os.path.splitext(filename)
    ext_lower = ext.lower()
    if ext_lower not in ALLOWED_EXTENSIONS:
        print(f"Пропущен файл с неподдерживаемым расширением: {filename}")
        continue

    # Формируем новое имя: <имя_материала>_albedo<расширение>
    safe_mat_name = bpy.path.clean_name(mat.name)
    new_filename = f"{safe_mat_name}_albedo{ext_lower}"
    new_path = os.path.join(dirpath, new_filename)

    # Проверяем, не совпадает ли текущее имя с новым
    if os.path.normpath(orig_path) == os.path.normpath(new_path):
        print(f"Уже переименовано: {filename}")
        continue

    # Переименование файла на диске
    try:
        os.rename(orig_path, new_path)
        print(f"Переименовано: '{filename}' -> '{new_filename}'")
        # Обновляем путь в Blender
        img.filepath = bpy.path.relpath(new_path)
        img.name = os.path.splitext(new_filename)[0]
    except Exception as e:
        print(f"Ошибка при переименовании '{filename}': {e}")
