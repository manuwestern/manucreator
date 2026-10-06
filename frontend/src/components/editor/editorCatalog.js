import { Type, Heart, Leaf, Image, Minus, Circle, RectangleHorizontal, Triangle, Star } from 'lucide-react';

export const SHAPES = [
  { type: 'line', label: 'Linie', icon: Minus, widthMm: 90, heightMm: 0 },
  { type: 'circle', label: 'Kreis', icon: Circle, widthMm: 60, heightMm: 60 },
  { type: 'rectangle', label: 'Rechteck', icon: RectangleHorizontal, widthMm: 80, heightMm: 50 },
  { type: 'triangle', label: 'Dreieck', icon: Triangle, widthMm: 70, heightMm: 60 },
  { type: 'star', label: 'Stern', icon: Star, widthMm: 65, heightMm: 65 },
];
export const OBJECT_ICONS = { text: Type, heart: Heart, branch: Leaf, image: Image, ...Object.fromEntries(SHAPES.map(s => [s.type, s.icon])) };
export const isShape = o => SHAPES.some(s => s.type === o?.type);
export const MM_TO_UNITS = 600 / 220;
export const FONTS = [
  { name: 'Cormorant Garamond', category: 'Klassisch', weight: 600 },
  { name: 'Roboto', category: 'Klar', weight: 400 },
  { name: 'Open Sans', category: 'Klar', weight: 400 },
  { name: 'Lato', category: 'Klar', weight: 400 },
  { name: 'Montserrat', category: 'Klar', weight: 400 },
  { name: 'Poppins', category: 'Klar', weight: 400 },
  { name: 'DM Sans', category: 'Klar', weight: 400 },
  { name: 'Oswald', category: 'Klar', weight: 400 },
  { name: 'Playfair Display', category: 'Klassisch', weight: 400 },
  { name: 'Merriweather', category: 'Klassisch', weight: 400 },
  { name: 'Dancing Script', category: 'Handschrift', weight: 400 },
  { name: 'Caveat', category: 'Handschrift', weight: 400 },
  { name: 'Pacifico', category: 'Handschrift', weight: 400 },
  { name: 'Italianno', category: 'Handschrift', weight: 400 },
  { name: 'Georgia', category: 'Klassisch', weight: 400 },
];
export const fontSlug = name => name.toLowerCase().replaceAll(' ', '-');
export const fontWeight = name => FONTS.find(f => f.name === name)?.weight || 400;
export const normalizeRotation = angle => ((angle + 180) % 360 + 360) % 360 - 180;
export function shapeDefaults(type) {
  const shape = SHAPES.find(s => s.type === type);
  return shape ? { widthMm: shape.widthMm, heightMm: shape.heightMm, strokeWidthMm: 1, filled: false, lockAspect: true } : {};
}