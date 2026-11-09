// Props schema for an episode (props.json). Times in seconds.
export type Move = 'none' | 'push' | 'pan-l' | 'pan-r' | 'parallax' | 'speaker' | 'drift' | 'pull';   // v0.3: speaker = push toward focus (cap 1.25), drift = slow breathing move for silences; v0.5: pull = slow pull-out (zoom out), reverse of push
export type Trans = 'cut' | 'dissolve' | 'goldwipe';
export type WindSpec = {amp?: number; lambda?: number; speed?: number; cell?: number; zones?: number[][]; calm?: number[][]};   // v0.4 procedural wind: amp px at 1920 wide; rects [x0,y0,x1,y1] 0..1
export type Label = {tag: 'SOURCE' | 'INTERP' | 'INVENTED' | 'ORDER' | 'OPEN' | 'DEVICE'; text: string; fa?: string; at?: number};   // v0.6: ORDER/OPEN/DEVICE chips; fa = Persian couplet under the text (right-to-left, \n = line break); at = seconds into the card when this row fades in (default 0.6 + 0.7 per row)
export type ShotSpec = {
  id: string;                       // shot ID (S01…), shown in animatic mode
  kind: 'image' | 'video' | 'title' | 'chapter' | 'labels' | 'end';
  src?: string;                     // file in the public dir (image or locked-camera clip)
  src916?: string;                  // DEPRECATED v0.3: Shorts now show the full 16:9 frame in a 9:16 canvas (letterbox); unused
  fg?: string;                      // BiRefNet cut-out for parallax
  dur: number;                      // seconds on screen (before transition overlap)
  move?: Move; dir?: 1 | -1;        // one move per shot (STUDIO §5)
  focus?: [number, number];         // v0.3: speaker move target, 0..1 of the frame (x, y); default [0.5, 0.42]
  wind?: WindSpec;                  // v0.4: procedural wind on fg (if given) else on src (still images only)
  dust?: boolean;                   // gold-dust particles
  text?: string; sub?: string;      // title / chapter / end card text
  logoSize?: number;                // v0.5b: title card logo centred above the wordmark at this px size (1080p); unset = small top-right mark
  logo?: string;                    // v0.5: brand mark (transparent PNG in public): title card top-right, end card centre-left
  veilIn?: number; veilOut?: [number, number]; textIn?: [number, number]; textOut?: [number, number];   // v0.7 (Nov 6, EP2): slow title dissolve; veilOut = [from, to] seconds for the veil to lift to 0 (opening title card that dissolves into the first shot; dust:false recommended). veilIn = seconds for the dimming veil to grow from 0 (picture starts undimmed, so the card dissolves out of the shot before it); textIn / textOut = seconds from the card start for the logo and title to fade in / out. All unset = the v0.6 behaviour (instant veil, text in 0.2 to 1.0 s, out 1.6 to 1.0 s before the end)
  labels?: Label[];                 // closing segment: what the text says / what we changed
  trans?: Trans; transDur?: number; // transition INTO this shot
  line?: string;                    // script line ID(s), animatic overlay
};
export type Clip = {src: string; at: number; trimStart?: number; dur?: number; vol?: number};
export type Caption = {start: number; end: number; text: string};
export type FilmProps = {
  shots: ShotSpec[];
  narration?: Clip[];
  music?: Clip[];
  duckDb?: number;                  // music ducking under voice, 12–15 dB (STUDIO §5)
  captions?: Caption[];
  showCaptions?: boolean;           // burn-in (Shorts: true; master: false, upload SRT instead)
  hook?: string; footer?: string;    // v0.4 Shorts: hook line in the top lapis band, closing line ('Full film on YouTube — link in bio') in the bottom band
  animatic?: boolean;               // shot IDs + timecode + "ANIMATIC" tag
};
