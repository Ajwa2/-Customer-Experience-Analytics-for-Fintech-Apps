# Notebooks

Place exploratory Jupyter notebooks in this folder. Use the same virtual environment as the project or create a separate `requirements-notebooks.txt` if you need notebook-only packages (e.g., `notebook`, `ipykernel`, `pandas`, `plotly`).

To run a notebook server:

```powershell
python -m pip install notebook ipykernel
python -m ipykernel install --user --name=project-env
jupyter notebook
```
