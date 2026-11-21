"""Собирает manifest.json для автообновления.
Запуск:  python make_manifest.py <github_user> <repo> [branch]
Кладёт в эту папку: svotactical-<версия>.jar (последний из build/libs), svo_ss.zip (пак винтовок TACZ) и manifest.json.
Потом всё содержимое этой папки (кроме make_manifest.py) загружается в репозиторий GitHub (Add file -> Upload files).
"""
import glob, hashlib, json, os, re, shutil, sys, zipfile

user, repo = sys.argv[1], sys.argv[2]
branch = sys.argv[3] if len(sys.argv) > 3 else 'main'
here = os.path.dirname(os.path.abspath(__file__))
libs = r'D:\claude\internet\SvoTacticalCore\build\libs'
tacz = r'D:\C-perenos\PrismLauncher\instances\1.20.1\minecraft\tacz\svo_ss'

jars = sorted(glob.glob(libs + r'\svotactical-*.jar'), key=lambda p: [int(x) for x in re.findall(r'\d+', os.path.basename(p))])
jar = jars[-1]
name = os.path.basename(jar)
version = re.search(r'svotactical-(.+)\.jar', name).group(1)
shutil.copy(jar, os.path.join(here, name))

zpath = os.path.join(here, 'svo_ss.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(tacz):
        for f in files:
            full = os.path.join(root, f)
            if f.endswith('.bak_svo'): continue
            z.write(full, os.path.relpath(full, tacz))   # gunpack.meta.json в корне архива

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
raw = 'https://raw.githubusercontent.com/%s/%s/%s/' % (user, repo, branch)

old = [os.path.basename(j) for j in jars if os.path.basename(j) != name]
delete = ['mods/' + o for o in old] + [
    'mods/svohider-1.1.0.jar',
    'mods/entityculling-forge-1.11.2-mc1.20.1.jar',
    'mods/chloride-FORGE-mc1.20.1-v1.8.1.jar',
    'mods/Terralith_1.20.x_v2.5.4.jar',
    'mods/tectonic-3.0.17-forge-1.20.1.jar',
]
manifest = {
    'version': version,
    'files': [
        {'path': 'mods/' + name, 'url': raw + name, 'sha256': sha(os.path.join(here, name))},
        {'path': 'tacz/svo_ss.zip', 'url': raw + 'svo_ss.zip', 'sha256': sha(zpath)},
        # сторонний пак качается с CurseForge напрямую, в репозиторий не кладётся
        # ресурспак стёкол для русских деревень (CurseForge, оригинальная ссылка; включает его мод — PackAutoEnable)
        {'path': 'resourcepacks/BSG - Medieval - 1.20.zip', 'url': 'https://mediafilez.forgecdn.net/files/4779/199/BSG%20-%20Medieval%20-%201.20.zip', 'sha256': sha('D:/C-perenos/PrismLauncher/instances/1.20.1/minecraft/resourcepacks/BSG - Medieval - 1.20.zip')},
        {'path': 'tacz/mw19_guns_addon_v200.zip', 'url': 'https://edge.forgecdn.net/files/6505/302/mw19_guns_addon_v200.zip', 'sha256': sha('D:/C-perenos/PrismLauncher/instances/1.20.1/minecraft/tacz/mw19_guns_addon_v200.zip')},
    ],
    'delete': delete,
}
json.dump(manifest, open(os.path.join(here, 'manifest.json'), 'w', encoding='utf-8'), indent=2)
print('версия', version, '| manifest:', raw + 'manifest.json')
