# Quick Start Guide for Documentation

This is a quick guide to get you started with building and maintaining documentation.

## First Time Setup

1. Install documentation dependencies:
   ```bash
   cd docs
   pip install -r requirements.txt
   ```

2. Build the documentation:
   ```bash
   make html
   ```

3. View the documentation:
   - Open `build/html/index.html` in your browser

## Common Tasks

### Adding Documentation for a New Module

1. Create a new RST file in `source/`:
   ```bash
   touch source/your_module.rst
   ```

2. Add basic structure:
   ```rst
   Your Module Name
   ===============

   .. automodule:: path.to.your.module
      :members:
      :undoc-members:
      :show-inheritance:
   ```

3. Add to `source/index.rst`:
   ```rst
   .. toctree::
      :maxdepth: 2
      :caption: Contents:

      tests
      your_module
   ```

### Live Preview While Writing

Use sphinx-autobuild for live preview:
```bash
sphinx-autobuild source build/html
```

### Writing Good Docstrings

Example of a well-documented function:
```python
def process_data(input_data: dict, options: Optional[dict] = None) -> List[str]:
    """Process the input data according to specified options.

    Args:
        input_data: The data to process
        options: Optional configuration parameters

    Returns:
        List of processed strings

    Raises:
        ValueError: If input_data is empty
        TypeError: If input_data is not a dictionary
    """
    pass
```

## Tips

1. Always rebuild docs after changes:
   ```bash
   make clean
   make html
   ```

2. Check for warnings in build output

3. Test documentation examples

4. Keep docstrings up to date with code

## Need Help?

- Check the full guide in `README.md`
- Refer to [Sphinx Documentation](https://www.sphinx-doc.org/)
- Look at existing documentation for examples 