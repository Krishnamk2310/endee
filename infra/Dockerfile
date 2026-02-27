# build stage
ARG BASE_IMAGE=debian:13-slim
FROM ${BASE_IMAGE} AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    cmake \
    clang \
    build-essential \
    libssl-dev \
    libcurl4-openssl-dev \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build_space

# copy source
COPY ./src /build_space/src
COPY ./third_party /build_space/third_party
COPY ./CMakeLists.txt /build_space/CMakeLists.txt
COPY ./install.sh /build_space/install.sh

# build server
ARG BUILD_ARCH
ENV BUILD_ARCH=${BUILD_ARCH}
ARG DEBUG=false
ENV DEBUG=${DEBUG}
RUN chmod +x ./install.sh && \
    if [ "$DEBUG" = "true" ]; then \
    ./install.sh --${BUILD_ARCH} --debug_all --skip-deps; \
    else \
    ./install.sh --${BUILD_ARCH} --release --skip-deps; \
    fi && \
    cp ./build/ndd-${BUILD_ARCH} ./ndd-server

# runtime stage
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH=/usr/local/bin:$PATH

# runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    libcurl4 \
    liblmdb0 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# non-root user
RUN groupadd -r -g 1000 endee && \
    useradd -r -u 1000 -g endee -s /bin/false -d /home/endee endee && \
    mkdir -p /data /home/endee && \
    chown -R endee:endee /data /home/endee && \
    chmod 755 /data

# copy binary
COPY --from=builder /build_space/ndd-server /usr/local/bin/ndd-server
RUN chmod +x /usr/local/bin/ndd-server

# copy ui
# COPY --from=builder /build_space/frontend /usr/local/frontend

# set user
USER endee
WORKDIR /home/endee

# env vars
ENV NDD_DATA_DIR=/data \
    NDD_SERVER_PORT=8080 \
    NDD_LOG_LEVEL=info \
    NDD_NUM_THREADS=0

EXPOSE 8080

# health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health || exit 1

LABEL org.opencontainers.image.title="endee-oss"
LABEL org.opencontainers.image.description="Endee Open Source"
LABEL org.opencontainers.image.url="https://endee.io/"
LABEL org.opencontainers.image.documentation="https://docs.endee.io/"
LABEL org.opencontainers.image.vendor="Endee Labs"
# source info
LABEL org.opencontainers.image.source=""


# entrypoint
ENTRYPOINT ["/usr/local/bin/ndd-server"]

CMD []
