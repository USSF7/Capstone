{
  description = "Capstone declarative deployment definitions";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  };

  outputs = { self, nixpkgs }:
    {
      nixosModules.capstone-compose = import ./nix/modules/capstone-compose.nix { inherit self; };
      nixosModules.default = self.nixosModules.capstone-compose;
    };
}
