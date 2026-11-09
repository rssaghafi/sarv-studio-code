import React, {useEffect, useLayoutEffect, useRef, useState} from 'react';
import {continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {WindSpec} from './types';
// Procedural wind (kit v0.4, WX): a smooth displacement field warps cloth, hair, plumes and banners of a still or a cut-out layer.
// Inverse mapping on a grid of small cells (no gaps). `calm` rectangles (faces, hands) are held still; `zones` (optional) limit the wind to listed regions.
// Rect = [x0, y0, x1, y1] in 0..1 of the frame. Deterministic: depends only on the frame number.
const smooth = (a: number, b: number, x: number) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const inside = (r: number[], x: number, y: number, feather: number) =>
  Math.min(smooth(r[0] - feather, r[0] + feather, x), smooth(r[2] + feather, r[2] - feather, x), smooth(r[1] - feather, r[1] + feather, y), smooth(r[3] + feather, r[3] - feather, y));
export const windWeight = (w: WindSpec, nx: number, ny: number) => {
  let k = 1;
  if (w.zones && w.zones.length) k = Math.max(...w.zones.map((z) => inside(z, nx, ny, 0.03)));
  for (const c of w.calm ?? []) k *= 1 - inside(c, nx, ny, 0.035);
  return k;
};
export const WindImg: React.FC<{src: string; w: WindSpec}> = ({src, w}) => {
  const ref = useRef<HTMLCanvasElement>(null); const f = useCurrentFrame(); const {fps, width: W, height: VH} = useVideoConfig(); const H = VH > W ? Math.round(W * 9 / 16) : VH;   // Shorts: the 16:9 window is W wide
  const [img, setImg] = useState<HTMLImageElement | null>(null); const [h] = useState(() => delayRender('wind image'));
  useEffect(() => { const i = new Image(); i.onload = () => { setImg(i); continueRender(h); }; i.onerror = () => continueRender(h); i.src = staticFile(src); }, [src, h]);
  useLayoutEffect(() => {
    if (!img || !ref.current) return;
    const ctx = ref.current.getContext('2d'); if (!ctx) return;
    ctx.clearRect(0, 0, W, H);
    const sc = Math.max(W / img.width, H / img.height), sw = W / sc, sh = H / sc, sx = (img.width - sw) / 2, sy = (img.height - sh) / 2;
    const t = f / fps, cell = w.cell ?? 8, amp = (w.amp ?? 7) * (W / 1920), lam = w.lambda ?? 0.22, sp = w.speed ?? 0.45;
    const gust = 0.78 + 0.22 * Math.sin((2 * Math.PI * t) / 3.7 + 1.1);
    for (let y = 0; y < H; y += cell) for (let x = 0; x < W; x += cell) {
      const nx = x / W, ny = y / H, k = windWeight(w, nx, ny);
      if (k < 0.01) { ctx.drawImage(img, sx + x / sc, sy + y / sc, (cell + 1) / sc, (cell + 1) / sc, x, y, cell + 1, cell + 1); continue; }
      const ph = 2 * Math.PI * (t * sp - ny / lam - nx * 0.6);
      const dx = k * amp * gust * (0.65 * Math.sin(ph) + 0.35 * Math.sin(2.3 * ph + 0.9 + nx * 5));
      const dy = k * amp * gust * 0.32 * Math.sin(ph * 0.8 + 2.0 + ny * 6);
      ctx.drawImage(img, sx + (x - dx) / sc, sy + (y - dy) / sc, (cell + 1) / sc, (cell + 1) / sc, x, y, cell + 1, cell + 1);
    }
  }, [img, f, fps, W, H, w]);
  return <canvas ref={ref} width={W} height={H} style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}} />;
};
