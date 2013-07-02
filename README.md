A Flask app to list duplicate files.

Copy settings.yaml.example to settings.yaml. Then edit it and set the "path", to, say, where your NAS device is mounted.

By default, it will list files with the same sizes. Specify "?checksum" in the URL to list files with the same sizes and checksums.
