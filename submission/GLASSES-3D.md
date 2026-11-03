# Meta Ray-Ban Display 3D illustration

This original procedural model approximates the black Meta Ray-Ban Display for the Ayah Lens editorial video. It is not manufacturer CAD.

The model uses curved, bevelled solid meshes for two rounded trapezoid rims, a raised bridge, thick tapered temples and nose supports. It includes one camera on the viewer's left and one capture indicator opposite. The indicator is a physical opal surface, without animation that implies recording. The right lens has a faint combiner coating. Both lenses remain free of device output or generated words. Logos are omitted.

The geometry was drawn from these official references:

- [Meta launch article](https://about.fb.com/news/2025/09/meta-ray-ban-display-ai-glasses-emg-wristband/).
- [Ray-Ban black product listing](https://www.ray-ban.com/usa/electronics/0HX000001-META%20RAY-BAN%20DISPLAY-Black/815820026709).
- [Meta shop gallery](https://www.meta.com/ai-glasses/meta-ray-ban-display-glasses-and-neural-band/), especially the angled black-frame photograph and front view.

The official gallery images were inspected privately. Their local copies remain ignored under `build/video-v0.2/reference/`. The Ray-Ban page blocked command-line retrieval. Its published product identity was read through the web tool. No source photograph or imported mesh appears in the render.

## Reproduction

Requirements are Python 3 with Pillow, Node.js, Google Chrome at its standard macOS path, FFmpeg and FFprobe. The free JavaScript dependencies live only in the ignored build directory.

```sh
npm install --prefix build/video-v0.2/3d three@0.187.0 puppeteer-core@25.16.0
python3 tools/render_glasses_3d.py --check
python3 tools/render_glasses_3d.py
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames,duration -of json build/video-v0.2/assets/glasses-turntable.mp4
```

The renderer serves assets through a temporary localhost-only HTTP server. Headless Chrome renders the actual perspective scene through WebGL. FFmpeg encodes the resulting 360 frames as H.264, 1920×1080, 30 frames per second and 12 seconds. No external network is used during rendering. No paid service, generation call or purchased model is required.

The smooth looping orbit changes the product's yaw, pitch and roll. A moving key light provides restrained highlights. The frame geometry changes perspective and occludes rear temples through the lenses. The scene uses the exact paper background `#F3EFE5`. The product stays on the right for post-production typography. Add “3D illustration” in post; the asset itself contains no text.

## Checks and receipts

The geometry contract was observed failing before implementation: `AssertionError: Expected two volumetric lens rims`. The implemented check measures the rendered mesh, rather than trusting a declarative part count. It verifies two rims, one camera, one opposite indicator, more than 100 mm of depth, curved surface triangles, projected landmark changes, image changes, background color and framing.

The passing check reported 23 mesh parts, 47,478 triangles and 161.99 mm of transformed depth. The four sampled projected bounds stayed within x785–1890 and y395–797. The frame-90 versus frame-270 pixel difference was 52.531 summed mean RGB levels. These checks establish actual geometry and changing rendered views. They do not establish production dimensional accuracy.

Private review and mesh receipts:

- `build/video-v0.2/3d/full-product.png`: centered standalone product preview.
- `build/video-v0.2/3d/preview-0.png`, `preview-90.png`, `preview-180.png`, `preview-270.png`: editorial keyframes.
- `build/video-v0.2/3d/mesh.json`: exported original scene geometry and materials.
- `build/video-v0.2/3d/receipt.json`: measured mesh counts, projected vertices and landmarks.
- `build/video-v0.2/3d/render.log`: full render output.
- `build/video-v0.2/assets/glasses-turntable.mp4`: integration asset.

The producing subagent inspected the official gallery and all four rendered keyframes. The render visibly contains black solid thickness, clear shaded lenses, changing temple perspective and asymmetric camera hardware. It is an editorial product approximation. The lens contour, hinge clearances, optical combiner, internal electronics and material response are simplified. Millimeter values are modelling units and are not verified product measurements. No fabricated official branding, display output or endorsement is implied.

The final encoded asset passed FFprobe: 1920×1080, `30/1`, `12.000000` seconds and `360` picture frames. All 360 source frames passed a pixel-bounds check, with combined bounds x785–1890 and y395–797. The producing subagent also inspected an encoded frame at 11.8 seconds. The late picture was present and the product remained fully visible. `build/video-v0.2/3d/frame-contract.json` records the all-frame check.
