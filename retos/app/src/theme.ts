/**
 * Sistema visual.
 *
 * Dos superficies distintas y deliberadamente diferentes:
 * - La del niño: colores cálidos, tipografía grande, áreas táctiles enormes.
 * - La del adulto: sobria, densa, sin ilustración. Que se note al entrar que
 *   se ha cambiado de sitio, para que el niño no crea que es su zona.
 */

export const colors = {
  bg: '#FFF8F0',
  surface: '#FFFFFF',
  ink: '#2A2118',
  inkSoft: '#7A6A58',
  primary: '#F26B3A',
  primaryDark: '#D2521F',
  accent: '#3AA6A0',
  done: '#3F9D57',
  locked: '#C9BFB2',
  border: '#EADFD1',
  // Zona de adultos
  parentBg: '#F4F5F7',
  parentInk: '#1C2530',
  parentBorder: '#DCE1E8',
  danger: '#C0392B',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const radii = {
  sm: 10,
  md: 18,
  lg: 28,
  pill: 999,
} as const;

/** Tamaños pensados para que un adulto lea a un metro y un niño acierte al pulsar. */
export const type = {
  display: { fontSize: 34, fontWeight: '800' as const, lineHeight: 40 },
  title: { fontSize: 26, fontWeight: '800' as const, lineHeight: 32 },
  heading: { fontSize: 20, fontWeight: '700' as const, lineHeight: 26 },
  body: { fontSize: 17, fontWeight: '400' as const, lineHeight: 24 },
  label: { fontSize: 15, fontWeight: '600' as const, lineHeight: 20 },
  caption: { fontSize: 13, fontWeight: '400' as const, lineHeight: 18 },
} as const;

/** Altura mínima de cualquier cosa pulsable en la zona del niño. */
export const TOUCH_MIN = 64;
