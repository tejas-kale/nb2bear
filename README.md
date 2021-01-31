# nb2bear
> Package to convert a Jupyter notebook to a Bear note.


[Bear](https://bear.app) is a popular note-taking app on Mac which also serves as an excellent knowledge base. Analysts
and data scientists often use Jupyter notebooks for exploring data and models. But when we have notebooks scattered
across multiple projects, it can be tedious to search them without explicitly starting a Jupyter server or running a
`nbviewer` server.

The aim of this package is to add a Jupyter notebook as a Bear note with the appropriate formatting. It makes use of
Bear's x-callback-url API for this purpose.

*Note: Due to current restrictions in Bear's API and the sandboxed nature of Mac apps, the package cannot automatically
import images into the note.*

## Install

`pip install nb2bear`

## How to use

### As a library

```
from nb2bear import convert_nb_to_bear
nb_file_path: str = "./assets/demo.ipynb"
bear_api_token: str = "D11B63-D71E64-DE9400"
convert_nb_to_bear(nb_file_path, bear_api_token)
```
