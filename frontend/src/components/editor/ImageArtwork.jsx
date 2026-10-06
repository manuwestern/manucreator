import { useId } from 'react';

export const ImageArtwork = ({ object: o, preview = false }) => {
  const id = useId().replace(/[^a-zA-Z0-9]/g, '');
  const filterId = `wood-engraving-${id}`;
  const engraved = preview || o.imageView !== 'original';
  const source = engraved && o.backgroundRemoved ? o.cutoutSrc : o.src;
  if (!source) return null;
  return <>
    <defs>
      <filter id={filterId} x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB" data-testid={`${preview ? 'preview-' : ''}engraving-filter-${o.id}`}>
        <feComponentTransfer in="SourceGraphic" result="contrast"><feFuncR type="linear" slope="1.15" intercept="-0.075" /><feFuncG type="linear" slope="1.15" intercept="-0.075" /><feFuncB type="linear" slope="1.15" intercept="-0.075" /></feComponentTransfer>
        {/* Photo luminance becomes burn density, not opaque sepia paint. White reveals the wood. */}
        <feColorMatrix in="contrast" type="matrix" values="0 0 0 0 0.37647  0 0 0 0 0.21569  0 0 0 0 0.08235  -0.2126 -0.7152 -0.0722 0 1" result="burn" />
        <feComponentTransfer in="burn" result="toned"><feFuncA type="gamma" amplitude="0.96" exponent="0.85" offset="0" /></feComponentTransfer>
        <feComposite in="toned" in2="SourceGraphic" operator="in" />
      </filter>
    </defs>
    <image href={source} x="-85" y="-85" width="170" height="170" preserveAspectRatio="xMidYMid meet" filter={engraved ? `url(#${filterId})` : undefined} data-testid={`${preview ? 'preview-' : ''}image-artwork-${o.id}`} data-image-mode={engraved ? 'engraving' : 'original'} data-background-removed={engraved && !!o.backgroundRemoved} />
  </>;
};