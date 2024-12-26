# Documentation Guide

This guide explains how to create, build, and maintain documentation for the Flask Auth Service project using Sphinx.

## Directory Structure

```
docs/
├── Makefile              # Build automation file
├── build/                # Generated documentation files
├── source/               # Documentation source files
│   ├── _static/         # Static files (images, custom CSS, etc.)
│   ├── _templates/      # Custom HTML templates
│   ├── conf.py          # Sphinx configuration file
│   ├── index.rst        # Main documentation page
│   └── tests.rst        # Test documentation
└── README.md            # This file
```

## Setup Instructions

1. Install required packages:
   ```bash
   pip install sphinx sphinx-rtd-theme
   ```

2. Create new documentation for a module:
   ```bash
   cd docs
   sphinx-quickstart  # If starting a new documentation project
   ```

## Building Documentation

1. Build HTML documentation:
   ```bash
   cd docs
   make html
   ```

2. View the documentation:
   - Open `docs/build/html/index.html` in a web browser

## Adding New Documentation

### 1. Add New RST Files

Create a new `.rst` file in `source/` directory:
```rst
Module Name
==========

Description of the module.

.. automodule:: path.to.your.module
   :members:
   :undoc-members:
   :show-inheritance:
```

### 2. Update index.rst

Add your new file to the toctree in `index.rst`:
```rst
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tests
   your_new_file
```

### 3. Writing Docstrings

Use Google-style docstrings in your Python code:

```python
def function_name(param1: type, param2: type) -> return_type:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ErrorType: Description of when this error is raised
    """
    pass
```

## Configuration

The documentation uses the following Sphinx extensions:

- `sphinx.ext.autodoc`: Automatically include documentation from docstrings
- `sphinx.ext.napoleon`: Support for Google-style docstrings
- `sphinx.ext.viewcode`: Add links to highlighted source code
- `sphinx.ext.coverage`: Check documentation coverage

Configure these in `source/conf.py`.

## Theme Customization

The documentation uses the Read the Docs theme. Customize it in `conf.py`:

```python
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
}
```

## Best Practices

1. **Documentation Structure**:
   - Keep related topics together
   - Use clear, descriptive headings
   - Include examples where appropriate

2. **Writing Style**:
   - Be clear and concise
   - Use consistent terminology
   - Include code examples for complex features

3. **Code Documentation**:
   - Document all public APIs
   - Include type hints
   - Explain parameters and return values
   - Document exceptions and edge cases

4. **Maintenance**:
   - Update docs when code changes
   - Check for broken links
   - Verify examples work
   - Run `make html` to check for errors

## Common Tasks

### Adding a New Test Module

1. Create test file with proper docstrings
2. Create new RST file in `source/`
3. Add to `index.rst` toctree
4. Update test documentation sections

### Updating Existing Documentation

1. Modify relevant RST files
2. Update docstrings in code
3. Rebuild documentation:
   ```bash
   make clean
   make html
   ```

### Adding Images

1. Place images in `source/_static/`
2. Reference in RST files:
   ```rst
   .. image:: _static/image_name.png
      :alt: Alternative text
   ```

## Troubleshooting

Common issues and solutions:

1. **Missing Modules**:
   - Check `sys.path` in `conf.py`
   - Verify module is importable

2. **Build Errors**:
   - Check syntax in RST files
   - Verify docstring format
   - Look for missing dependencies

3. **Autodoc Issues**:
   - Verify module path is correct
   - Check import statements
   - Ensure docstrings are properly formatted

## Additional Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Guide](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/) 