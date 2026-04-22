# Nix Deployment

This repository now exposes a NixOS module at `nixosModules.capstone-compose`.

What it does:
- enables Docker on the host
- declares a `capstoneCompose.service` systemd unit
- deploys the production stack from `docker-compose.yml` and `docker-compose.prod.yml`
- makes NixOS the deployment entrypoint instead of repo-local shell scripts

Minimal example:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    capstone.url = "path:/srv/Capstone";
  };

  outputs = { nixpkgs, capstone, ... }: {
    nixosConfigurations.home-server = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        capstone.nixosModules.default
        {
          services.capstoneCompose = {
            enable = true;
            environmentFile = "/var/lib/secrets/capstone.env";
          };
        }
      ];
    };
  };
}
```

The environment file should contain the keys from `.env.prod.example`.

Deploy changes with your normal NixOS workflow, for example `nixos-rebuild switch --flake .#home-server`.
Refresh the app containers without a full rebuild of the machine config with `systemctl reload capstoneCompose`.

Notes:
- The production override now persists backend-uploaded images in a Docker volume instead of bind-mounting the repo checkout.
- The Cloudflare quick tunnel is behind the Compose `tunnel` profile. Enable it with `services.capstoneCompose.profiles = [ "tunnel" ];` if you want the tunnel container managed by NixOS as part of deployment.
- For a fully declarative public URL, prefer a named tunnel or another stable reverse proxy hostname.
