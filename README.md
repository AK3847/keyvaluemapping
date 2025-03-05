# How to use:

- git clone this repo:
```bash
git clone https://github.com/AK3847/keyvaluemapping.git
cd keyvaluemapping
```

- setup a virtual environment for python and activate it (optional):
```bash
python -m venv .venv
.venv\Scripts\activate
```

- install requirements:
```bash
pip install -r requirements.txt
```

- run the `excel_to_php_converter.py` using:
```bash
python excel_to_php_converter.py
```

- Give your input file name (excel file)
- A menu will appear, choose the desired sheet by using ↓ ↑ for navigation.
- Once the desired sheet you will be again prompted to choose the **Key** column, again use ↓ ↑ for navigation.
- Similary, select your **Value** column.
- Finally give your output file name (without php) and the file will be stored in an `output` folder with given filename.