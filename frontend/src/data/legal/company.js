export const company = {
  brand: 'ManuCreator',
  owner: 'Manuel Bayer',
  street: 'Büttgerwald 16',
  postcode: '47877',
  city: 'Willich',
  country: 'Deutschland',
  email: 'info@manucreator.de',
};

export const legalVersion = '2026-10-04';
export const legalDate = '4. Oktober 2026';
export const address = 'Manuel Bayer · ManuCreator, Büttgerwald 16, 47877 Willich, Deutschland';
export const legalNavigation = [
  { key: 'imprint', path: '/impressum', label: 'Impressum' },
  { key: 'terms', path: '/agb', label: 'AGB' },
  { key: 'privacy', path: '/datenschutz', label: 'Datenschutz' },
  { key: 'withdrawal', path: '/widerruf', label: 'Widerruf' },
];

export const imprint = {
  key: 'imprint',
  title: 'Impressum',
  subtitle: 'Anbieterkennzeichnung nach § 5 DDG',
  note: 'Die angegebenen Unternehmensdaten stammen vom Betreiber. Eine geschäftliche Telefonnummer und gegebenenfalls bereits zugeteilte Identifikationsnummern sind noch zu ergänzen; die abschließende rechtliche Prüfung steht aus.',
  sections: [
    { id: 'anbieter', title: 'Anbieter', paragraphs: ['ManuCreator', 'Inhaber: Manuel Bayer', 'Einzelunternehmer, nicht im Handelsregister eingetragen.', 'Büttgerwald 16\n47877 Willich\nDeutschland'] },
    { id: 'kontakt', title: 'Kontakt', paragraphs: ['E-Mail: info@manucreator.de', 'Für Projektanfragen steht außerdem das unverbindliche Kontaktformular auf der Startseite zur Verfügung.'], links: [{ label: 'E-Mail an ManuCreator', href: 'mailto:info@manucreator.de' }, { label: 'Zum Anfragebereich', href: '/#kontakt' }] },
    { id: 'umsatzsteuer', title: 'Umsatzsteuer', paragraphs: ['ManuCreator nimmt die Kleinunternehmerregelung nach § 19 UStG in Anspruch. Für die darunter fallenden Umsätze wird keine Umsatzsteuer berechnet oder gesondert ausgewiesen.'] },
    { id: 'streitbeilegung', title: 'Verbraucherstreitbeilegung', paragraphs: ['ManuCreator ist weder verpflichtet noch bereit, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.', 'Beschwerden können an die oben genannte E-Mail-Adresse oder Postanschrift gerichtet werden. Der Rechtsweg und gesetzliche Verbraucherrechte bleiben unberührt.'] },
  ],
};