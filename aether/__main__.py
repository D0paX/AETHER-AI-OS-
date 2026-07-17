import argparse
import asyncio
import sys

from aether.core.kernel import AetherKernel
from aether.interfaces.cli import AetherCLI


async def startup(mode: str) -> None:
    kernel = AetherKernel()
    await kernel.boot()

    if mode == "text":
        cli = AetherCLI(kernel)
        try:
            await cli.run()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await kernel.shutdown()
    elif mode == "api":
        import uvicorn

        from aether.interfaces.api import app

        # Attach kernel to app state
        app.state.kernel = kernel

        config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
        server = uvicorn.Server(config)

        try:
            await server.serve()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await kernel.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Aether OS Entry Point")
    parser.add_argument(
        "--mode", choices=["text", "voice", "api"], default="api", help="Operating mode"
    )
    parser.add_argument(
        "--config", type=str, help="Path to config.yaml (optional override)", default=None
    )
    args = parser.parse_args()

    # We could set the config override here if supported by the kernel, but kernel takes config object.
    # We will pass the arguments if needed.

    try:
        asyncio.run(startup(args.mode))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
