import React from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
// Gold-dust particles (from the Oct 17 Parallax component). Deterministic per seed.
export const Dust: React.FC<{seed?: string; n?: number}> = ({seed = 'd', n = 40}) => {
  const f = useCurrentFrame();
  const {width: W, height: H} = useVideoConfig();
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {new Array(n).fill(0).map((_, i) => {
        const x0 = random(`${seed}x${i}`) * W, y0 = random(`${seed}y${i}`) * H, sp = 0.25 + random(`${seed}s${i}`) * 0.6;
        const r = 1.5 + random(`${seed}r${i}`) * 3, ph = random(`${seed}p${i}`) * 6.28;
        const y = (((y0 - f * sp * 2) % H) + H) % H, x = x0 + Math.sin(f / 22 + ph) * 14;
        const tw = 0.35 + 0.45 * (0.5 + 0.5 * Math.sin(f / 9 + ph * 3));
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: r * 2, height: r * 2, borderRadius: '50%',
          background: 'radial-gradient(circle, #fff4c2 0%, #e2b64a 55%, rgba(226,182,74,0) 100%)', opacity: tw * Math.min(1, f / 15)}} />;
      })}
    </AbsoluteFill>
  );
};
