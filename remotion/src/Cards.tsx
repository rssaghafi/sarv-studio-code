import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Shot} from './Shot';
import {C, SERIF} from './style';
import type {ShotSpec} from './types';
// v0.6 (Nov 5, EP2 closing segment): labels card chips ORDER/OPEN/DEVICE, optional `fa` Persian couplet and `at` fade-in time per label row (v0.5b files in ../_to_delete/remotion_v0.5b_src/). v0.5b (Oct 25): title logo centred via logoSize; end card without text = no NEXT line (sub = tagline). v0.5 (Oct 24, G5 finished film): logo on title (top-right brand mark) and end card; labels card sits high (end-screen room) with an optional footer line.
// Title, chapter, closing-labels and end cards. Full-bleed painting underneath, no borders (STUDIO §2).
const fadeIO = (f: number, D: number, fps: number) =>
  interpolate(f, [0.2 * fps, 1.0 * fps, D - 1.6 * fps, D - 1.0 * fps], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
const Veil: React.FC<{a: number}> = ({a}) => (
  <AbsoluteFill style={{background: `radial-gradient(ellipse at center, rgba(22,30,52,${Math.min(0.85, a * 1.25)}) 0%, rgba(22,30,52,${Math.min(0.9, a * 1.1)}) 60%, rgba(22,30,52,${Math.min(0.95, a * 1.3)}) 100%)`}} />
);
const txt: React.CSSProperties = {fontFamily: SERIF, color: C.cream, textAlign: 'center', textShadow: '0 2px 4px rgba(10,8,4,.75), 0 0 28px rgba(10,8,4,.6)'};
export const TitleCard: React.FC<{s: ShotSpec}> = ({s}) => {
  const f = useCurrentFrame(); const {durationInFrames: D, fps, width: W, height: H} = useVideoConfig(); const u = Math.min(W, H) / 1080;
  const ease = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)} as const;
  // v0.7: optional slow dissolve (veilIn, textIn, textOut in seconds from the card start); unset = v0.6 behaviour
  const o = (s.textIn || s.textOut)
    ? interpolate(f, [(s.textIn?.[0] ?? 0.2) * fps, (s.textIn?.[1] ?? 1.0) * fps], [0, 1], ease) * interpolate(f, s.textOut ? [s.textOut[0] * fps, s.textOut[1] * fps] : [D - 1.6 * fps, D - 1.0 * fps], [1, 0], ease)
    : fadeIO(f, D, fps);
  // v0.7 (Nov 6): veilOut = [from, to] seconds for the veil to LIFT to 0 (title as an opening card that dissolves into the first shot); dust defaults to true, set dust:false to switch it off
  const veil = s.veilOut ? 0.45 * (1 - interpolate(f, [s.veilOut[0] * fps, s.veilOut[1] * fps], [0, 1], ease))
    : s.veilIn ? 0.45 * interpolate(f, [0, s.veilIn * fps], [0, 1], ease) : 0.45;
  return (<AbsoluteFill>
    <Shot s={{...s, move: s.move ?? 'push', dust: s.dust ?? true}} /><Veil a={veil} />
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity: o, padding: 80 * u}}>
      {s.logo && s.logoSize && <Img src={staticFile(s.logo)} style={{width: s.logoSize * u, height: s.logoSize * u, marginBottom: 26 * u, filter: 'drop-shadow(0 4px 14px rgba(0,0,0,.5))'}} />}
      <div style={{...txt, fontSize: 38 * u, letterSpacing: '0.42em', color: C.gold, fontWeight: 700}}>SARV &amp; SIMURGH</div>
      <div style={{width: 120 * u, height: 2, background: C.gold, margin: `${22 * u}px 0`, opacity: 0.8}} />
      <div style={{...txt, fontSize: 112 * u, fontWeight: 600, lineHeight: 1.05}}>{s.text}</div>
      {s.sub && <div style={{...txt, fontSize: 40 * u, fontStyle: 'italic', fontWeight: 500, marginTop: 24 * u, color: C.gold}}>{s.sub}</div>}
    </AbsoluteFill>
    {s.logo && !s.logoSize && <Img src={staticFile(s.logo)} style={{position: 'absolute', top: 44 * u, right: 52 * u, width: 132 * u, height: 132 * u, opacity: o, filter: 'drop-shadow(0 3px 10px rgba(0,0,0,.45))'}} />}
  </AbsoluteFill>);
};
export const ChapterCard: React.FC<{s: ShotSpec}> = ({s}) => {
  const f = useCurrentFrame(); const {durationInFrames: D, fps, width: W, height: H} = useVideoConfig(); const u = Math.min(W, H) / 1080;
  const o = fadeIO(f, D, fps);
  return (<AbsoluteFill>
    <Shot s={s} /><Veil a={0.5} />
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity: o}}>
      {s.sub && <div style={{...txt, fontSize: 32 * u, letterSpacing: '0.35em', color: C.gold, fontWeight: 600}}>{s.sub.toUpperCase()}</div>}
      <div style={{...txt, fontSize: 92 * u, fontWeight: 600, marginTop: 16 * u}}>{s.text}</div>
    </AbsoluteFill></AbsoluteFill>);
};
const TAG = {SOURCE: {c: C.turquoise, l: 'From the text'}, INTERP: {c: C.ochre, l: 'Interpretation'}, INVENTED: {c: C.rose, l: 'Our invention'},
  ORDER: {c: '#5F6F9E', l: 'Our order'}, OPEN: {c: C.crimson, l: 'Open question'}, DEVICE: {c: '#7A5C7E', l: 'Our device'}};   // v0.6 (Nov 5): ORDER, OPEN, DEVICE
