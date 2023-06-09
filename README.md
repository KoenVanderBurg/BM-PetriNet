# BM-PetriNet

This tool allows you to render and simulate a Petri Net from a KGML (KEGG database) file. 
Due to limiting factors, only basic data exploration is possible, thus this is not a tool to base fully fledged experiments on.

## Requirements

- python 3.11.2
- pip 23.1.2
- matplotlib 3.7.1

## Usage

1. Clone the repository
2. Create a virtual environment and activate it

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Build the project

```bash
pip install -e .
```

4. Run the project

```bash
KGML_PetriNet path/to/kgml/file
```

## Extra information	

More information about the KGML file structure can be found in the KEGG markup [documentation](https://www.genome.jp/kegg/xml/docs/).
