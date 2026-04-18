# Installation

## PyPI

```bash
pip install kongming-rs-hv
```

## Supported Platforms

| Platform | Architectures | Python Versions |
|----------|--------------|-----------------|
| Linux | x86_64 | 3.10–3.14 |
| macOS | Apple Silicon & Intel | 3.10–3.14 |
| Windows | x86_64 | 3.10–3.14 |

## Verifying Installation

```python
import kongming
print(kongming.__version__)  # e.g. should be "3.6.5", as of Apr. 2026. Yours should be newer. 

from kongming import hv
print(hv.MODEL_64K_8BIT)  # should print 1
```

## Import Paths

The package exposes two main modules:

```python
from kongming import hv       # hypervector operations
from kongming import memory   # storage and selectors
```

Model constants are available directly on `hv`:

```python
hv.MODEL_64K_8BIT      # 1
hv.MODEL_1M_10BIT      # 2
hv.MODEL_16M_12BIT     # 3
hv.MODEL_256M_14BIT    # 4
hv.MODEL_4G_16BIT      # 5
```

## Docker

If you'd rather not install anything on your host, you can run `kongming-rs-hv`
inside a container. This works on any system with Docker — no Python, no
virtualenv, no wheel compatibility to worry about.

### One-liner: throwaway Python REPL

Drop straight into a Python shell with the package preinstalled:

```bash
docker run --rm -it --platform=linux/amd64 python:3.12-slim sh -c "\
    pip install --quiet --root-user-action=ignore \
        --disable-pip-version-check kongming-rs-hv && python"
```

`--rm` removes the container on exit. Nothing is persisted. Re-running reinstalls
from PyPI, which takes a few seconds. The `--root-user-action=ignore` and
`--disable-pip-version-check` flags silence pip's root-user and upgrade notices,
which are harmless inside a throwaway container.

`--platform=linux/amd64` is pinned because today we only publish a
`manylinux_x86_64` wheel. On Apple Silicon this runs under Rosetta emulation
(functional but slower than native). A native `linux_aarch64` wheel is on the
roadmap — once published, you can drop the `--platform` flag.

### Reusable image

For repeat use, build a small image once:

```dockerfile
# Dockerfile
FROM python:3.12-slim
RUN pip install --no-cache-dir --disable-pip-version-check kongming-rs-hv
CMD ["python"]
```

```bash
docker build -t kongming-hv .
docker run --rm -it kongming-hv
```

To run a script from the host instead of an interactive REPL, mount the current
directory:

```bash
docker run --rm -v "$PWD":/work -w /work kongming-hv python my_script.py
```

### JupyterLab in a container

For interactive exploration with notebooks:

```dockerfile
# Dockerfile.jupyter
FROM python:3.12-slim
RUN pip install --no-cache-dir --disable-pip-version-check \
    kongming-rs-hv jupyterlab
WORKDIR /notebooks
EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", \
     "--ServerApp.token=''", "--ServerApp.password=''"]
```

```bash
docker build -f Dockerfile.jupyter -t kongming-hv-jupyter .
docker run --rm -p 8888:8888 -v "$PWD":/notebooks kongming-hv-jupyter
```

Open <http://localhost:8888> in your browser. Notebooks saved under `/notebooks`
are persisted to the mounted host directory.

> The disabled token/password above is fine for local use. Do not expose this
> container on a public network without adding authentication.