const FA = "'Noto Naskh Arabic', 'Geeza Pro', 'Al Nile', 'Arial', serif";   // v0.6: system Persian-capable fonts (the bundled Cormorant has no Arabic script)
export const LabelsCard: React.FC<{s: ShotSpec}> = ({s}) => {
  const f = useCurrentFrame(); const {fps, width: W, height: H} = useVideoConfig(); const u = Math.min(W, H) / 1080;
  return (<AbsoluteFill>
    <Shot s={s} /><Veil a={0.62} />
    <AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', padding: `${150 * u}px ${120 * u}px 0`}}>
      {s.text && <div style={{...txt, fontSize: 64 * u, fontWeight: 600, marginBottom: 36 * u}}>{s.text}</div>}
      {(s.labels ?? []).map((lb, i) => {
        const t0 = lb.at ?? 0.6 + i * 0.7;
        const o = interpolate(f, [t0 * fps, (t0 + 0.6) * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (<div key={i} style={{display: 'flex', alignItems: lb.fa ? 'flex-start' : 'center', gap: 22 * u, opacity: o, translate: `0 ${(1 - o) * 12}px`, margin: `${10 * u}px 0`, width: '100%', maxWidth: 1400 * u}}>
          <div style={{fontFamily: SERIF, fontWeight: 700, fontSize: 26 * u, letterSpacing: '0.12em', color: '#fff', background: TAG[lb.tag].c,
            padding: `${6 * u}px ${16 * u}px`, borderRadius: 6 * u, minWidth: 310 * u, textAlign: 'center', whiteSpace: 'nowrap', flexShrink: 0, marginTop: lb.fa ? 8 * u : 0}}>{TAG[lb.tag].l.toUpperCase()}</div>
          <div style={{display: 'flex', flexDirection: 'column', flex: 1}}>
            <div style={{...txt, textAlign: 'left', fontSize: 40 * u, fontWeight: 500}}>{lb.text}</div>
            {lb.fa && <div style={{...txt, fontFamily: FA, direction: 'rtl', textAlign: 'right', whiteSpace: 'pre-line', fontSize: 46 * u, fontWeight: 400, color: C.gold, lineHeight: 1.5, marginTop: 8 * u}}>{lb.fa}</div>}
          </div>
        </div>);
      })}
      {s.sub && <div style={{...txt, fontSize: 32 * u, fontStyle: 'italic', color: C.gold, marginTop: 40 * u,
        opacity: interpolate(f, [(1.0 + (s.labels ?? []).length * 0.7) * fps, (1.6 + (s.labels ?? []).length * 0.7) * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>{s.sub}</div>}
    </AbsoluteFill></AbsoluteFill>);
};
export const EndCard: React.FC<{s: ShotSpec}> = ({s}) => {
  const f = useCurrentFrame(); const {durationInFrames: D, fps, width: W, height: H} = useVideoConfig(); const u = Math.min(W, H) / 1080;
  const o = fadeIO(f, D + 1.0 * fps, fps);
  const side = !!s.logo && W > H;   // 16:9 with logo: content in the left half, right half left free for YouTube end-screen elements
  return (<AbsoluteFill>
    <Shot s={{...s, dust: true}} /><Veil a={0.55} />
    <div style={{position: 'absolute', top: 0, bottom: 0, left: 0, width: side ? W * 0.5 : W, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', opacity: o}}>
      {s.logo && <Img src={staticFile(s.logo)} style={{width: 300 * u, height: 300 * u, marginBottom: 26 * u, filter: 'drop-shadow(0 4px 14px rgba(0,0,0,.5))'}} />}
      {s.logo && <div style={{...txt, fontSize: 40 * u, letterSpacing: '0.38em', color: C.gold, fontWeight: 700, marginBottom: 34 * u}}>SARV &amp; SIMURGH</div>}
      {s.text && <div style={{...txt, fontSize: 30 * u, letterSpacing: '0.35em', color: C.gold, fontWeight: 600}}>NEXT</div>}
      {s.text && <div style={{...txt, fontSize: (s.logo ? 70 : 88) * u, fontWeight: 600, marginTop: 10 * u}}>{s.text}</div>}
      {s.sub && <div style={{...txt, fontSize: (s.text ? 34 : 44) * u, fontStyle: 'italic', marginTop: 16 * u}}>{s.sub}</div>}
    </div></AbsoluteFill>);
};
