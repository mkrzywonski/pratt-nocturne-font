{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [ pkgs.harfbuzz pkgs.opentype-sanitizer pkgs.fontconfig (pkgs.python3.withPackages (ps: with ps; [ fonttools pillow shapely brotli reportlab ])) ];
}
