FROM rocker/verse:4.2.2

# system deps + gdebi  
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3 python3-pip git curl \
      libudunits2-dev libgdal-dev libgeos-dev libproj-dev \
      gdebi-core && \
    rm -rf /var/lib/apt/lists/*

# install Quarto CLI  
ARG QUARTO_VERSION="1.0.38"
RUN curl -L \
      https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb \
    -o quarto.deb && \
    gdebi --non-interactive quarto.deb && \
    rm quarto.deb

# extra R packages  
RUN R -e "install.packages(c('plotly','DT','zoo'), repos='https://cran.rstudio.com/')"

WORKDIR /app

# Python deps  
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# your app code
COPY entrypoint.sh scripts/ docs/ ./

# mark safe for git and make entrypoint executable
RUN chmod +x entrypoint.sh && \
    git config --global --add safe.directory /app && \
    git config --global --add safe.directory /app/docs

ENTRYPOINT ["./entrypoint.sh"]
