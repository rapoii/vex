---
name: video-production
description: Technical video creation with Manim, Remotion, FFmpeg, and code-driven workflows.
---

# Video Production

Use this skill to plan, script, generate, edit, and ship technical videos with code.

Goal: create clear videos where visuals explain faster than text.

## When to use video

Use video when motion helps:

- Algorithm steps.
- Data structure mutation.
- Math transformations.
- UI interactions.
- Before/after visual comparison.
- Timeline or race condition.
- Architecture flow.
- CLI workflow demonstration.

Do not use video when static docs are better:

- Exact API reference.
- Long command lists.
- Dense tables.
- Copy-paste code.
- Legal/license text.

## Production workflow

1. Define audience and outcome.
2. Write script.
3. Create storyboard.
4. Choose tool.
5. Generate visuals.
6. Record or synthesize audio.
7. Edit with FFmpeg or NLE.
8. Review for accuracy and pacing.
9. Export variants.
10. Publish with metadata.

## Audience and outcome

Start with one sentence:

```text
After watching, viewer can explain how binary search narrows a failing commit range.
```

Good outcomes:

- Viewer can perform task.
- Viewer can understand tradeoff.
- Viewer can identify failure mode.
- Viewer can read output correctly.

Bad outcomes:

- Viewer learns everything about topic.
- Viewer is impressed.
- Viewer sees many features.

## Script

A script controls pacing.

Script sections:

- Hook.
- Setup.
- Visual explanation.
- Example.
- Verification or result.
- Recap.
- Next action.

Keep narration concrete:

```text
Bad: This is a powerful way to understand complex systems.
Good: Each step cuts search space in half, so ten checks can cover about one thousand commits.
```

Timing guide:

- 0-10s: problem and promise.
- 10-30s: setup.
- 30-90s: core explanation.
- 90-150s: realistic example.
- Final 15s: recap and next action.

## Storyboard

Storyboard before coding animation.

For each scene capture:

- Scene goal.
- Visual elements.
- Motion.
- Narration.
- Duration.
- Assets needed.

Storyboard template:

```text
Scene 1
Goal: Show failing test range.
Visual: Commit timeline with red failing end and green passing start.
Motion: Highlight midpoint.
Narration: "Bisect asks one question: does this midpoint pass?"
Duration: 12s
```

## Tool choice

Choose based on visual type.

| Tool | Best for | Avoid for |
| --- | --- | --- |
| Manim | Math, algorithms, graphs, geometric animation | React UI mockups |
| Remotion | React-based motion graphics, UI demos, branded videos | Heavy math layout |
| FFmpeg | Editing, clipping, encoding, overlays, audio muxing | Designing complex scenes alone |
| Browser recorder | Real product walkthroughs | Abstract explanations |
| Slides | Lightweight explainers | Precise animation |

## Manim

Manim is best for mathematical and algorithm animation.

Use for:

- Sorting algorithms.
- Search algorithms.
- Graph traversal.
- Vector/matrix operations.
- State machines.
- Timelines.
- Coordinate systems.
- Data flow diagrams.

### Manim scene pattern

```python
from manim import *

class BinarySearchScene(Scene):
    def construct(self):
        values = VGroup(*[Square().scale(0.4) for _ in range(8)]).arrange(RIGHT)
        labels = VGroup(*[Text(str(i)).scale(0.4).move_to(values[i]) for i in range(8)])
        self.play(Create(values), Write(labels))
        marker = SurroundingRectangle(values[3], color=YELLOW)
        self.play(Create(marker))
        self.wait(1)
```

### Manim practices

- Keep each scene focused.
- Use consistent colors for meaning.
- Animate state changes, not everything.
- Use labels for abstract concepts.
- Leave pauses after important transformations.
- Avoid tiny text.
- Render low quality while iterating.
- Render final quality only after timing is stable.

### Manim command examples

```bash
manim -pql video.py BinarySearchScene
```

```bash
manim -pqh video.py BinarySearchScene
```

Use low quality for preview, high quality for final.

## Remotion

Remotion is best for React-based videos.

Use for:

- UI explainers.
- Product feature videos.
- Code-themed motion graphics.
- Social clips.
- Branded templates.
- Data-driven video variants.

### Remotion component pattern

```tsx
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

export const TitleCard = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20], [0, 1]);

  return (
    <AbsoluteFill style={{background: '#0b1020', color: 'white', justifyContent: 'center', alignItems: 'center'}}>
      <h1 style={{opacity}}>Systematic Debugging</h1>
    </AbsoluteFill>
  );
};
```

### Remotion practices

