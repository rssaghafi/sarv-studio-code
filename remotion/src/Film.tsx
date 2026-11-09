import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {Shot} from './Shot';
import {ChapterCard, EndCard, LabelsCard, TitleCard} from './Cards';
import {goldWipe} from './GoldWipe';
import {C, SERIF} from './style';
import type {Caption, FilmProps, ShotSpec} from './types';
export const transFrames = (s: ShotSpec, i: number, fps: number) =>
  i === 0 || !s.trans || s.trans === 'cut' ? 0 : Math.round((s.transDur ?? (s.trans === 'goldwipe' ? 1.0 : 0.8)) * fps);
export const totalFrames = (p: FilmProps, fps: number) =>
  p.shots.reduce((a, s, i) => a + Math.round(s.dur * fps) - transFrames(s, i, fps), 0);
const Body: React.FC<{s: ShotSpec}> = ({s}) =>
  s.kind === 'title' ? <TitleCard s={s} /> : s.kind === 'chapter' ? <ChapterCard s={s} /> :
  s.kind === 'labels' ? <LabelsCard s={s} /> : s.kind === 'end' ? <EndCard s={s} /> : <Shot s={s} />;
// Speech windows (from captions) drive music ducking: −duckDb under voice, 0.3 s ramps.
const speech = (caps: Caption[] = []) => {
  const out: [number, number][] = [];
  [...caps].sort((a, b) => a.start - b.start).forEach((c) => {
    const l = out[out.length - 1]; if (l && c.start - l[1] < 0.6) l[1] = Math.max(l[1], c.end); else out.push([c.start, c.end]);
  });
  return out;
};
const duckGain = (t: number, win: [number, number][], db: number) => {
  const r = 0.3; let g = 0;
  for (const [a, b] of win) g = Math.max(g, Math.min(1, Math.max(0, Math.min((t - (a - r)) / r, ((b + r) - t) / r))));
  return Math.pow(10, (-db * g) / 20);
};
const Captions: React.FC<{caps: Caption[]}> = ({caps}) => {
  const f = useCurrentFrame(); const {fps, width: W, height: H} = useVideoConfig(); const t = f / fps;
  const c = caps.find((x) => t >= x.start && t <= x.end); if (!c) return null;
  const vertical = H > W; const u = Math.min(W, H) / 1080;
  const fh = Math.round(W * 9 / 16);   // v0.5: on 9:16 the caption sits wholly in the lower lapis band, never over the 16:9 picture
  return (<AbsoluteFill style={vertical ? {justifyContent: 'flex-start', alignItems: 'center', paddingTop: Math.round((H + fh) / 2) + 48 * u} : {justifyContent: 'flex-end', alignItems: 'center', paddingBottom: H * 0.06}}>
    <div style={{fontFamily: SERIF, fontWeight: 600, fontSize: (vertical ? 58 : 46) * u, color: '#FFF8EC', textAlign: 'center', maxWidth: W * (vertical ? 0.86 : 0.74),
      lineHeight: 1.18, padding: `${8 * u}px ${22 * u}px`, borderRadius: 10 * u, background: 'rgba(30,46,81,.55)', textShadow: '0 2px 6px rgba(0,0,0,.6)'}}>{c.text}</div>
  </AbsoluteFill>);
};
const Bands: React.FC<{hook?: string; footer?: string}> = ({hook, footer}) => {
  const {width: W, height: H} = useVideoConfig(); if (H <= W) return null;
  const fh = Math.round(W * 9 / 16), band = Math.round((H - fh) / 2);
  const box = (extra: React.CSSProperties): React.CSSProperties => ({position: 'absolute', left: 0, right: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 70px', textAlign: 'center', fontFamily: SERIF, color: '#FFF8EC', ...extra});
  return (<>
    {hook && <div style={box({top: 0, height: band, fontWeight: 700, fontSize: 74, lineHeight: 1.12, textShadow: '0 2px 6px rgba(0,0,0,.45)'})}>{hook}</div>}
    {footer && <div style={box({bottom: 0, height: 150, fontWeight: 600, fontSize: 40, color: '#EBB96D', fontStyle: 'italic'})}>{footer}</div>}
  </>);
};
const AnimaticHud: React.FC<{p: FilmProps}> = ({p}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  let acc = 0, cur = p.shots[0];
  p.shots.forEach((s, i) => { const st = acc - transFrames(s, i, fps); if (f >= st) cur = s; acc = st + Math.round(s.dur * fps); });
  const tc = (x: number) => `${String(Math.floor(x / fps / 60)).padStart(2, '0')}:${String(Math.floor(x / fps) % 60).padStart(2, '0')}:${String(x % fps).padStart(2, '0')}`;
  return (<div style={{position: 'absolute', left: 24, top: 20, fontFamily: 'monospace', fontSize: 26, color: '#fff', background: 'rgba(0,0,0,.55)', padding: '6px 14px', borderRadius: 6}}>
    ANIMATIC · {cur.id}{cur.line ? ` · ${cur.line}` : ''} · {tc(f)}</div>);
};
export const Film: React.FC<FilmProps> = (p) => {
  const {fps} = useVideoConfig(); const win = speech(p.captions); const db = p.duckDb ?? 13;
  return (<AbsoluteFill style={{backgroundColor: C.lapisDeep}}>
    <TransitionSeries>
      {p.shots.map((s, i) => {
        const tf = transFrames(s, i, fps);
        return (<React.Fragment key={s.id}>
          {tf > 0 && <TransitionSeries.Transition presentation={s.trans === 'goldwipe' ? goldWipe() : fade()} timing={linearTiming({durationInFrames: tf})} />}
          <TransitionSeries.Sequence durationInFrames={Math.round(s.dur * fps)} name={s.id}><Body s={s} /></TransitionSeries.Sequence>
        </React.Fragment>);
      })}
    </TransitionSeries>
    {(p.narration ?? []).map((c, i) => (
      <Sequence key={`n${i}`} from={Math.round(c.at * fps)} durationInFrames={c.dur ? Math.round(c.dur * fps) : undefined} name={`VO ${i + 1}`}>
        <Audio src={staticFile(c.src)} startFrom={Math.round((c.trimStart ?? 0) * fps)} volume={c.vol ?? 1} />
      </Sequence>))}
    {(p.music ?? []).map((c, i) => {
      const at = Math.round(c.at * fps);
      return (<Sequence key={`m${i}`} from={at} durationInFrames={c.dur ? Math.round(c.dur * fps) : undefined} name={`Music ${i + 1}`}>
        <Audio src={staticFile(c.src)} startFrom={Math.round((c.trimStart ?? 0) * fps)}
          volume={(fr) => (c.vol ?? 0.8) * duckGain((fr + at) / fps, win, db) * interpolate(fr, [0, fps], [0, 1], {extrapolateRight: 'clamp'})} />
      </Sequence>);
    })}
    {p.showCaptions && p.captions && <Captions caps={p.captions} />}
    <Bands hook={p.hook} footer={p.footer} />
    {p.animatic && <AnimaticHud p={p} />}
  </AbsoluteFill>);
};
