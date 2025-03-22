#!/usr/bin/env python3
"""
Serverless Deployer CLI - Main entry point
"""
import os
import click
from rich.console import Console
from rich.panel import Panel

from .config import load_config, save_config, init_config
from .utils.logger import setup_logger
from .aws.deploy import deploy as aws_deploy
from .vercel.deploy import deploy as vercel_deploy

console = Console()
logger = setup_logger()

PROVIDERS = {
    "aws": aws_deploy,
    "vercel": vercel_deploy,
}

@click.group()
@click.version_option()
def cli():
    """Serverless Deployer - Simplify your serverless deployments."""
    pass


@cli.command()
@click.option("--name", prompt="Project name", help="Name of your serverless project")
@click.option(
    "--provider",
    type=click.Choice(["aws", "vercel"]),
    prompt="Default provider",
    help="Default deployment provider",
)
def init(name, provider):
    """Initialize a new serverless project with configuration."""
    if os.path.exists("serverless.yml"):
        if not click.confirm("serverless.yml already exists. Overwrite?"):
            click.echo("Aborted.")
            return

    config = init_config(name, provider)
    save_config(config)
    
    console.print(
        Panel.fit(
            f"✅ Initialized serverless project: [bold]{name}[/bold]",
            title="Success",
            border_style="green",
        )
    )
    console.print("\nNext steps:")
    console.print("  1. Edit [bold]serverless.yml[/bold] to configure your functions")
    console.print("  2. Run [bold]serverless-deployer deploy[/bold] to deploy your functions")


@cli.command()
@click.option(
    "--provider",
    type=click.Choice(["aws", "vercel"]),
    help="Provider to deploy to (overrides config default)",
)
@click.option(
    "--function", "-f", help="Deploy specific function instead of all functions"
)
@click.option("--env-file", help="Path to .env file for environment variables")
def deploy(provider, function, env_file):
    """Deploy functions to the specified provider."""
    try:
        config = load_config()
        
        # Use provider from command line or fall back to config
        provider = provider or config.get("provider")
        if not provider:
            click.echo("No provider specified and no default in config.")
            return
            
        if provider not in PROVIDERS:
            click.echo(f"Provider {provider} not supported.")
            return
            
        deploy_func = PROVIDERS[provider]
        
        console.print(f"Deploying to [bold]{provider}[/bold]...")
        result = deploy_func(config, function_name=function, env_file=env_file)
        
        if result:
            console.print(
                Panel.fit(
                    "✅ Deployment completed successfully!",
                    title="Success",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel.fit(
                    "❌ Deployment failed. Check logs for details.",
                    title="Error",
                    border_style="red",
                )
            )
    except Exception as e:
        logger.exception("Deployment failed")
        console.print(f"❌ Error: {str(e)}", style="bold red")


@cli.command()
def list():
    """List all configured functions."""
    try:
        config = load_config()
        functions = config.get("functions", [])
        
        if not functions:
            console.print("No functions configured in serverless.yml")
            return
            
        console.print(Panel.fit("Configured Functions", border_style="blue"))
        
        for idx, func in enumerate(functions, 1):
            console.print(f"[bold]{idx}.[/bold] {func['name']}")
            console.print(f"  Path: {func['path']}")
            console.print(f"  Provider: {func.get('provider', config.get('provider', 'not specified'))}")
            if "memory" in func:
                console.print(f"  Memory: {func['memory']}MB")
            if "timeout" in func:
                console.print(f"  Timeout: {func['timeout']}s")
            console.print("")
    except Exception as e:
        logger.exception("Failed to list functions")
        console.print(f"❌ Error: {str(e)}", style="bold red")


@cli.command()
def history():
    """Show deployment history."""
    console.print("Deployment history feature coming soon!")


@cli.command()
@click.option("--deployment-id", required=True, help="ID of the deployment to roll back to")
def rollback(deployment_id):
    """Roll back to a previous deployment."""
    console.print("Rollback feature coming soon!")


if __name__ == "__main__":
    cli() 