# Godot Docker Builds

## Exporting
Before running this, you will need to install docker. You will also need to have an export configuration named "HTML5" with threads enabled.

    TAG='wasm-threads-release-3.2.4' PRJ_DIR='[[Your Godot Project Directory]]' OUT_DIR='[[Output Directory]]' docker-compose run --service-ports builder

After running this, you can view your app locally at `http://localhost:8080`. The exported project will also be in `[[Output Directory]]`. To actually serve it, you need to send these 2 headers from your webserver:

    Cross-Origin-Opener-Policy: same-origin
    Cross-Origin-Embedder-Policy: require-corp

## Building

    TO_BUILD='wasm-threads-release-3.2.4' ./build.py