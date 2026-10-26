# Contributing to One

If you are interested in the project and wish to contribute, this document will provide you with the necessary instructions and guidelines to get started. We appreciate your contribution!

## Read this before starting

- [README](README.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## Index

- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Making a Fork](#making-a-fork)
- [Pull Request Process](#pull-request-process)
- [Testing Your Changes](#testing-your-changes)

## Project Structure
The project is structured as follows:

```
One/
├── src/
│   ├── main.py              # Main entry point
│   ├── ast/                 # Abstract Syntax Tree for parsing
│   ├── audio/               # Audio processing and VAD
│   ├── classifier/          # Intent classification
│   ├── commands/            # Command handler
│   ├── lexer/               # Tokenization
│   └── parser/              # Parser
├── frontend/               # Frontend interface (Slint)
├── database/                # Database logic
├── tests/                   # Unit tests
├── .github/workflows/       # GitHub Actions
├── requirements.txt         # Project dependencies
└── .env.example             # Example environment variables
```


## How to Contribute

There are several ways to contribute to the project:

### Report Bugs

Before creating a bug report, check the list of [issues](https://github.com/one-assist/One/issues).

When reporting a bug, include:
- Your environment (OS, Python version, project version)
- Steps to reproduce the behavior
- Observed behavior and expected behavior
- Screenshots or logs if possible

### Suggest Improvements

Suggestions for improvements are always welcome! When suggesting an improvement:

- Use a clear and descriptive title
- Provide a detailed description of the improvement suggested
- List examples of how the improvement would work
- Explain why this improvement would be useful

### Submit Pull Request

Contributions via pull requests are much appreciated!

 - Fork the repository and create your branch from `main`
 - Implement your changes
 - Ensure the code follows the project's style guide
 - Write tests for your changes
 - Update the documentation if necessary
 - Submit a pull request

## Making a Fork

### Requirements

- Python 3.8+
- Git
- A functional microphone
- `pip` and `venv`

### Setup

1. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/One.git
   cd One
   ```

2. **Configure repository upstream**
   ```bash
   git remote add upstream https://github.com/one-assist/One.git
   ```

3. **Create a branch**
   ```bash
   # Create a new branch for your feature
   git checkout -b feat/branch-name

   # Or for a bug fix
   git checkout -b fix/branch-name
   ```

4. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # (Linux/macOS)
   source venv/bin/activate
   
   # (Windows)
   venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

## Pull Request Process

1. **Keep your fork up to date**
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. **Use conventional commits**
   ```bash
   git commit -m "feat: add new command"
   
   # Or for a bug fix
   git commit -m "fix: fix bug in open program command"
   ```

3. **Push your changes**
   ```bash
   git push origin feat/branch-name
   ```

4. **Create a pull request**
   - Use a descriptive title
   - Include a clear description of the changes
   - Reference any related issues
   - Include screenshots if it's a visual change

## Testing Your Changes

### Execute application
   ```bash
   python -m src.main.py
   ```
### Execute tests
   ```bash
   python -m unittest tests/test_parser.py
   ```