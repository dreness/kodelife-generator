"""
Test file watching with simplest possible shader.
"""

from pathlib import Path

from klproj import (
    KodeProjBuilder,
    PassType,
    RenderPass,
    create_default_vertex_stage,
    create_fragment_file_watch_stage,
)


def main():
    # Get absolute path to red.fs
    current_dir = Path(__file__).parent
    red_fs_path = str(current_dir / "red.fs")

    builder = KodeProjBuilder(api="GL3")
    builder.set_resolution(1280, 720)
    builder.set_author("File Watch Test")

    # Create stages
    vertex_stage = create_default_vertex_stage()
    fragment_stage = create_fragment_file_watch_stage(red_fs_path)

    # Create render pass
    render_pass = RenderPass(
        pass_type=PassType.RENDER,
        label="Test",
        enabled=1,
        stages=[vertex_stage, fragment_stage],
        width=1280,
        height=720,
    )

    builder.add_pass(render_pass)
    builder.save("red_watch.klproj")
    print("✓ Created: red_watch.klproj")
    print(f"  Watching: {red_fs_path}")


if __name__ == "__main__":
    main()
