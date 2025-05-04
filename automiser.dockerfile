# ──────────── 1) Base image ────────────
FROM rocker/verse:4.2.2

# ──────────── 2) System deps + gdebi (for Quarto) ────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 python3-pip git curl \
      libudunits2-dev libgdal-dev libgeos-dev libproj-dev \
      gdebi-core && \
    rm -rf /var/lib/apt/lists/*

# ──────────── 3) Install Quarto CLI ────────────
ARG QUARTO_VERSION="1.0.38"
RUN curl -L \
      https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb \
    -o quarto.deb && \
    gdebi --non-interactive quarto.deb && \
    rm quarto.deb

# Only extra R packages (add zoo for rollmean)
RUN R -e "install.packages(c('plotly','DT','zoo'), repos='https://cran.rstudio.com/')"


# ──────────── 5) Application setup ────────────
WORKDIR /app

# 5a) Python deps first (caching)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 5b) Copy entrypoint + code
COPY entrypoint.sh project-orc-losses.qmd scripts/ docs/ ./

# 5c) Permissions & safe-git
RUN chmod +x entrypoint.sh && \
    git config --global --add safe.directory /app && \
    git config --global --add safe.directory /app/docs

ENTRYPOINT ["./entrypoint.sh"]
