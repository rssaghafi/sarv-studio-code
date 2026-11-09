import React from 'react';
import {Composition} from 'remotion';
import './style';
import {Film, totalFrames} from './Film';
import type {FilmProps} from './types';
// Compositions: Film (16:9 master; animatic when props.animatic=true) and Short (9:16).
// Props come from the episode's props.json (render.sh init … <props.json>). Duration follows the props.
const FPS = 30;
const empty: FilmProps = {shots: [{id: 'S01', kind: 'title', dur: 4, text: 'Sarv & Simurgh'}]};
const meta = ({props}: {props: FilmProps}) => ({durationInFrames: Math.max(1, totalFrames(props, FPS))});
export const Root: React.FC = () => (<>
  <Composition id="Film" component={Film} defaultProps={empty} calculateMetadata={meta} fps={FPS} width={1920} height={1080} durationInFrames={120} />
  <Composition id="Short" component={Film} defaultProps={empty} calculateMetadata={meta} fps={FPS} width={1080} height={1920} durationInFrames={120} />
</>);
