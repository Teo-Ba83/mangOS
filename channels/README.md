# Release channels

- **beta**: every build. Macs with "Receive beta versions" on (Settings >
  Software Update) install each build.
- **stable**: only the build written in `stable-build`. All other Macs get it.

To make a build stable, change the number in `stable-build` (on GitHub: open
the file, pencil icon, change the number, "Commit changes"), or run
Actions > "Promote a build to stable". The build's own files, already signed,
become the stable release: nothing is rebuilt. Only the newest builds are
kept, so promote within a few builds.
