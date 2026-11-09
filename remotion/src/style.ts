import {loadFont} from '@remotion/fonts';
import f500 from './fonts/cormorant-garamond-latin-500-normal.woff2';
import f600 from './fonts/cormorant-garamond-latin-600-normal.woff2';
import f700 from './fonts/cormorant-garamond-latin-700-normal.woff2';
import f500i from './fonts/cormorant-garamond-latin-500-italic.woff2';
export const SERIF = 'Cormorant Garamond';
loadFont({family: SERIF, url: f500, weight: '500'});
loadFont({family: SERIF, url: f600, weight: '600'});
loadFont({family: SERIF, url: f700, weight: '700'});
loadFont({family: SERIF, url: f500i, weight: '500', style: 'italic'});
// Palette from 01_bible/style/palette.json
export const C = {gold: '#EBB96D', ochre: '#A9743C', umber: '#5D3D1F', cream: '#E5CFB9', lapis: '#223560', lapisDeep: '#1E2E51',
  turquoise: '#41838E', crimson: '#7A2B19', rose: '#C07E5A', ink: '#2A1C10'};
