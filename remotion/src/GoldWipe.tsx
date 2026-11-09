import React from 'react';
import type {TransitionPresentation, TransitionPresentationComponentProps} from '@remotion/transitions';
// Gold-leaf wipe: the next shot is revealed left→right behind a soft glowing gold edge.
// Replaces the planned "page-turn" (a page curl would break negative rule N11: no paper, no page curl).
const Comp: React.FC<TransitionPresentationComponentProps<Record<string, never>>> = ({children, presentationDirection, presentationProgress: p}) => {
  if (presentationDirection === 'exiting') return <>{children}</>;
  const x = -15 + p * 130; // edge position in %, overshoots both sides
  const mask = `linear-gradient(100deg, black ${x - 12}%, transparent ${x + 4}%)`;
  return (<div style={{position: 'absolute', inset: 0}}>
    <div style={{position: 'absolute', inset: 0, WebkitMaskImage: mask, maskImage: mask}}>{children}</div>
    <div style={{position: 'absolute', inset: 0, pointerEvents: 'none', opacity: Math.sin(p * Math.PI),
      background: `linear-gradient(100deg, transparent ${x - 9}%, rgba(255,226,150,.55) ${x - 3}%, rgba(235,185,109,.9) ${x - 1}%, transparent ${x + 5}%)`}} />
  </div>);
};
export const goldWipe = (): TransitionPresentation<Record<string, never>> => ({component: Comp, props: {}});
