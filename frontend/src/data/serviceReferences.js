// Only actual supplied images and the existing cover; no duplicate filler slides.
const coverTitles = {
  holz: 'Lebensbaum auf Holz',
  kunststoff: 'Individuelle Gehäusebeschriftung',
  glas: 'Whiskyglas „Good Times“',
  metall: 'Metallschild „Built Different“',
  schiefer: 'Eine Botschaft auf Schiefer',
  textil: 'T-Shirt „Good Ideas Wear Better“',
};

const additionalReferences = {
  holz: [
    { id: 'make-it-real', src: '/images/contact-original.webp', thumbnail: '/images/references/holz-make-it-real-thumb.webp', title: 'Holzblock „Make it Real“', alt: 'Holzblock mit graviertem Make-it-Real-Schriftzug auf einer Werkbank' },
  ],
  glas: [
    { id: 'praxisschild', src: '/images/references/glas-praxisschild.webp', thumbnail: '/images/references/glas-praxisschild-thumb.webp', title: 'Praxisschild aus Glas', alt: 'Transparentes Glasschild mit Zahn-Symbol und der Gravur Dr. Klein Zahnarztpraxis' },
    { id: 'familienportrait', src: '/images/references/glas-familienportrait.webp', thumbnail: '/images/references/glas-familienportrait-thumb.webp', title: 'Familienporträt in Kristallglas', alt: 'Kristallglas mit graviertem Familienporträt und dem Schriftzug Unsere Familie' },
  ],
  metall: [
    { id: 'bauteil', src: '/images/references/metall-bauteil.webp', thumbnail: '/images/references/metall-bauteil-thumb.webp', title: 'Individuelle Bauteilkennzeichnung', alt: 'Zylindrisches Metallbauteil mit graviertem QR-Code, Seriennummer und technischen Angaben' },
    { id: 'hundemarke', src: '/images/references/metall-hundemarke.webp', thumbnail: '/images/references/metall-hundemarke-thumb.webp', title: 'Hundemarke „Luna“', alt: 'Runde Metallmarke mit graviertem Hundemotiv, dem Namen Luna und einem kleinen Herz' },
  ],
};

export const referencesFor = service => [
  { id: 'cover', src: service.image, thumbnail: `/images/references/${service.id}-cover-thumb.webp`, title: coverTitles[service.id], alt: service.alt },
  ...(additionalReferences[service.id] || []),
];