{ self }:
{ config, lib, pkgs, ... }:

let
  cfg = config.services.capstoneCompose;
  composeBin = "${pkgs.docker-compose}/bin/docker-compose";
  composeFiles = [
    "${cfg.source}/docker-compose.yml"
    "${cfg.source}/docker-compose.prod.yml"
  ];
  composeFileArgs = lib.concatStringsSep " " (map (file: "-f ${lib.escapeShellArg file}") composeFiles);
  profileArgs = lib.concatStringsSep " " (map (profile: "--profile ${lib.escapeShellArg profile}") cfg.profiles);
  composeWrapper = pkgs.writeShellScript "capstone-compose" ''
    set -euo pipefail
    export COMPOSE_PROJECT_NAME=${lib.escapeShellArg cfg.projectName}
    exec ${composeBin} ${composeFileArgs} ${profileArgs} --env-file ${lib.escapeShellArg cfg.environmentFile} "$@"
  '';
in
{
  options.services.capstoneCompose = {
    enable = lib.mkEnableOption "Capstone production deployment via Docker Compose";

    source = lib.mkOption {
      type = lib.types.path;
      default = self.outPath;
      defaultText = lib.literalExpression "self.outPath";
      description = ''
        Repository source used as the Docker Compose build context.
      '';
    };

    environmentFile = lib.mkOption {
      type = lib.types.path;
      example = "/var/lib/secrets/capstone.env";
      description = ''
        Environment file passed to Docker Compose. Populate it from `.env.prod.example`
        and keep secrets outside the Nix store.
      '';
    };

    projectName = lib.mkOption {
      type = lib.types.str;
      default = "capstone";
      description = "Docker Compose project name.";
    };

    profiles = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      example = [ "tunnel" ];
      description = ''
        Optional Docker Compose profiles to enable for deployment.
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    virtualisation.docker.enable = true;

    systemd.services.capstoneCompose = {
      description = "Capstone production deployment";
      wantedBy = [ "multi-user.target" ];
      wants = [ "network-online.target" ];
      after = [ "docker.service" "network-online.target" ];
      requires = [ "docker.service" ];
      path = [ pkgs.docker pkgs.docker-compose ];

      serviceConfig = {
        Type = "oneshot";
        RemainAfterExit = true;
        WorkingDirectory = cfg.source;
        ExecStart = "${composeWrapper} up -d --build";
        ExecReload = "${composeWrapper} up -d --build";
        ExecStop = "${composeWrapper} down";
      };
    };
  };
}