- Treat video as deterministic React render.
- Use props for data-driven scenes.
- Keep composition dimensions explicit.
- Use frame numbers for precise timing.
- Use reusable scene components.
- Keep fonts and colors consistent.
- Test at target aspect ratio.
- Preview before rendering.

### Remotion command examples

```bash
npx remotion preview
```

```bash
npx remotion render src/index.ts Root output.mp4
```

## FFmpeg

FFmpeg is best for editing, encoding, and automation.

Use for:

- Trim clips.
- Concatenate segments.
- Add audio.
- Add subtitles.
- Resize or crop.
- Convert formats.
- Extract frames.
- Normalize audio.
- Create GIF previews.

### FFmpeg commands

Trim without re-encoding when possible:

```bash
ffmpeg -ss 00:00:05 -to 00:00:20 -i input.mp4 -c copy clip.mp4
```

Render web-friendly MP4:

```bash
ffmpeg -i input.mov -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -c:a aac output.mp4
```

Add audio to video:

```bash
ffmpeg -i video.mp4 -i narration.wav -c:v copy -c:a aac -shortest output.mp4
```

Create GIF preview:

```bash
ffmpeg -i input.mp4 -vf "fps=12,scale=800:-1:flags=lanczos" preview.gif
```

Burn subtitles:

```bash
ffmpeg -i input.mp4 -vf subtitles=captions.srt output.mp4
```

### FFmpeg practices

- Keep source exports lossless or high quality.
- Use yuv420p for broad MP4 compatibility.
- Preserve original files.
- Script repeatable edits.
- Name intermediate files clearly.
- Check audio sync after muxing.
- Export small preview before final.

## Visual design

Clarity beats decoration.

Rules:

- One idea per scene.
- Consistent color meaning.
- Large readable text.
- High contrast.
- Limited motion.
- Motion must reveal relationship.
- Leave whitespace.
- Avoid flashing.
- Avoid unnecessary camera movement.

Color example:

- Green: passing or valid.
- Red: failing or invalid.
- Yellow: current focus.
- Blue: neutral data.
- Gray: inactive.

## Code visuals

When showing code:

- Use large font.
- Highlight few lines.
- Avoid full files.
- Animate diff or focus box.
- Use real code if possible.
- Keep syntax highlighting readable.
- Pause after showing important line.

Do not show terminal output too fast. Viewers cannot skim video like text.

## Audio

Good audio matters more than perfect animation.

Audio checklist:

- Clear narration.
- No clipping.
- Consistent volume.
- Noise reduced.
- Pauses after complex ideas.
- Music low or absent for technical content.
- Captions available.

Narration style:

- Short sentences.
- Concrete terms.
- Match visual timing.
- Do not read code line by line unless teaching syntax.

## Captions

Captions improve accessibility and search.

Caption rules:

- Use accurate text.
- Break lines naturally.
- Keep timing readable.
- Include important spoken terms.
- Do not caption background music unless relevant.

SRT example:

```text
1
00:00:00,000 --> 00:00:03,000
A reliable repro turns debugging from guessing into measurement.
```

## Review checklist

Before publishing:

- Technical claims verified.
- Code examples current.
- Visuals match narration.
- Text readable on mobile.
- Audio clear.
- Captions present if public.
- No secrets or private data visible.
- Commands safe.
- License for assets and music compatible.
- Export plays in target platform.

## Export settings

Common targets:

### YouTube

- 1920x1080 or 3840x2160.
- MP4 H.264.
- AAC audio.
- Thumbnail 1280x720.
- Captions uploaded.

### Social clip

- 1080x1920 vertical or 1080x1080 square.
- Short hook in first 2 seconds.
- Captions burned or uploaded.
- Large text.

### Docs embed

- Short loop if possible.
- MP4 plus GIF fallback if needed.
- Keep file size reasonable.
- Add text alternative.

## Publishing metadata

Include:

- Title.
- Description.
- Chapters if long.
- Links to docs or code.
- Captions.
- Thumbnail.
- Tags or keywords.
- License/attribution if assets used.

Title examples:

```text
Root-Cause Debugging in Four Phases
```

```text
Animating Binary Search with Manim
```

## Common mistakes

Avoid:

- Animating without storyboard.
- Showing unreadable code.
- Using motion that does not teach.
- Recording low-quality audio.
- Skipping captions.
- Exporting only huge files.
- Using copyrighted assets without permission.
- Publishing commands that were not verified.
- Making intro longer than useful content.

## Quick brief

```text
Audience:
Outcome:
Length:
Format:
Tool:
Scenes:
Narration:
Assets:
Export targets:
Review requirements:
```
