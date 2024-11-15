# Use an official OCaml base image
FROM ocaml/opam:debian-10-ocaml-4.11

# Install necessary packages
RUN sudo apt-get update && sudo apt-get install -y \
    git \
    opam

# Initialize OPAM and switch to the required OCaml version
RUN opam init -y --disable-sandboxing && \
    opam switch create 4.11.1 && \
    eval $(opam env)

# Clone the MonPoly repository
RUN git clone https://bitbucket.org/monpoly/monpoly.git

# Set the working directory
WORKDIR /home/opam/monpoly

# Install dependencies
RUN opam install --deps-only -y .

# Build and install MonPoly
RUN dune build --release && \
    dune install

# Set the entrypoint to monpoly
ENTRYPOINT ["monpoly"]