{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/basics/
  env.GREET = "devenv";
  env.PYTHONPATH = ".";

  # https://devenv.sh/packages/
  # Install Python packages system-wide or in the virtual environment
  packages = [ 
    pkgs.python3
    pkgs.python3Packages.numpy
    pkgs.python3Packages.gymnasium
    pkgs.python3Packages.matplotlib
  ];

  # https://devenv.sh/scripts/
  scripts.hello.exec = ''
    echo hello from $GREET
  '';

  enterShell = ''
    hello
    git --version
  '';

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

  # See full reference at https://devenv.sh/reference/options/
}