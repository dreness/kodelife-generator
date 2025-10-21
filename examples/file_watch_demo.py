"""
File Watching Demo

This example demonstrates how to create a KodeLife project that watches
external shader files for changes. This allows you to use external IDEs
and enables live reloading for quick iteration.

The project will reference external .fs and .vs files and automatically
reload them when they change.
"""

from pathlib import Path

from klproj import (
    KodeProjBuilder,
    PassType,
    RenderPass,
    create_default_vertex_stage,
    create_fragment_file_watch_stage,
    create_shadertoy_params,
)


def main():
    """Create a file-watching KodeLife project."""
    # Define paths to shader files (these should exist)
    # You can create these files in the same directory
    current_dir = Path(__file__).parent
    fragment_path = str(current_dir / "plasma.fs")

    # For this example, we'll use the default embedded vertex shader
    # But you can uncomment the line below to watch a custom vertex shader:
    # vertex_path = str(current_dir / "custom.vs")

    print("Creating file-watching project...")
    print(f"Fragment shader: {fragment_path}")

    # Create the builder
    builder = KodeProjBuilder(api="GL3")
    builder.set_resolution(1280, 720)
    builder.set_author("File Watch Demo")
    builder.set_comment("Demo of file watching for live shader development")

    # Add standard Shadertoy parameters
    # These provide iTime, iResolution, iMouse, etc.
    for param in create_shadertoy_params():
        builder.add_global_param(param)

    # Create shader stages
    # Option 1: Use default embedded vertex shader (no file watching)
    vertex_stage = create_default_vertex_stage()

    # Option 2: Watch a custom vertex shader file (uncomment if you have one)
    # vertex_stage = create_vertex_file_watch_stage(vertex_path)

    # Create fragment stage that watches the external file
    fragment_stage = create_fragment_file_watch_stage(fragment_path)

    # Create render pass with both stages
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Main Pass",
        enabled=1,
        stages=[vertex_stage, fragment_stage],
        width=1280,
        height=720,
    )

    builder.add_pass(render_pass)

    # Save the project
    output_path = str(current_dir / "plasma_watch.klproj")
    builder.save(output_path)

    print(f"✓ Created: {output_path}")
    print()
    print("Usage:")
    print("1. Open plasma_watch.klproj in KodeLife")
    print("2. Edit plasma.fs in your favorite IDE")
    print("3. Save the file - KodeLife will automatically reload it!")
    print()
    print("Tips:")
    print("- KodeLife watches the absolute path to the shader file")
    print("- You can move the .klproj file, but keep the shader file in place")
    print("- Use this for rapid iteration and external editor workflows")


if __name__ == "__main__":
    main()
