import React from 'react';
import {AbsoluteFill, Easing, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Dust} from './Dust';
import {WindImg} from './Wind';
import type {ShotSpec} from './types';
// Camera kit v0.4 (STUDIO v1.2 §5; v0.4 adds procedural wind): one eased move per shot, laid over a still or a locked-camera clip. EVERY shot carries a move.
// Caps: push ≤1.10 on shots ≤6 s, ≤1.15 on longer holds; speaker ≤1.25 (2K source); drift 1.02→1.05 with ≤±5 px; pan overscan 1.08 with ±3% travel; parallax relative offset ≤14 px.
// Shorts (9:16) show the COMPLETE 16:9 frame in the middle of a lapis canvas (DIR-01 B): nothing is cropped, bands above/below carry captions.
const ease = Easing.inOut(Easing.sin);
const Media: React.FC<{src: string}> = ({src}) => {
  const style: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover'};
  return /\.(mp4|mov|webm)$/i.test(src) ? <OffthreadVideo src={staticFile(src)} muted style={style} /> : <Img src={staticFile(src)} style={style} />;
};
export const Shot: React.FC<{s: ShotSpec}> = ({s}) => {
  const f = useCurrentFrame();
  const {durationInFrames: D, width: W, height: H} = useVideoConfig();
  const t = interpolate(f, [0, Math.max(1, D - 1)], [0, 1], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const vertical = H > W; const move = s.move ?? 'none'; const dir = s.dir ?? 1;
  const pushMax = s.dur <= 6 ? 1.10 : 1.15;
  let bg: React.CSSProperties = {};
  if (move === 'push') bg = {scale: String(interpolate(t, [0, 1], [1.0, pushMax]))};
  if (move === 'pull') bg = {scale: String(interpolate(t, [0, 1], [pushMax, 1.0]))};   // v0.5 (Nov 3): pull-out, e.g. EP2 S07-05; rebuilt in the shared engine from the EP2 cloud-only patch
  if (move === 'pan-l' || move === 'pan-r') {
    const d = move === 'pan-l' ? 1 : -1;
    bg = {scale: '1.08', translate: `${interpolate(t, [0, 1], [3 * d, -3 * d])}% 0`};
  }
  if (move === 'parallax') bg = {scale: String(1.05 + 0.04 * t), translate: `${dir * -18 * t}px 0`};
  if (move === 'speaker') { const [fx, fy] = s.focus ?? [0.5, 0.42]; bg = {transformOrigin: `${fx * 100}% ${fy * 100}%`, scale: String(interpolate(t, [0, 1], [1.0, 1.25]))}; }
  if (move === 'drift') bg = {scale: String(interpolate(t, [0, 1], [1.02, 1.05])), translate: `${dir * interpolate(t, [0, 1], [-5, 5])}px ${interpolate(t, [0, 1], [2.5, -2.5])}px`};
  // 16:9 window: full canvas on the master; centred full-width band-less window on 9:16
  const fh = vertical ? Math.round(W * 9 / 16) : H;
  const frame: React.CSSProperties = vertical ? {position: 'absolute', left: 0, right: 0, top: Math.round((H - fh) / 2), height: fh, overflow: 'hidden'} : {position: 'absolute', inset: 0, overflow: 'hidden'};
  return (
    <AbsoluteFill style={{backgroundColor: '#1E2E51', overflow: 'hidden'}}>
      <div style={frame}>
        <AbsoluteFill style={bg}>{s.src && (s.wind && !s.fg ? <WindImg src={s.src} w={s.wind} /> : <Media src={s.src} />)}{s.fg && s.wind && move !== 'parallax' && <WindImg src={s.fg} w={s.wind} />}</AbsoluteFill>
        {move === 'parallax' && s.fg && (
          <AbsoluteFill style={{scale: String(1.05 + 0.055 * t), translate: `${dir * -30 * t}px 0`}}>
            {s.wind ? <WindImg src={s.fg} w={s.wind} /> : <Img src={staticFile(s.fg)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}
          </AbsoluteFill>
        )}
        {s.dust && <Dust seed={s.id} n={44} />}
      </div>
      {vertical && (<>
        <div style={{position: 'absolute', left: 0, right: 0, top: Math.round((H - fh) / 2) - 2, height: 3, background: '#C9973F'}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: Math.round((H - fh) / 2) + fh - 1, height: 3, background: '#C9973F'}} />
      </>)}
    </AbsoluteFill>
  );
};
