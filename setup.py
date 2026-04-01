from setuptools import setup, find_packages

setup(
    name="lama-lang",
    version="1.0.0",
    description="🦙 LAMA — a beginner-friendly programming language",
    py_modules=[
        "lama",
        "lexer",
        "parser",
        "interpreter",
        "builtins_lama",
        "package_manager",
    ],
    entry_points={
        "console_scripts": [
            "lama=lama:main",
        ],
    },
    python_requires=">=3.8",
)
