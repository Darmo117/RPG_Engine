import pathlib
import shutil
import sys

import fonts_repo

fonts_repo_path = pathlib.Path(fonts_repo.path).expanduser() / 'fonts'
dest_path = pathlib.Path('..', 'run', 'data', 'fonts')

for font_family in fonts_repo_path.glob('NotoSans*'):
    print(font_family)
    if font_family.is_dir():
        # Using glob as font file name prefix may not be the exact same as directory name
        font_file = next((font_family / 'googlefonts' / 'ttf').glob('*-Regular.ttf'))
        try:
            shutil.copy(font_file, dest_path / (font_family.name + '.ttf'))
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
