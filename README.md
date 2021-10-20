# ds-cookiecutter guide (Kuebiko)

> Kuebiko (久延毘古) is the Shinto kami ("god; deity") of Folk wisdom, knowledge and agriculture, and is represented in Japanese mythology as a scarecrow who cannot walk but has comprehensive awareness.

A "full" (see [Corners cut](docs/guide/index.md#corners-cut)) example [`ds-cookiecutter`](http://nestauk.github.io/ds-cookiecutter/) project broken down into episodes, with annotations/narrative for each episode focusing on a different aspect. In addition, there are a set of reference guides consolidating key concepts and pointing to further resources.

For the guide material [start here (markdown)](docs/guide/index.md) or [here (online docs)](https://nestauk.github.io/kuebiko/), the rest of the README relates to content that would be in this repo if it were a real project and not a guide.

## Setup

- Meet the data science cookiecutter [requirements](http://nestauk.github.io/ds-cookiecutter/quickstart), in brief:
  - Install: `git-crypt`, `direnv`, and `conda`
  - Have a Nesta AWS account configured with `awscli`
- Run `make install` to configure the development environment:
  - Setup the conda environment
  - Configure pre-commit
  - Configure metaflow to use AWS
- Run `make serve-guide-docs` to build and serve documentation locally

---

<small><p>Project based on <a target="_blank" href="https://github.com/nestauk/ds-cookiecutter">Nesta's data science project template</a>
(<a href="http://nestauk.github.io/ds-cookiecutter">Read the docs here</a>).
</small>
