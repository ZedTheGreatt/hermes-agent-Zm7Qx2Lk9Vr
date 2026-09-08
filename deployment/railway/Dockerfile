FROM nixos/nix

RUN nix-env -iA nixpkgs.python312 nixpkgs.git nixpkgs.openssl

WORKDIR /app

COPY . .

RUN pip install -e .

ENV SUPABASE_ENABLED=true
ENV SUPABASE_MEMORY_ENABLED=true
ENV SUPABASE_VECTOR_ENABLED=true
ENV HERMES_HOME=/data/.hermes

CMD ["python", "cli.py"]
