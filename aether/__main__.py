import sys
import asyncio
import uvicorn
import argparse

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
        # Launching FastAPI via code (for internal testing/dev if needed), 
        # though standard way might be just running uvicorn directly.
        # But per requirements, the __main__.py starts the CLI. 
        # Wait, the requirements say "--mode text|voice (default: text)".
        # It doesn't explicitly say --mode api, but the text mode is the CLI.
        # FastAPI might run in background or alongside?
        # Actually the prompt says: "Implement internal FastAPI server... 
        # entry point python -m aether ... parses CLI args --mode text|voice... 
        # Initialize kernel, await kernel.initialize(), cli = AetherCLI(kernel), await cli.run()"
        pass

def main() -> None:
    parser = argparse.ArgumentParser(description="Aether OS Entry Point")
    parser.add_argument("--mode", choices=["text", "voice"], default="text", help="Operating mode")
    parser.add_argument("--config", type=str, help="Path to config.yaml (optional override)", default=None)
    args = parser.parse_args()

    # We could set the config override here if supported by the kernel, but kernel takes config object.
    # We will pass the arguments if needed.

    try:
        asyncio.run(startup(args.mode))
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
