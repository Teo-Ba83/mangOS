# MangOS updates

## How it works

1. Every change pushed to this repository is built by GitHub Actions
   (`.github/workflows/build-iso.yml`). The build produces:
   - the ISO, for new installations;
   - `mangos-system.deb`: everything that makes the system MangOS (themes,
     settings, tools, Wi-Fi setup, the updater itself). It also depends on
     the Debian packages of the image, so an update can add new programs.
2. The build signs `mangos-system.deb` with **Sigstore** (keyless): the
   signature proves the file was produced by `build-iso.yml` in
   `Teo-Ba83/mangOS`. No private key has to be stored anywhere.
3. Before publishing, the build checks that the updater accepts the signed
   package and **refuses** a tampered copy.
4. ISO and update are published as the only release of the public
   repository `Teo-Ba83/mangos-updates`; older builds are deleted.
5. On every installed MangOS, `mangos-updater.timer` looks for a newer
   version 15 minutes after start-up and then every 6 hours. If there is
   one, it downloads it, verifies the signature, installs it with apt and
   shows a notification. *Settings > Software Update* checks right away.

Debian's own security updates keep coming from Debian
(`unattended-upgrades`), as before.

Turn automatic installation off with `MANGOS_AUTO_UPDATE=no` in
`/etc/mangos/updates.conf` (Software Update still works by hand). The
updater log is in `journalctl -u mangos-updater`, the history in
`/var/lib/mangos/updater/history`.

Note: Sigstore records every signature in a public transparency log
(Rekor). The record shows the repository name `Teo-Ba83/mangOS`, the
workflow and the commit, but not the code.

## One-time setup (about 5 minutes, in the browser)

1. **Create the public repository.** github.com > *New repository* >
   name `mangos-updates`, **Public**, tick **Add a README file** (releases
   need at least one commit) > *Create repository*.
2. **Create a token for it.** Profile picture > *Settings* > *Developer
   settings* > *Personal access tokens* > *Fine-grained tokens* >
   *Generate new token*:
   - Token name: `mangos-updates publisher`; Expiration: up to 1 year
     (renew it before it expires, otherwise builds go back to step 4 below);
   - Repository access: *Only select repositories* > `mangos-updates`;
   - Permissions > Repository permissions > **Contents: Read and write**;
   - *Generate token* and copy it (it is shown only once).
3. **Give it to the build.** Repository `mangOS` > *Settings* > *Secrets
   and variables* > *Actions* > *New repository secret*: name
   `MANGOS_UPDATES_TOKEN`, value: the token > *Add secret*.
4. Start a build (or let the next change start it). From then on ISO and
   updates appear in `https://github.com/Teo-Ba83/mangos-updates/releases`
   and the private repository keeps no releases.

Until the secret exists, builds are published as a release of the private
repository (also keeping only the latest one); installed systems cannot
download from there, so automatic updates start once the setup is done.
